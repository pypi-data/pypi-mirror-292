import builtins
import hashlib
import importlib
import os
import random
import sys
import threading
import traceback
import zipfile
from copy import deepcopy
from typing import Any, Dict, Hashable, Optional, Set

import localstack.pro.core.persistence.pods.api.manager
import pytest
from localstack.pro.core.bootstrap import pods_client
from localstack.pro.core.bootstrap.pods import constants as cloud_pods_constants
from localstack.pro.core.bootstrap.pods_client import is_compatible_version
from localstack.pro.core.constants import API_STATES_DIRECTORY
from localstack.pro.core.persistence.models import Revision
from localstack.pro.core.persistence.pods.api.manager import get_pods_manager
from localstack.pro.core.persistence.pods.merge.state_merge import merge_3way, merge_3way_sets
from localstack.state import pickle
from localstack.testing.config import TEST_AWS_ACCOUNT_ID
from localstack.utils.files import load_file, mkdir, new_tmp_dir, rm_rf
from localstack.utils.strings import short_uid

SERVICE_NAMES_SAMPLE = ["s3", "sqs", "qldb", "cognito"]
REGIONS_SAMPLE = ["eu-west-1", "eu-west-2", "eu-central-1", "na-east-1"]


@pytest.fixture()
def set_pods_environ(monkeypatch):
    pod_dir = new_tmp_dir()
    monkeypatch.setenv("POD_DIR", pod_dir)
    yield

    rm_rf(pod_dir)


@pytest.fixture()
def state_file_factory(tmp_path):
    """
    Factory that can be used to create state files with randomized content
    in a temporary path.
    """

    class Factory:
        state_file_paths = []

        @staticmethod
        def create_state_file(service: str, region: str, content: bytes = None):
            from localstack.services.dynamodb.models import DynamoDBStore

            dummy_region = DynamoDBStore()

            file_name = f"state_file-{short_uid()}"
            path = os.path.join(tmp_path, API_STATES_DIRECTORY, service, region)
            mkdir(path)
            file_path = os.path.join(path, file_name)
            with open(file_path, "wb") as fp:
                if content:
                    fp.write(content)
                else:
                    fp.write(pickle.dumps(dummy_region))
            Factory.state_file_paths.append(file_path)
            return file_path

    yield Factory


@pytest.fixture()
def state_file_reference_factory():
    """
    Factory that can be used to create *fake" references, i.e.
    factory does not actually create any physical files.
    """

    class Factory:
        state_file_hashes = []

        @staticmethod
        def create_state_file_ref(file_path: str = None):
            from localstack.pro.core.persistence.models import StateFileRef
            from localstack.pro.core.persistence.utils.hash_utils import random_hash

            service = random.choice(SERVICE_NAMES_SAMPLE)
            region = random.choice(REGIONS_SAMPLE)
            if file_path:
                rel_path = file_path
                with open(file_path, "rb") as fp:
                    hash_ref = hashlib.sha1(fp.read()).hexdigest()
                    fp.seek(0, os.SEEK_END)
                    size = fp.tell()
            else:
                hash_ref = random_hash()
                size = random.randint(0, 1024)
                rel_path = os.path.join(service, region)
            state_file = StateFileRef(
                hash_ref=hash_ref,
                rel_path=rel_path,
                file_name=f"state_file-{short_uid()}",
                size=size,
                service=service,
                region=region,
                account_id=TEST_AWS_ACCOUNT_ID,
            )
            Factory.state_file_hashes.append(state_file.hash_ref)
            return state_file

    yield Factory


def _assert_init_filesystem(manager):
    import localstack.pro.core.bootstrap.pods.constants as cloudpods_constants

    pod_dir = manager.pods_fs_ops.config_context.pod_root_dir
    objects_dir = os.path.join(pod_dir, cloudpods_constants.OBJ_STORE_DIR)

    # check basic file system
    assert os.path.isdir(pod_dir)
    assert os.path.isdir(objects_dir)


def test_name_and_versions():
    from localstack.pro.core.cli.cloud_pods import get_pod_name_and_version

    assert get_pod_name_and_version(pod_name="my-pod:1") == ("my-pod", 1)
    assert get_pod_name_and_version(pod_name="my-pod") == ("my-pod", None)
    assert get_pod_name_and_version(pod_name="my-pod:strong:1") == ("my-pod:strong", 1)
    assert get_pod_name_and_version(pod_name="ci:my-pod:run1") == ("ci:my-pod:run1", None)
    assert get_pod_name_and_version(pod_name="ci:my-pod:run1:3") == ("ci:my-pod:run1", 3)


# todo: patch POD_DIR for tests
class TestCloudPods:
    def test_init_works(self):
        """
        Create filesystem (with TMP_DIR/POD_DIR/.cpvcs as root):
        objects/rev/{rev0_key}
        objects/ver/{ver0_key}
        versions/
        HEAD
        VER_LOG
        MAX_VER
        KNOWN_VER

        Test checks whether filesystem is correctly created and that the initial V0 and its initial active revision
        are created and correctly referenced
        """
        pod_name = f"pod-{short_uid()}"
        manager = localstack.pro.core.persistence.pods.api.manager.get_pods_manager(
            pod_name=pod_name
        )
        manager.pods_fs_ops.init(pod_name=pod_name)
        _assert_init_filesystem(manager=manager)

    # models tests
    def test_models_instantiation_and_methods_work(self):
        from localstack.pro.core.persistence.models import Revision, StateFileRef, Version
        from localstack.pro.core.persistence.utils.hash_utils import random_hash

        state_files = [
            StateFileRef(
                hash_ref=random_hash(),
                rel_path="",
                file_name=random_hash(),
                size=random.randint(15, 500),
                service=random.choice(SERVICE_NAMES_SAMPLE),
                region=random.choice(REGIONS_SAMPLE),
                account_id=TEST_AWS_ACCOUNT_ID,
            )
            for _ in range(10)
        ]

        revision = Revision(
            hash_ref=random_hash(),
            state_files=state_files[:5],
            parent_ptr="",
            creator="",
            rid=short_uid(),
            revision_number=0,
        )
        version = Version(
            hash_ref=random_hash(),
            state_files=state_files[5:],
            parent_ptr="",
            creator="",
            comment="Test Version",
            outgoing_revision_ptrs=set(),
            incoming_revision_ptr="",
            version_number=0,
        )
        version.revisions.append(revision)
        rev_state_files_str = revision.state_files_info()
        ver_state_files_str = version.state_files_info()

        assert rev_state_files_str == "\n".join(
            map(lambda state_file: str(state_file), state_files[:5])
        )
        assert ver_state_files_str == "\n".join(
            map(lambda state_file: str(state_file), state_files[5:])
        )

    # helper/seek/lookup method tests
    # todo: also test whether Files are correctly written to (symlinks)
    def test_empty_push_updates_graph_correctly(self):
        pod_name = f"pod-{short_uid()}"
        manager = get_pods_manager(pod_name=pod_name)
        manager.init()
        max_ver = manager.pods_fs_ops.get_max_version()
        known_versions = manager.pods_fs_ops.list_versions()
        # no finalized versions prior to push yet
        assert not known_versions
        assert not max_ver

        # check whether subsequent pushes update head, max version and known versions properly
        for push_attempt in range(1, 5):
            manager.pods_fs_ops.push(version=push_attempt)
            # this is the version not yet finalized (+1 on the max attempt)
            max_ver = manager.pods_fs_ops.get_max_version()
            known_versions = manager.pods_fs_ops.list_versions()
            # Versioning starts from 0
            assert len(known_versions) == push_attempt
            # test whether references aren't broken on push
            assert max_ver.version_number == push_attempt + 1 == known_versions[-1].version_number

    def test_empty_commit_expands_active_revision_correctly(self):
        pod_name = f"pod-{short_uid()}"
        manager = get_pods_manager(pod_name=pod_name)
        manager.pods_fs_ops.init()
        # r0 (new)

        # head points to the root of the active revision path and on init the expansion point should be the root
        expansion_point, head = manager.pods_fs_ops.get_latest_revision_of_active_version()

        assert expansion_point.parent_ptr == cloud_pods_constants.NIL_PTR

        # first commit works differently than subsequent ones
        manager.pods_fs_ops.commit()
        # r0 (prev) -> r1 (new)
        new_expansion_point, head = manager.pods_fs_ops.get_latest_revision_of_active_version()
        # check whether expansion point has updated and correctly references
        assert new_expansion_point.parent_ptr != cloud_pods_constants.NIL_PTR
        updated_prev_expansion_point = head.get_revision(new_expansion_point.parent_ptr)

        # since hash updates of the root in the active revision path we check by revision number
        assert (
            updated_prev_expansion_point.revision_number
            == expansion_point.revision_number
            == Revision.DEFAULT_INITIAL_REVISION_NUMBER
        )

        # test whether commit is created correctly
        assoc_commit = updated_prev_expansion_point.assoc_commit
        assert assoc_commit.tail_ptr == updated_prev_expansion_point.hash_ref
        assert assoc_commit.head_ptr == new_expansion_point.hash_ref

        manager.pods_fs_ops.commit()
        # r0 (prev parent) commit-> r1(prev) commit-> r2 (new)
        new_expansion_point, head = manager.pods_fs_ops.get_latest_revision_of_active_version()
        updated_prev_expansion_point = head.get_revision(new_expansion_point.parent_ptr)
        updated_prev_expansion_point_parent = head.get_revision(
            updated_prev_expansion_point.parent_ptr
        )
        # test whether changed reference is updated in the commit of the parent
        assert (
            updated_prev_expansion_point_parent.assoc_commit.head_ptr
            == updated_prev_expansion_point.hash_ref
        )
        assoc_commit = updated_prev_expansion_point.assoc_commit
        assert assoc_commit.tail_ptr == updated_prev_expansion_point.hash_ref
        assert assoc_commit.head_ptr == new_expansion_point.hash_ref

    # state file tests
    # note: doesn't test whether state files are correctly copied into the storage, only that the references are correctly set
    def test_commit_and_push_reference_state_files_correctly(self, state_file_reference_factory):
        from localstack.pro.core.persistence.models import StateFileRef

        def _add_files_to_expansion_point(amount: int):
            for _ in range(amount):
                pods_api._add_state_file_to_expansion_point(
                    state_file_reference_factory.create_state_file_ref()
                )

        def _extract_keys_from_state_file_ref(state_files: Set[StateFileRef]):
            return set(map(lambda sf: sf.hash_ref, state_files))

        def _assert_state_file_references(
            state_files: Set[StateFileRef], expected_size: int, idx_factory: int
        ):
            assert len(state_files) == expected_size
            state_files_keys = _extract_keys_from_state_file_ref(state_files)
            assert state_files_keys == set(
                state_file_reference_factory.state_file_hashes[
                    idx_factory : expected_size + idx_factory
                ]
            )

        pod_name = f"pod-{short_uid()}"
        manager = get_pods_manager(pod_name=pod_name)
        pods_api = manager.pods_fs_ops
        pods_api.init(pod_name=pod_name)

        expansion_point, _ = pods_api.get_latest_revision_of_active_version()
        # No state files should be associated to the expansion point on startup
        assert not expansion_point.state_files
        # add random files (check factory fixture or something..)
        _add_files_to_expansion_point(amount=3)
        # test whether they exist?
        expansion_point, _ = pods_api.get_latest_revision_of_active_version()
        expansion_point_state_files = expansion_point.state_files
        _assert_state_file_references(expansion_point_state_files, expected_size=3, idx_factory=0)
        pods_api.commit()
        # check whether new expansion point doesn't reference any state files
        expansion_point, version = pods_api.get_latest_revision_of_active_version()
        assert not expansion_point.state_files
        prev_expansion_point = version.get_revision(expansion_point.parent_ptr)

        # check whether previous extension point still references the same state files
        expansion_point_state_files = prev_expansion_point.state_files
        _assert_state_file_references(expansion_point_state_files, expected_size=3, idx_factory=0)

        # add new files to expansion point before pushing
        _add_files_to_expansion_point(amount=3)
        expansion_point, _ = pods_api.get_latest_revision_of_active_version()
        pods_api.push(version=1)
        # check whether new version references the same state files as the pushed expansion point
        expansion_point, head = pods_api.get_latest_revision_of_active_version()
        # check whether previous version (v0) does not
        previous_version = manager.pods_fs_ops.object_storage.get_in_progress_version()
        assert not previous_version.state_files

        # add more random files
        _add_files_to_expansion_point(amount=3)
        # check whether expansion point of v1 can store state file references
        expansion_point, _ = pods_api.get_latest_revision_of_active_version()
        _assert_state_file_references(expansion_point.state_files, expected_size=3, idx_factory=6)
        # push and check head again
        pods_api.push(version=2)

    def test_state_files_copied_and_referenced_correctly(self, state_file_factory):
        def _assert_copies_exists_with_correct_content(copy_orig_pairs: Dict[str, str]):
            for copy_key, orig_path in copy_orig_pairs.items():
                with open(orig_path, "rb") as fp_orig, open(
                    pods_api._get_state_file_path(copy_key), "rb"
                ) as fp_copy:
                    hash_orig = hashlib.sha1(fp_orig.read()).hexdigest()
                    hash_copy = hashlib.sha1(fp_copy.read()).hexdigest()
                    assert hash_orig == hash_copy == copy_key

        pod_name = f"pod-{short_uid()}"
        manager = get_pods_manager(pod_name=pod_name)
        pods_api = manager.pods_fs_ops

        pods_api.init()
        # create a couple of state files with random content
        state_file_paths = [
            state_file_factory.create_state_file(
                region=random.choice(REGIONS_SAMPLE), service=random.choice(SERVICE_NAMES_SAMPLE)
            )
            for _ in range(10)
        ]
        copy_orig = {}
        for state_file_path in state_file_paths:
            path, file_name = os.path.split(state_file_path)
            key = pods_api.create_state_file_from_fs(
                object=load_file(state_file_path, mode="rb"),
                file_name=file_name,
                account_id=TEST_AWS_ACCOUNT_ID,
                region=random.choice(REGIONS_SAMPLE),
                service=random.choice(SERVICE_NAMES_SAMPLE),
                root=API_STATES_DIRECTORY,
            )
            copy_orig[key] = state_file_path

        # check whether files have been correctly copied to the object storage
        _assert_copies_exists_with_correct_content(copy_orig)

        # test whether push correctly creates a state and meta archive for head
        pods_api.push()
        _, head = pods_api.get_latest_revision_of_active_version()

        head_version_state_archive = pods_api.config_context.get_pod_version_archive_path(version=1)
        assert os.path.isfile(head_version_state_archive)

    def test_writing_multiple_congruent_sf_to_same_revision_overwrites_previous(self):
        # congruence between two sf is defined as having the same rel_path, file_name, service and region
        from localstack.pro.core.persistence.models import StateFileRef
        from localstack.pro.core.persistence.utils.hash_utils import random_hash

        pod_name = f"pod-{short_uid()}"
        manager = get_pods_manager(pod_name=pod_name)
        pods_api = manager.pods_fs_ops

        pods_api.init()
        # create two references that are congruent (i.e. different only in size and content/hash)
        sf1 = StateFileRef(
            hash_ref=random_hash(),
            size=42,
            rel_path="local/stack",
            file_name="localstack",
            service="LocalStack as a Service",
            region="Localhost",
            account_id=TEST_AWS_ACCOUNT_ID,
        )
        sf2 = StateFileRef(
            hash_ref=random_hash(),
            size=21,
            rel_path="local/stack",
            file_name="localstack",
            service="LocalStack as a Service",
            region="Localhost",
            account_id=TEST_AWS_ACCOUNT_ID,
        )

        pods_api._add_state_file_to_expansion_point(sf1)
        # check whether sf1 is correctly referenced
        expansion_point, _ = pods_api.get_latest_revision_of_active_version()
        # there should be exactly one state file in the expansion point
        assert len(expansion_point.state_files) == 1
        # which should be equal to sf1 (note: pop doesn't mutate since we aren't writing the result back to the store)
        assert sf1 == expansion_point.state_files.pop()

        # now adding sf2 should overwrite sf1
        pods_api._add_state_file_to_expansion_point(sf2)
        expansion_point, _ = pods_api.get_latest_revision_of_active_version()
        # since sf1 got overwritten there should only be 1 state file
        assert len(expansion_point.state_files) == 1
        # which should be equal to sf2
        assert sf2 == expansion_point.state_files.pop()

    def test_get_max_version_no_returns_correct_version_number(self, state_file_factory):
        pod_name = f"pod-{short_uid()}"
        manager = get_pods_manager(pod_name=pod_name)
        pods_api = manager.pods_fs_ops

        pods_api.init()
        assert not pods_api.get_max_version_no()
        pods_api.push(version=1)
        assert pods_api.get_max_version_no() == 1
        _, active_version = pods_api.get_latest_revision_of_active_version()
        assert active_version.version_number == 2
        pods_api.commit()
        pods_api.commit()
        pods_api.commit()
        # commits should not increase the version number
        assert pods_api.get_max_version_no() == 1
        pods_api.push(version=2)
        pods_api.commit()
        pods_api.commit()
        pods_api.push(version=3)
        pods_api.commit()
        pods_api.push(version=4)
        pods_api.commit()
        # three pushes should increase the max version by exactly 3, even if there have been some commits before
        assert pods_api.get_max_version_no() == 4
        pods_api.set_active_version(1)
        # setting active revision should not change the version number
        assert pods_api.get_max_version_no() == 4

    def test_pushing_versions_creates_state_zip(self):
        pod_name = f"pod-{short_uid()}"
        manager = get_pods_manager(pod_name=pod_name)
        pods_api = manager.pods_fs_ops

        pods_api.init()

        no_versions = 3
        for i in range(no_versions):
            pods_api.push(version=i + 1)
            path = pods_api.config_context.get_pod_version_archive_path(version=i + 1)
            assert os.path.isfile(path)

    def test_create_versions_archive_creates_correct_zip(self, state_file_factory):
        pod_name = f"pod-{short_uid()}"
        manager = get_pods_manager(pod_name=pod_name)
        pods_api = manager.pods_fs_ops

        pods_api.init()

        sf_path_1 = state_file_factory.create_state_file(
            service="Sample-Service1", region="Sample region1"
        )
        sf_path_2 = state_file_factory.create_state_file(
            service="Sample-Service2", region="Sample region2"
        )

        key_1 = pods_api.create_state_file_from_fs(
            object=load_file(sf_path_1, mode="rb"),
            file_name=os.path.basename(sf_path_1),
            account_id=TEST_AWS_ACCOUNT_ID,
            service="Sample-Service1",
            region="Sample region 1",
            root=API_STATES_DIRECTORY,
        )
        key_2 = pods_api.create_state_file_from_fs(
            object=load_file(sf_path_1, mode="rb"),
            file_name=os.path.basename(sf_path_2),
            account_id=TEST_AWS_ACCOUNT_ID,
            service="Sample-Service2",
            region="Sample region 2",
            root=API_STATES_DIRECTORY,
        )

        pods_api.commit()
        pods_api.commit()
        pods_api.push(version=1)
        pods_api.commit()
        pods_api.commit()

        archive_path = pods_api.config_context.get_pod_version_archive_path(version=1)

        with zipfile.ZipFile(archive_path, "r") as archive:
            filelist = list(map(lambda file: file.filename, archive.filelist))
            assert os.path.join(f"objects/{key_1}") in filelist
            assert os.path.join(f"objects/{key_2}") in filelist

    def test_listing_locally_available_pods(self):
        pod_names = [f"p-{short_uid()}" for _ in range(10)]

        for pod_name in pod_names:
            manager = get_pods_manager(pod_name=pod_name)
            manager.pods_fs_ops.init(pod_name=pod_name)

        manager = get_pods_manager("")
        available_pods = manager.pods_fs_ops.list_locally_available_pods()
        for pod_name in pod_names:
            assert pod_name in available_pods

    def test_committing_and_pushing_correctly_updates_revision_in_obj_store(
        self, state_file_factory
    ):
        pod_name = f"pod-{short_uid()}"
        manager = get_pods_manager(pod_name=pod_name)
        pods_api = manager.pods_fs_ops
        pods_api.init()

        expansion_point, _ = pods_api.get_latest_revision_of_active_version()

        key_before_commit = expansion_point.hash_ref

        # add a file so there is a hash to compute
        sf_path_1 = state_file_factory.create_state_file(
            service="Sample-Service1", region="Sample region1"
        )
        pods_api.create_state_file_from_fs(
            object=load_file(sf_path_1, mode="rb"),
            file_name=os.path.basename(sf_path_1),
            account_id=TEST_AWS_ACCOUNT_ID,
            service="Sample-Service1",
            region="Sample region 1",
            root=API_STATES_DIRECTORY,
        )

        pods_api.commit()

        expansion_point, version = pods_api.get_latest_revision_of_active_version()

        # since we've just committed the previous expansion point is the parent of the current expansion point
        prev_expansion_point = version.get_revision(expansion_point.parent_ptr)

        # since the revision has been committed the hash should have been updated according to the state files it associated
        assert prev_expansion_point.hash_ref != key_before_commit

        sf_path_2 = state_file_factory.create_state_file(
            service="Sample-Service2", region="Sample region2"
        )
        pods_api.create_state_file_from_fs(
            object=load_file(sf_path_2, mode="rb"),
            file_name=os.path.basename(sf_path_2),
            account_id=TEST_AWS_ACCOUNT_ID,
            service="Sample-Service2",
            region="Sample region 2",
            root=API_STATES_DIRECTORY,
        )

        pods_api.commit()

        # retrieve updated version/revision
        expansion_point, version = pods_api.get_latest_revision_of_active_version()

        parent_rev = version.get_revision(expansion_point.parent_ptr).parent_ptr
        prev_prev_expansion_point = version.get_revision(parent_rev)

        # however, once committed the hash reference is immutable
        assert prev_prev_expansion_point.hash_ref == prev_expansion_point.hash_ref

        # pushing should now create a new version, where the incoming revision commit points to it
        pods_api.push(version=1)

        _, version_2 = pods_api.get_latest_revision_of_active_version()
        # check that version 2 is initialized correctly
        assert version_2.version_number == 2
        assert version_2.incoming_revision_ptr is None


class Test3WayMergeBaseScenarios:
    _StateType = Dict[str, str]

    @staticmethod
    def assert_merge_scenario(anc: _StateType, cur: _StateType, inj: _StateType, res: _StateType):
        cur_res = deepcopy(cur)
        merge_3way(cur_res, inj, anc)
        assert cur_res == res

    @staticmethod
    def theta() -> Dict[str, str]:
        return {"theta_k1": "theta_v1", "theta_k2": "theta_v2"}

    @staticmethod
    def psi() -> Dict[str, str]:
        return {"psi_k1": "psi_v1", "psi_k2": "psi_v2"}

    def test_empty_inject(self):
        self.assert_merge_scenario(anc={}, cur={**self.theta()}, inj={}, res={**self.theta()})

    def test_inject_addition(self):
        self.assert_merge_scenario(
            anc={}, cur={"a": "x"}, inj={**self.theta()}, res={"a": "x", **self.theta()}
        )

    def test_inject_update(self):
        self.assert_merge_scenario(
            anc={},
            cur={"a": "x", **self.theta()},
            inj={"a": "y", **self.theta()},
            res={"a": "y", **self.theta()},
        )

    def test_strict_inject_update(self):
        self.assert_merge_scenario(
            anc={"a": "x", **self.theta()},
            cur={"a": "x", **self.theta()},
            inj={"a": "y", **self.theta()},
            res={"a": "y", **self.theta()},
        )

    def test_strict_head_update(self):
        self.assert_merge_scenario(
            anc={"a": "y", **self.theta()},
            cur={"a": "x", **self.theta()},
            inj={"a": "y", **self.theta()},
            res={"a": "x", **self.theta()},
        )

    def test_inject_deletion(self):
        self.assert_merge_scenario(
            anc={"a": "x", **self.theta()},
            cur={"a": "x", **self.theta(), **self.psi()},
            inj={**self.theta()},
            res={**self.theta(), **self.psi()},
        )

    def test_inject_deletion_on_update(self):
        self.assert_merge_scenario(
            anc={"a": "x", **self.theta()},
            cur={"a": "y", **self.theta(), **self.psi()},
            inj={**self.theta()},
            res={**self.theta(), **self.psi()},
        )

    def test_basic_merge_sets(self):
        # Base cases, primitives.

        # Unchanged.
        cur = {1, "a"}
        merge_3way_sets(cur, set(), None)
        assert cur == {1, "a"}

        cur = {1, "a"}
        merge_3way_sets(cur, set(), set())
        assert cur == {1, "a"}

        # Addition.
        cur = {1, "a"}
        merge_3way_sets(cur, {"b"}, None)
        assert cur == {1, "a", "b"}

        cur = {1, "a"}
        merge_3way_sets(cur, {"b"}, {"c"})
        assert cur == {1, "a", "b"}

        # Deletion.
        cur = {1, "a"}
        merge_3way_sets(cur, {"b"}, {"a"})
        assert cur == {1, "b"}

        cur = {1, "a"}
        merge_3way_sets(cur, {"b"}, {1, "a"})
        assert cur == {"b"}

        class _TestClass:
            def __init__(self, hashable_part: Hashable, other: Optional[Any]):
                self.hashable_part: Hashable = hashable_part
                self.other: Optional[Any] = other

            def __hash__(self):
                return hash(self.hashable_part)

            def __eq__(self, other):
                # For testing/assertion purposes.
                return self.hashable_part == other.hashable_part and self.other == other.other

            def __repr__(self):
                return f"{hash(self.hashable_part)}: {self.hashable_part}, {self.other}"

            def __str__(self):
                return self.__repr__()

        # Hashable cases.

        # Unchanged.
        cur = {_TestClass(1, {"a": "A"})}
        merge_3way_sets(cur, set(), None)
        assert cur == {_TestClass(1, {"a": "A"})}

        cur = {_TestClass(1, {"a": "A"})}
        merge_3way_sets(cur, set(), set())
        assert cur == {_TestClass(1, {"a": "A"})}

        # Addition.

        # Addition in non hashable part.
        cur = {_TestClass(1, {"a": "A"})}
        merge_3way_sets(cur, {_TestClass(1, {"a": "A", "b": "B"})}, None)
        assert cur == {_TestClass(1, {"a": "A", "b": "B"})}

        cur = {_TestClass(1, {"a": "A"}), _TestClass(2, {"x": "X"})}
        merge_3way_sets(cur, {_TestClass(1, {"b": "B"}), _TestClass(2, {"x": "X", "y": "Y"})}, None)
        assert cur == {_TestClass(1, {"a": "A", "b": "B"}), _TestClass(2, {"x": "X", "y": "Y"})}

        # Addition in hashable part.
        cur = {_TestClass(1, {"a": "A"}), _TestClass(2, {"x": "X"})}
        merge_3way_sets(cur, {_TestClass(1, {"b": "B"}), _TestClass(3, {"y": "Y"})}, None)
        assert cur == {
            _TestClass(1, {"a": "A", "b": "B"}),
            _TestClass(2, {"x": "X"}),
            _TestClass(3, {"y": "Y"}),
        }

        # Deletion.

        # Deletion in non hashable part.
        cur = {_TestClass(1, {"a": "A"})}
        merge_3way_sets(cur, {_TestClass(1, {"b": "B"})}, {_TestClass(1, {"a": "A", "c": "C"})})
        assert cur == {_TestClass(1, {"b": "B"})}

        # Deletion in hashable part.
        cur = {_TestClass(1, {"a": "A"}), _TestClass(2, {"x": "X"})}
        merge_3way_sets(cur, {_TestClass(3, {"y": "Y"})}, cur)
        assert cur == {_TestClass(3, {"y": "Y"})}


class TestCloudPodsCli:
    def test_assert_import_no_runtime_modules(self, monkeypatch):
        """
        Run a test with runtime imports, to assert that runtime dependencies are not
        imported from the pods CLI commands.
        """

        removed_modules = {}
        restricted_modules = ["hypercorn", "flask", "moto", "localstack.pro.core.persistence"]
        try:
            thread_id = threading.current_thread().ident

            for key in set(sys.modules):
                if key in {"warnings", "builtins", "sys"}:
                    continue
                if key.startswith("_"):
                    continue
                removed_modules[key] = sys.modules.pop(key)

            def _import_(name, *args, **kwargs):
                result = import_orig(name, *args, **kwargs)
                if threading.current_thread().ident == thread_id:
                    # keep track of the module, if it has been imported by the current thread
                    tl_module = result.__name__.split(".")[0]
                    imported_modules.add(tl_module)
                    # print a stack trace for debugging if a restricted module is imported
                    if tl_module in restricted_modules:
                        print("".join(traceback.format_stack()))  # print() on purpose here
                return result

            imported_modules = set()
            import_orig = builtins.__import__
            monkeypatch.setattr(builtins, "__import__", _import_)

            # trigger the internal import mechanism via importlib
            importlib.import_module(pods_client.__name__)

            # Assert that certain runtime dependencies are not included in the loaded dependencies.
            # Note: we may need to extend/maintain this list of modules over time.
            assert "localstack" in imported_modules or imported_modules.issuperset(
                ("localstack", "pro", "core")
            )
            for module in restricted_modules:
                assert module not in imported_modules

        finally:
            sys.modules.update(removed_modules)


def test_compatible_versions():
    assert not is_compatible_version("3.0.0", "3.0.1.dev1234")
    assert not is_compatible_version("3.0.0", "3.0.1")
    assert is_compatible_version("3.0.1.dev2345", "3.0.1.dev1234")
    assert is_compatible_version("3.0.1.dev2345", "3.0.1")
