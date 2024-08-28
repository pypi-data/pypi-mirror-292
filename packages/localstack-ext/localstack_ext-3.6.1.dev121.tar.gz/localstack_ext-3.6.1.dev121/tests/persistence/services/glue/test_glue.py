from localstack.utils.strings import short_uid


def test_glue_get_job(persistence_validations, snapshot, aws_client):
    job_name = f"glue-job-{short_uid()}"
    aws_client.glue.create_job(Name=job_name, Role="r1", Command={"Name": "pythonshell"})

    def validate():
        snapshot.match("get_glue_job", aws_client.glue.get_job(JobName=job_name))

    persistence_validations.register(validate)
