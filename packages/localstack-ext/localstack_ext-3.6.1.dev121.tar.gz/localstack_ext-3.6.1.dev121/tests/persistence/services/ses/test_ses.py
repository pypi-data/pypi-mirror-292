from localstack.utils.strings import short_uid


def test_ses_get_template(persistence_validations, snapshot, aws_client):
    template_name = f"template-{short_uid()}"
    aws_client.ses.create_template(
        Template={
            "TemplateName": template_name,
            "SubjectPart": "Sample Subject",
            "TextPart": "Sample Text",
            "HtmlPart": "<p></p>",
        }
    )

    def validate():
        snapshot.match("ses_get_template", aws_client.ses.get_template(TemplateName=template_name))

    persistence_validations.register(validate)
