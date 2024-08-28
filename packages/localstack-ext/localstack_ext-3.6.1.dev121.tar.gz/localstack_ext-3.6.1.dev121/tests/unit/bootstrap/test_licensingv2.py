import json
import os

import pytest
from localstack import config
from localstack.constants import VERSION
from localstack.pro.core import config as config_ext
from localstack.pro.core.bootstrap.licensingv2 import (
    ApiKeyCredentials,
    AuthToken,
    CredentialsMissingError,
    DevLocalstackEnvironment,
    LicensedLocalstackEnvironment,
    LicensedPluginLoaderGuard,
    LicenseSignatureMismatchError,
    LicenseV1,
    LicenseV1Client,
    ProductInfo,
    get_credentials_from_environment,
    get_licensed_environment,
)
from plugin import Plugin, PluginDisabled, PluginSpec

TEST_CREDENTIALS_AUTH_TOKEN = "ls-wuku4263-vila-zeji-4925-motaqexi39ff"

# this license has the secret "test_secret" encoded with the credentials set in test_credentials above
# it can't be used to decode the code, but everything else can be tested
test_license_json_auth_token = {
    "license_format": "1",
    "id": "c8378e2e-97b4-43b3-9ee8-f000015a815e",
    "signature": "c83b929057458f1f55432fe4ea6f6778a59f259448b7dc7cee1da5e7e6ae5c12",
    "offline_data": {
        "localstack_version": VERSION,
    },
    "products": [{"name": "localstack-pro", "version": "*.*.*"}],
    "license_type": "Personal (Hobby)",
    "license_status": "ACTIVE",
    "issue_date": "2023-11-01T14:18:25+00:00",
    "expiry_date": "2033-10-29T14:18:25+00:00",
    "license_secret": "TFMxLjA6sJcGTEc4SpmM1/Apuwbmg1lYSV0WmgyP/2cEHAmv/b4=",
    "last_activated": "2023-11-01T14:18:25+00:00",
    "reactivate_after": "2033-10-29T14:18:25+00:00",
}

TEST_CREDENTIALS_API_KEY = "4plthKEMs"

test_license_json_api_key = {
    "license_format": "1",
    "id": "a7acb64c-5aec-4fc5-9c5d-39778417b859",
    "signature": "4e88e9dc8a8d9a197c1ee2f25d88fb8e5c839ccc8162d8a9e3e71b146a685462",
    "offline_data": {
        "localstack_version": VERSION,
    },
    "products": [{"name": "localstack-pro", "version": "*.*.*"}],
    "license_type": "Personal (Hobby)",
    "license_status": "ACTIVE",
    "issue_date": "2023-11-14T13:30:38+00:00",
    "expiry_date": "2033-11-11T13:30:38+00:00",
    "license_secret": "TFMxLjA67Ma1iSmrQB6JTTvMQg2Xbgd0dk7VC3qMMEEaerVKwr4=",
    "last_activated": "2023-11-14T13:30:38+00:00",
    "reactivate_after": "2033-11-11T13:30:38+00:00",
}


class TestLicensedLocalstackEnvironment:
    @pytest.fixture(autouse=True)
    def unset_credentials(self, monkeypatch):
        monkeypatch.setenv("LOCALSTACK_API_KEY", "")
        monkeypatch.setenv("LOCALSTACK_AUTH_TOKEN", "")

    @pytest.fixture(
        params=[
            {
                "LOCALSTACK_API_KEY": "",
                "LOCALSTACK_AUTH_TOKEN": TEST_CREDENTIALS_AUTH_TOKEN,
                "TEST_LICENSE": test_license_json_auth_token,
            },
            {
                "LOCALSTACK_API_KEY": TEST_CREDENTIALS_API_KEY,
                "LOCALSTACK_AUTH_TOKEN": "",
                "TEST_LICENSE": test_license_json_api_key,
            },
        ],
        ids=["auth_token", "api_key"],
    )
    def test_license(self, request, monkeypatch):
        monkeypatch.setenv("LOCALSTACK_API_KEY", request.param["LOCALSTACK_API_KEY"])
        monkeypatch.setenv("LOCALSTACK_AUTH_TOKEN", request.param["LOCALSTACK_AUTH_TOKEN"])
        yield request.param["TEST_LICENSE"]

    @pytest.fixture
    def licensed_environment(self, tmp_path, test_license):
        license_file = tmp_path / "license.json"
        license_file.write_text(json.dumps(test_license, indent=2))

        env = LicensedLocalstackEnvironment(LicenseV1Client())
        env.get_license_file_read_locations = lambda: [str(license_file)]
        return env

    def test_active_cached_offline_license(self, licensed_environment, test_license):
        licensed_environment.activate_license(offline_only=True)
        license_ = licensed_environment.license
        assert license_
        assert isinstance(license_, LicenseV1)
        assert license_.id == test_license["id"]
        assert license_.signature == test_license["signature"]

    def test_license_activation_fails_without_credentials(self, licensed_environment, monkeypatch):
        monkeypatch.setenv("LOCALSTACK_AUTH_TOKEN", "")
        monkeypatch.setenv("LOCALSTACK_API_KEY", "")

        with pytest.raises(CredentialsMissingError):
            licensed_environment.activate_license(offline_only=True)

    def test_decode_license_secret(self, licensed_environment, monkeypatch):
        licensed_environment.activate_license(offline_only=True)
        license_ = licensed_environment.license

        credentials = get_credentials_from_environment()

        assert (
            licensed_environment.client.decode_decryption_key(credentials, license_)
            == b"test_secret"
        )

    def test_active_license_with_different_credentials_does_not_work(
        self, licensed_environment, monkeypatch
    ):
        # check which one's currently set, and set a different one
        if os.environ.get("LOCALSTACK_AUTH_TOKEN"):
            monkeypatch.setenv("LOCALSTACK_AUTH_TOKEN", "ls-xiqiqiwi-6218-xele-wamu-jova401928ad")
        else:
            monkeypatch.setenv("LOCALSTACK_API_KEY", "4plthKEMt")

        with pytest.raises(LicenseSignatureMismatchError):
            licensed_environment.activate_license(offline_only=True)

    @pytest.mark.parametrize(
        ("env_key", "env_value", "expected_class"),
        (
            ("LOCALSTACK_AUTH_TOKEN", "test", DevLocalstackEnvironment),
            ("LOCALSTACK_AUTH_TOKEN", TEST_CREDENTIALS_AUTH_TOKEN, LicensedLocalstackEnvironment),
            ("LOCALSTACK_API_KEY", "test", DevLocalstackEnvironment),
            ("LOCALSTACK_API_KEY", TEST_CREDENTIALS_API_KEY, LicensedLocalstackEnvironment),
        ),
    )
    def test_get_get_licensed_environment(self, monkeypatch, env_key, env_value, expected_class):
        get_licensed_environment.clear()
        monkeypatch.setenv(env_key, env_value)
        assert type(get_licensed_environment()) == expected_class

    def test_save_license(self, licensed_environment, tmp_path, monkeypatch):
        path = tmp_path / "test-cache"
        path.mkdir()

        monkeypatch.setattr(config.dirs, "cache", str(path))
        licensed_environment.activate_license(offline_only=True)

        licensed_environment.save_license()

        actual = json.loads((path / "license.json").read_bytes())
        expected = json.loads(
            licensed_environment.serializer.serialize(licensed_environment.license)
        )
        assert actual == expected

    def test_has_product_license(self, licensed_environment, tmp_path, monkeypatch):
        licensed_environment.activate_license(offline_only=True)
        license_ = licensed_environment.license
        # FIXME: this test shows that it's far too easy to manipulate the licensing environment
        license_.products.append(
            ProductInfo(name="localstack.extensions/enterprise-*", version="*")
        )

        assert not licensed_environment.has_product_license("localstack.extensions/foo")
        assert not licensed_environment.has_product_license("localstack.extensions/enterprise")
        assert not licensed_environment.has_product_license("localstack,extensions/enterprise-foo")
        assert licensed_environment.has_product_license("localstack.extensions/enterprise-foo")
        assert licensed_environment.has_product_license("localstack.extensions/enterprise-")

    def test_product_license_guard(self, licensed_environment, tmp_path, monkeypatch):
        class MockPlugin(Plugin):
            requires_license = None

        plugin_restricted = MockPlugin()
        plugin_restricted.namespace = "localstack.extensions"
        plugin_restricted.name = "enterprise-only"
        plugin_restricted.requires_license = True

        plugin_regular = MockPlugin()
        plugin_regular.namespace = "localstack.extensions"
        plugin_regular.name = "this-is-fine"
        plugin_regular.requires_license = False

        listener = LicensedPluginLoaderGuard(licensed_environment)

        # test before activating
        # this one should be ok
        listener.on_init_after(
            PluginSpec(plugin_regular.namespace, plugin_regular.name, None),
            plugin_regular,
        )

        # this one's disabled
        with pytest.raises(PluginDisabled):
            listener.on_init_after(
                PluginSpec(plugin_restricted.namespace, plugin_restricted.name, None),
                plugin_restricted,
            )

        # now activate the license
        licensed_environment.activate_license(True)
        # this one should be ok
        listener.on_init_after(
            PluginSpec(plugin_regular.namespace, plugin_regular.name, None), plugin_regular
        )
        # this one's still not allowed
        with pytest.raises(PluginDisabled):
            listener.on_init_after(
                PluginSpec(plugin_restricted.namespace, plugin_restricted.name, None),
                plugin_restricted,
            )

        licensed_environment.license.products.append(
            ProductInfo(name="localstack.extensions/enterprise-only", version="*")
        )
        # now it's in the license so should be fine
        listener.on_init_after(
            PluginSpec(plugin_restricted.namespace, plugin_restricted.name, None),
            plugin_restricted,
        )


class TestCredentials:
    def test_get_test_credentials_from_environment_valid(self, monkeypatch):
        # special case for when using "test" as credentials, which should still work and not trigger errors
        monkeypatch.setenv("LOCALSTACK_API_KEY", "")
        monkeypatch.setenv("LOCALSTACK_AUTH_TOKEN", "test")

        credentials = get_credentials_from_environment()
        assert credentials.encoded() == "test"

    def test_get_credentials_from_environment(self, monkeypatch):
        monkeypatch.setenv("LOCALSTACK_AUTH_TOKEN", TEST_CREDENTIALS_AUTH_TOKEN)
        monkeypatch.setenv("LOCALSTACK_API_KEY", "")
        credentials = get_credentials_from_environment()
        assert credentials.encoded() == TEST_CREDENTIALS_AUTH_TOKEN
        assert isinstance(credentials, AuthToken)

        monkeypatch.setenv("LOCALSTACK_AUTH_TOKEN", "")
        monkeypatch.setenv("LOCALSTACK_API_KEY", "6SPj1XCXHx")
        credentials = get_credentials_from_environment()
        assert credentials.encoded() == "6SPj1XCXHx"
        assert isinstance(credentials, ApiKeyCredentials)

    def test_get_credentials_from_environment_with_cache_file(self, tmp_path, monkeypatch):
        # setup environment that looks like the CLI after it's been configured with `localstack auth
        # set-token`
        monkeypatch.setenv("LOCALSTACK_AUTH_TOKEN", "")
        monkeypatch.setenv("LOCALSTACK_API_KEY", "")
        tmp_auth_cache_path = tmp_path / "auth.json"
        monkeypatch.setattr(config_ext, "AUTH_CACHE_PATH", str(tmp_auth_cache_path))
        monkeypatch.setenv("LOCALSTACK_CLI", "1")

        from localstack.pro.core.bootstrap.auth import get_auth_cache

        cache = get_auth_cache()
        cache["LOCALSTACK_AUTH_TOKEN"] = TEST_CREDENTIALS_AUTH_TOKEN
        cache.save()

        credentials = get_credentials_from_environment()
        assert credentials.encoded() == TEST_CREDENTIALS_AUTH_TOKEN
        assert isinstance(credentials, AuthToken)

        cache.clear()
        cache.save()

        assert get_credentials_from_environment() is None

    def test_validate(self):
        # valid credentials
        c = AuthToken(TEST_CREDENTIALS_AUTH_TOKEN)
        assert c.is_syntax_valid()
        assert c.is_checksum_valid()
        assert c.is_valid()

        # valid syntax but invalid signature
        c = AuthToken("ls-xuku4263-vila-zeji-4925-motaqexi39ff")
        assert c.is_syntax_valid()
        assert not c.is_checksum_valid()
        assert not c.is_valid()

        c = AuthToken("test")
        assert not c.is_syntax_valid()
        assert not c.is_checksum_valid()
        assert not c.is_valid()

    def test_string_format(self):
        c = AuthToken(TEST_CREDENTIALS_AUTH_TOKEN)
        assert f"{c}" == "ls-wuku4263-****-****-****-************"
