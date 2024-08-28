import ast
import glob
import importlib
import os
from pathlib import Path
from typing import List

from localstack.pro.core.config import UNPROTECTED_FILES, UNPROTECTED_FOLDERS
from localstack.utils.files import load_file

# find the root path of the localstack.pro.core module
LOCALSTACK_EXT_ROOT_MODULE = importlib.import_module("localstack.pro.core")
ROOT_INIT_FILE_PATH = os.path.dirname(LOCALSTACK_EXT_ROOT_MODULE.__file__)


def assert_allowed(file_path: str, module: List[str]):
    # we only check imports from localstack.pro.core
    if module and len(module) > 3 and module[:3] == ["localstack", "pro", "core"]:
        # imports from unprotected modules are allowed
        if module[1] in UNPROTECTED_FOLDERS:
            return
        # imports from files in the root module (like config.py)
        if Path(ROOT_INIT_FILE_PATH, f"{module[1]}.py").is_file():
            return

        # construct the file path of the init dunder file (if the module results in a directory)
        # f.e. import localstack.pro.core.services.s3 or from localstack.pro.core.services import s3
        module_path = Path(ROOT_INIT_FILE_PATH, *module[1:])
        if module_path.is_dir():
            module_path = module_path / "__init__.py"
        else:
            # f.e. import localstack.pro.core.config
            module_path = Path(ROOT_INIT_FILE_PATH, *module[1:-1], f"{module[-1]}.py")
            if not module_path.is_file():
                if module_path.parent.is_dir():
                    # f.e. from localstack.pro.core.runtime.plugin import PlatformPlugin
                    module_path = module_path.parent / "__init__.py"
                else:
                    module_path = module_path.parent.parent / f"{module_path.parent.name}.py"
        if not module_path.is_file():
            return

        # imports of other unprotected files are allowed
        if any(
            str(module_path).endswith(unprotected_file) for unprotected_file in UNPROTECTED_FILES
        ):
            return

        # otherwise this import is most likely an import of encrypted code by unencrypted code
        raise Exception(f"{file_path}: Invalid import of a protected module ({module}).")


def enforce_no_protected_imports(file_path: str) -> None:
    root = ast.parse(load_file(file_path))

    for node in ast.iter_child_nodes(root):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue

        if isinstance(node, ast.ImportFrom):
            if node.module:
                for name in node.names:
                    # check "from x.y import z" statements
                    assert_allowed(file_path, node.module.split(".") + [name.name])

                    # check relative imports
                    if hasattr(node, "level") and node.level > 0:
                        module = file_path.split("localstack-ext/")[-1].replace("/", ".").split(".")
                        module = module[: -(node.level + 1)] + node.module.split(".")
                        assert_allowed(file_path, module + [name.name])

        for name in node.names:
            # check "import x.y.z" statements
            assert_allowed(file_path, name.name.split("."))


def test_no_restricted_imports_from_unprotected_folders():
    """
    Check all import statements within `bootstrap/**.py` and `packages/**.py` files using the `ast` module, and
    assert that no restricted modules are being imported.
    """
    for ext_module_name in UNPROTECTED_FOLDERS:
        module = importlib.import_module(f"localstack.pro.core.{ext_module_name}")
        root_dir = os.path.dirname(module.__file__)
        for folder_name, _, file_names in os.walk(root_dir):
            for file_name in file_names:
                if not file_name.endswith(".py"):
                    continue

                file_path = os.path.join(folder_name, file_name)
                enforce_no_protected_imports(file_path)


def test_no_restricted_imports_from_unprotected_files():
    # find all files which are unprotected
    for f in glob.glob(os.path.join(ROOT_INIT_FILE_PATH, "**/*.py"), recursive=True):
        if any(f.endswith(unprotected_file) for unprotected_file in UNPROTECTED_FILES):
            enforce_no_protected_imports(f)
