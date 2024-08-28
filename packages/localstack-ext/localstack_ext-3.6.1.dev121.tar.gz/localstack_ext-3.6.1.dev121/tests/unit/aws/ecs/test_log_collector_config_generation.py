import pytest
from localstack.pro.core.services.ecs.log_collectors.config_generator import (
    ConfigGenerator,
    IncludePosition,
)
from localstack.pro.core.services.ecs.log_collectors.fluent_bit_config_generator import (
    FluentBitConfigGenerator,
)
from localstack.pro.core.services.ecs.log_collectors.fluentd_config_generator import (
    FluentdConfigGenerator,
)
from localstack.testing.pytest import markers


class TestLogCollectorConfigGeneration:
    @pytest.fixture
    def generic_fluentd_config_generator(self) -> FluentdConfigGenerator:
        generator = FluentdConfigGenerator()
        self.build_default_generic_config(generator)
        return generator

    @pytest.fixture
    def generic_fluent_bit_config_generator(self) -> FluentBitConfigGenerator:
        generator = FluentBitConfigGenerator()
        self.build_default_generic_config(generator)
        return generator

    @staticmethod
    def build_default_generic_config(generator):
        generator.add_input("forward", "tag", {"Listen": "127.0.0.1", "Port": "24224"})
        generator.add_include_filter("*failure*", "log", "*")
        generator.add_exclude_filter("*success*", "log", "*")
        generator.add_field_to_record("cluster", "default", "*")
        generator.add_external_config("/etc/head_file.conf", IncludePosition.HEAD_OF_FILE)
        generator.add_output(
            "cloudwatch", "*", {"log_group_name": "my-group", "region": "us-west-2"}
        )

    @markers.aws.only_localstack
    def test_fluentd_generator_works_as_expected_with_generic_config(
        self, generic_fluentd_config_generator
    ):
        assert """
@include /etc/head_file.conf
<source>
    @type forward
    tag tag
    Listen 127.0.0.1
    Port 24224
</source>
<filter *>
    @type grep
    <regexp>
        key log
        pattern *failure*
    </regexp>
</filter>
<filter *>
    @type grep
    <exclude>
        key log
        pattern *success*
    </exclude>
</filter>
<filter *>
    @type record_transformer
    <record>
        cluster default
    </record>
</filter>
<match *>
    @type cloudwatch
    log_group_name my-group
    region us-west-2
</match>""" == generic_fluentd_config_generator.build_config()

    @markers.aws.only_localstack
    def test_fluent_bit_generator_works_as_expected_with_generic_config(
        self, generic_fluent_bit_config_generator
    ):
        assert """
@INCLUDE /etc/head_file.conf
[INPUT]
    Name forward
    Tag tag
    Listen 127.0.0.1
    Port 24224
[FILTER]
    Name grep
    Match *
    Regex log *failure*
[FILTER]
    Name grep
    Match *
    Exclude log *success*
[FILTER]
    Name record_modifier
    Match *
    Record cluster default
[OUTPUT]
    Name cloudwatch
    Match *
    log_group_name my-group
    region us-west-2""" == generic_fluent_bit_config_generator.build_config()

    @markers.aws.only_localstack
    def test_fluentd_config_generation_with_system_settings(self, generic_fluentd_config_generator):
        generic_fluentd_config_generator.add_system_settings("error")
        assert """
@include /etc/head_file.conf
<system>
    log_level error
</system>
<source>
    @type forward
    tag tag
    Listen 127.0.0.1
    Port 24224
</source>
<filter *>
    @type grep
    <regexp>
        key log
        pattern *failure*
    </regexp>
</filter>
<filter *>
    @type grep
    <exclude>
        key log
        pattern *success*
    </exclude>
</filter>
<filter *>
    @type record_transformer
    <record>
        cluster default
    </record>
</filter>
<match *>
    @type cloudwatch
    log_group_name my-group
    region us-west-2
</match>""" == generic_fluentd_config_generator.build_config()

    @markers.aws.only_localstack
    def test_fluent_bit_config_generation_with_system_settings(
        self, generic_fluent_bit_config_generator
    ):
        generic_fluent_bit_config_generator.add_service_settings("debug")
        assert """
@INCLUDE /etc/head_file.conf
[SERVICE]
    Log_Level debug
[INPUT]
    Name forward
    Tag tag
    Listen 127.0.0.1
    Port 24224
[FILTER]
    Name grep
    Match *
    Regex log *failure*
[FILTER]
    Name grep
    Match *
    Exclude log *success*
[FILTER]
    Name record_modifier
    Match *
    Record cluster default
[OUTPUT]
    Name cloudwatch
    Match *
    log_group_name my-group
    region us-west-2""" == generic_fluent_bit_config_generator.build_config()

    @markers.aws.only_localstack
    def test_generator_raises_exception_if_template_is_not_set(self):
        generator = ConfigGenerator()
        with pytest.raises(ValueError) as exc:
            generator.build_config()
        assert "Template not set" == str(exc.value)
