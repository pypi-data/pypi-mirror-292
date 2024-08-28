from localstack.pro.core.services.mwaa.provider import MwaaProvider


def test_environment_variables():
    def _convert(configs):
        return MwaaProvider.get_env_vars_for_airflow_configs(configs)

    assert _convert({"core.lazy_load_plugins": "true"}) == {
        "AIRFLOW__CORE__LAZY_LOAD_PLUGINS": "true"
    }
    assert _convert({" smtp.smtp_port": 587, "smtp.smtp_ssl  ": "true"}) == {
        "AIRFLOW__SMTP__SMTP_PORT": "587",
        "AIRFLOW__SMTP__SMTP_SSL": "true",
    }
