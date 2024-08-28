import pytest
from localstack.pro.core.services.iam.policy_engine.engine import (
    IAMEnforcementEngine,
    RenderException,
    ResourceRenderer,
)
from localstack.pro.core.services.iam.policy_engine.identity_policy_retrieval import (
    AssumedRole,
    Service,
    User,
)
from localstack.pro.core.services.iam.policy_engine.models import RequiredActionAndResource


@pytest.fixture
def engine():
    return IAMEnforcementEngine()


class TestResourceRendering:
    @pytest.fixture
    def renderer(self):
        return ResourceRenderer(
            map_entry={},
            resources_definition={},
            action_privilege_definition={},
            account="000000000000",
            region="us-east-1",
        )

    def test_regex_template_function(self, renderer):
        # test simple regex replacement
        service_request = {"PropertyName": "first:second"}
        template = "regex%${PropertyName}%/.*:(.+)/g"
        assert ["second"] == renderer.render_regex(service_request, template)

        # test regex replacement on target with multiple values
        service_request = {"PropertyName": ["first:second", "third:fourth", "fifth:sixth"]}
        template = "regex%${PropertyName[]}%/.*:(.+)/g"
        assert {
            "second",
            "fourth",
            "sixth",
        } == set(renderer.render_regex(service_request, template))

    def test_regex_template_function_failures(self, renderer):
        # test simple regex replacement
        service_request = {"PropertyName": "first:second"}
        template = "regex%${NotExistent}%/.*:(.+)/g"
        assert [""] == renderer.render_regex(service_request, template)

    def test_iftruthy_template_function(self, renderer):
        # test iftruthy replacement with truthy value
        service_request = {"PropertyName": "a_value"}
        template = "iftruthy%${PropertyName}%true%false"
        assert "true" == renderer.render_truthy(service_request, template)

        # test iftruthy replacement with value not present
        service_request = {}
        template = "iftruthy%${PropertyName}%true%false"
        assert "false" == renderer.render_truthy(service_request, template)

        # test iftruthy replacement with None value
        service_request = {"PropertyName": None}
        template = "iftruthy%${PropertyName}%true%false"
        assert "false" == renderer.render_truthy(service_request, template)

        # test iftruthy replacement with another placeholder as value
        service_request = {"PropertyName": "some-value", "OtherValue": "other-value"}
        template = "iftruthy%${PropertyName}%${OtherValue}%false"
        assert "${OtherValue}" == renderer.render_truthy(service_request, template)

    def test_if_template_match_template_function(self, renderer):
        service_request = {"Property1": "first:second", "Property2": "something_else_here"}
        template = "iftemplatematch%${Property1}"
        assert ["first:second"] == renderer.render_if_template_match(
            service_request, template, "${something}:${else}"
        )

        service_request = {"Property1": "first:second", "Property2": "something_else_here"}
        template = "iftemplatematch%${Property1}"
        assert [""] == renderer.render_if_template_match(
            service_request, template, "${something}:not"
        )

        service_request = {"Property1": "first:second", "Property2": "something_else_here"}
        template = "iftemplatematch%${Property1}"
        assert ["first:second"] == renderer.render_if_template_match(
            service_request, template, "${something}:second"
        )

    def test_resolve_template_functions(self, renderer):
        service_request = {"PropertyName": "some-value", "OtherValue": "other-value"}
        template = "arn:aws:%%iftruthy%${PropertyName}%${OtherValue}%false%%:something"
        assert ["arn:aws:${OtherValue}:something"] == renderer.resolve_template_functions(
            service_request, template
        )

        service_request = {"Property1": "first:second", "Property2": "something_else_here"}
        template = "arn:aws:something:%%regex%${Property1}%/.*:(.+)/g%%:anotherthing"
        assert ["arn:aws:something:second:anotherthing"] == renderer.resolve_template_functions(
            service_request, template
        )

        service_request = {"Property1": "first:second", "Property2": "something_else_here"}
        template = "arn:aws:%%iftemplatematch%${Property1}%%:anotherthing"
        assert ["arn:aws:first:second:anotherthing"] == renderer.resolve_template_functions(
            service_request, template, "${something}:${else}"
        )

        service_request = {"Property1": "value1", "Property2": "value2", "Property3": "value3"}
        template = "arn:aws:%%many%${Property1}%${Property2}%%:something"
        assert [
            "arn:aws:value1:something",
            "arn:aws:value2:something",
        ] == renderer.resolve_template_functions(service_request, template)

        service_request = {"Property1": "some/test+attribute&with,chars"}
        template = "arn:aws:%%urlencode%${Property1}%%:something"
        assert [
            "arn:aws:some%2Ftest%2Battribute%26with%2Cchars:something"
        ] == renderer.resolve_template_functions(service_request, template)

    def test_many_template_function(self, renderer):
        service_request = {"Property1": "value1", "Property2": "value2", "Property3": "value3"}
        template = "many%${Property1}%${Property2}"
        assert ["value1", "value2"] == renderer.render_many(
            service_request=service_request, template=template
        )
        service_request = {"Property1": "value1", "Property2": "value2", "Property3": "value3"}
        template = "many%${Property1}"
        assert ["value1"] == renderer.render_many(
            service_request=service_request, template=template
        )
        template = "many%${Property4}"
        assert [""] == renderer.render_many(service_request=service_request, template=template)

    def test_urlencode_template_function(self, renderer):
        service_request = {"Property1": "some/test+attribute&with,chars"}
        template = "urlencode%${Property1}"
        assert ["some%2Ftest%2Battribute%26with%2Cchars"] == renderer.render_urlencode(
            service_request=service_request, template=template
        )

    def test_render_request_placeholders(self, renderer):
        service_request = {"Property1": "value1"}
        template = "${Property1}"
        assert ["value1"] == renderer.render_plain_placeholder(service_request, template)

        service_request = {
            "Property1": {
                "Property2": [
                    {"Property3": "value1"},
                    {"Property3": "value2"},
                    {"Property3": "value3"},
                ]
            }
        }
        template = "${Property1.Property2[].Property3}"
        assert ["value1", "value2", "value3"] == renderer.render_plain_placeholder(
            service_request, template
        )

        service_request = {"Property1": {"Property2": ["value1", "value2", "value3"]}}
        template = "${Property1.Property2[]}"
        assert ["value1", "value2", "value3"] == renderer.render_plain_placeholder(
            service_request, template
        )

    def test_render_request_placeholder_failures(self, renderer):
        """Test if rendering raises a RenderException in cases
        the template keys cannot be found / have invalid types in the request"""
        # test simple not found
        service_request = {}
        template = "${Property1}"
        with pytest.raises(RenderException):
            renderer.render_plain_placeholder(service_request, template)

        # test subkey not found
        service_request = {"Property1": {}}
        template = "${Property1.Property2}"
        with pytest.raises(RenderException):
            renderer.render_plain_placeholder(service_request, template)

        # test not matching format
        service_request = {"Property1": "value1"}
        template = "${Property1.Property2}"
        with pytest.raises(RenderException):
            renderer.render_plain_placeholder(service_request, template)

        # test not matching format in list
        service_request = {"Property1": {"Property2": ["value1", "value2", "value3"]}}
        template = "${Property1.Property2[].Property3}"
        with pytest.raises(RenderException):
            renderer.render_plain_placeholder(service_request, template)

        # something completely invalid
        service_request = {"Property1": {"Property2": ["value1", "value2", "value3"]}}
        template = "${...}"
        with pytest.raises(RenderException):
            renderer.render_plain_placeholder(service_request, template)

    def test_resolve_template_placeholders(self, renderer):
        service_request = {"Property1": "value1"}
        template = "arn:aws:${Property1}:something"
        assert (True, ["arn:aws:value1:something"]) == renderer.resolve_template_placeholders(
            service_request=service_request, template=template, request_params_only=True
        )

        service_request = {"Property1": "value1"}
        template = "arn:aws:${Property1}:something:${Property2}"
        assert (
            False,
            ["arn:aws:value1:something:${Property2}"],
        ) == renderer.resolve_template_placeholders(
            service_request=service_request, template=template, request_params_only=True
        )

        service_request = {"Property1": "value1"}
        template = "arn:${Partition}:${Property1}:something"
        assert (True, ["arn:aws:value1:something"]) == renderer.resolve_template_placeholders(
            service_request=service_request, template=template, request_params_only=False
        )

        service_request = {"Property1": "value1"}
        template = "arn:${Partition}:${Property1}:something:${Property2}"
        assert (False, ["arn:aws:value1:something:*"]) == renderer.resolve_template_placeholders(
            service_request=service_request, template=template, request_params_only=False
        )

        service_request = {"Property1": "value1"}
        template = "arn:${Partition}:${Property1}:something"
        assert (
            False,
            ["arn:${Partition}:value1:something"],
        ) == renderer.resolve_template_placeholders(
            service_request=service_request, template=template, request_params_only=True
        )

    def test_resolve_template_placeholders_non_default_partition(self):
        """Test replacements in different partitions"""
        us_gov_renderer = ResourceRenderer(
            map_entry={},
            resources_definition={},
            action_privilege_definition={},
            account="000000000000",
            region="us-gov-west-1",
        )
        service_request = {"Property1": "value1"}
        template = "arn:${Partition}:${Property1}:something"
        assert (
            True,
            ["arn:aws-us-gov:value1:something"],
        ) == us_gov_renderer.resolve_template_placeholders(
            service_request=service_request, template=template, request_params_only=False
        )

        service_request = {"Property1": "value1"}
        template = "arn:${Partition}:${Region}:${Property1}:something"
        assert (
            True,
            ["arn:aws-us-gov:us-gov-west-1:value1:something"],
        ) == us_gov_renderer.resolve_template_placeholders(
            service_request=service_request, template=template, request_params_only=False
        )


class TestFilterApplicableStatements:
    @pytest.fixture
    def dummy_principal(self, aws_client):
        return AssumedRole.from_assumed_role_arn(
            "arn:aws:sts::000000000000:assumed-role/testrole/testsession",
            iam_client=aws_client.iam,
            access_key_id="LSIAQAAAAAAAGLEBQFAB",
        )

    def test_filter_statements_by_action(self, engine, aws_client, dummy_principal):
        matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:*",
                    "sqs:GetQueueAttributes",
                ],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "Action": "iam:GetUser",
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*",
            },
        ]
        not_matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetRole",
                ],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "sqs:GetQueueAttributes",
                ],
                "Resource": "*",
            },
        ]
        all_statements = matching_statements + not_matching_statements
        policy = {"Version": "2012-10-17", "Statement": all_statements}

        statements = engine.get_applicable_statements(
            required_action=RequiredActionAndResource(
                action="iam:GetUser",
                resource="arn:aws:iam::000000000000:user/test-user",
                account="000000000000",
            ),
            principal=dummy_principal,
            policies=[policy],
            match_account=False,
            iam_context={},
        )
        assert len(statements) == len(matching_statements)
        for statement in matching_statements:
            assert statement in statements

    def test_filter_statements_by_notaction(self, engine, aws_client, dummy_principal):
        matching_statements = [
            {
                "Effect": "Allow",
                "NotAction": [
                    "iam:GetRole",
                ],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "NotAction": [
                    "sqs:GetQueueAttributes",
                ],
                "Resource": "*",
            },
        ]
        not_matching_statements = [
            {
                "Effect": "Allow",
                "NotAction": [
                    "iam:*",
                    "sqs:GetQueueAttributes",
                ],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "NotAction": "iam:GetUser",
                "Resource": "*",
            },
        ]
        all_statements = matching_statements + not_matching_statements
        policy = {"Version": "2012-10-17", "Statement": all_statements}

        statements = engine.get_applicable_statements(
            required_action=RequiredActionAndResource(
                action="iam:GetUser",
                resource="arn:aws:iam::000000000000:user/test-user",
                account="000000000000",
            ),
            policies=[policy],
            principal=dummy_principal,
            match_account=False,
            iam_context={},
        )
        assert len(statements) == 2
        for statement in matching_statements:
            assert statement in statements

    def test_filter_statements_by_resource(self, engine, aws_client, dummy_principal):
        matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:*",
                ],
                "Resource": "arn:aws:iam::000000000000:user/test-user",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
            },
        ]
        not_matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "arn:aws:iam::000000000000:user/test-u",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "arn:aws:iam::000000000000:user/test-userino",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "arn:aws:iam::000000000000:role/test-user",
            },
        ]
        all_statements = matching_statements + not_matching_statements
        policy = {"Version": "2012-10-17", "Statement": all_statements}

        statements = engine.get_applicable_statements(
            required_action=RequiredActionAndResource(
                action="iam:GetUser",
                resource="arn:aws:iam::000000000000:user/test-user",
                account="000000000000",
            ),
            policies=[policy],
            principal=dummy_principal,
            match_account=False,
            iam_context={},
        )
        for statement in matching_statements:
            assert statement in statements
        assert len(statements) == 2

    def test_filter_statements_by_notresource(self, engine, aws_client, dummy_principal):
        matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "NotResource": "arn:aws:iam::000000000000:user/test-u",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "NotResource": "arn:aws:iam::000000000000:user/test-userino",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "NotResource": "arn:aws:iam::000000000000:role/test-user",
            },
        ]
        not_matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:*",
                ],
                "NotResource": "arn:aws:iam::000000000000:user/test-user",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:*",
                ],
                "NotResource": "*",
            },
        ]
        all_statements = matching_statements + not_matching_statements
        policy = {"Version": "2012-10-17", "Statement": all_statements}

        statements = engine.get_applicable_statements(
            required_action=RequiredActionAndResource(
                action="iam:GetUser",
                resource="arn:aws:iam::000000000000:user/test-user",
                account="000000000000",
            ),
            policies=[policy],
            principal=dummy_principal,
            match_account=False,
            iam_context={},
        )
        for statement in matching_statements:
            assert statement in statements
        assert len(statements) == len(matching_statements)

    def test_filter_statements_by_principal(self, engine, aws_client):
        principal = User.from_user_arn(
            user_arn="arn:aws:iam::000000000000:user/test-user", iam_client=aws_client.iam
        )
        matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:*",
                ],
                "Resource": "*",
                "Principal": {"AWS": "arn:aws:iam::000000000000:user/test-user"},
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": "*",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": {"AWS": "*"},
            },
        ]
        not_matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": {"AWS": "arn:aws:iam::000000000000:user/test-u"},
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": {"Service": "lambda.amazonaws.com"},
            },
        ]
        all_statements = matching_statements + not_matching_statements
        policy = {"Version": "2012-10-17", "Statement": all_statements}

        statements = engine.get_applicable_statements(
            required_action=RequiredActionAndResource(
                action="iam:GetUser",
                resource="arn:aws:iam::000000000000:user/test-user",
                account="000000000000",
            ),
            policies=[policy],
            principal=principal,
            match_account=False,
            iam_context={},
        )
        for statement in matching_statements:
            assert statement in statements
        assert len(statements) == len(matching_statements)

    def test_filter_statements_by_principal_account(self, engine, aws_client):
        principal = User.from_user_arn(
            user_arn="arn:aws:iam::000000000000:user/test-user", iam_client=aws_client.iam
        )
        matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:*",
                ],
                "Resource": "*",
                "Principal": {"AWS": "000000000000"},
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": "*",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": {"AWS": "*"},
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": {"AWS": "arn:aws:iam::000000000000:root"},
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": {"AWS": ["000000000000", "000000000001"]},
            },
        ]
        not_matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": {"Service": "lambda.amazonaws.com"},
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": {"AWS": ["000000000001"]},
            },
        ]
        all_statements = matching_statements + not_matching_statements
        policy = {"Version": "2012-10-17", "Statement": all_statements}

        statements = engine.get_applicable_statements(
            required_action=RequiredActionAndResource(
                action="iam:GetUser",
                resource="arn:aws:iam::000000000000:user/test-user",
                account="000000000000",
            ),
            policies=[policy],
            principal=principal,
            match_account=True,
            iam_context={},
        )
        for statement in matching_statements:
            assert statement in statements
        assert len(statements) == len(matching_statements)

    def test_filter_statements_by_service_principal(self, engine, aws_client):
        service_principal = Service(arn="lambda.amazonaws.com", account=None)
        matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:*",
                ],
                "Resource": "*",
                "Principal": {"Service": "lambda.amazonaws.com"},
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:*",
                ],
                "Resource": "*",
                "Principal": {"Service": ["lambda.amazonaws.com", "apigateway.amazonaws.com"]},
            },
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": "*",
            },
        ]
        not_matching_statements = [
            {
                "Effect": "Allow",
                "Action": [
                    "iam:GetUser",
                ],
                "Resource": "*",
                "Principal": {"AWS": "arn:aws:iam::000000000000:user/test-user"},
            }
        ]
        all_statements = matching_statements + not_matching_statements
        policy = {"Version": "2012-10-17", "Statement": all_statements}

        statements = engine.get_applicable_statements(
            required_action=RequiredActionAndResource(
                action="iam:GetUser",
                resource="arn:aws:iam::000000000000:user/test-user",
                account="000000000000",
            ),
            policies=[policy],
            principal=service_principal,
            match_account=False,
            iam_context={},
        )
        for statement in matching_statements:
            assert statement in statements
        assert len(statements) == len(matching_statements)

    def test_filter_source_arn_conditions(self, engine, aws_client, dummy_principal):
        matching_statements = [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceArn": "arn:aws:lambda:us-east-1:000000000000:function:test-function"
                    }
                },
            },
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*",
                "Condition": {
                    "StringLike": {"aws:SourceArn": "arn:aws:lambda:us-east-1:000000000000:*"}
                },
            },
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*",
                "Condition": {
                    "ArnLike": {"aws:SourceArn": "arn:aws:lambda:us-east-1:000000000000:function:*"}
                },
            },
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*",
                "Condition": {
                    "ArnLike": {"aws:SourceArn": "arn:aws:lambda:us-east-1:000000000000:*"}
                },
            },
        ]
        not_matching_statements = [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceArn": "arn:aws:lambda:us-east-1:000000000000:function:test-function-2"
                    }
                },
            },
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*",
                "Condition": {
                    "StringLike": {
                        "aws:SourceArn": "arn:aws:lambda:us-east-1:000000000000:*:notexisting"
                    }
                },
            },
        ]
        all_statements = matching_statements + not_matching_statements
        policy = {"Version": "2012-10-17", "Statement": all_statements}
        iam_context = {
            "aws:sourcearn": "arn:aws:lambda:us-east-1:000000000000:function:test-function"
        }

        statements = engine.get_applicable_statements(
            required_action=RequiredActionAndResource(
                action="iam:GetUser",
                resource="arn:aws:iam::000000000000:user/test-user",
                account="000000000000",
            ),
            policies=[policy],
            principal=dummy_principal,
            match_account=False,
            iam_context=iam_context,
        )
        for statement in matching_statements:
            assert statement in statements
        assert len(statements) == len(matching_statements)

    def test_null_matching_statement(self, engine, dummy_principal):
        matching_statements = [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*",
                "Condition": {"Null": {"aws:PrincipalTag/tag1": "false"}},
            },
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*",
                "Condition": {"Null": {"aws:PrincipalTag/tag2": "true"}},
            },
        ]
        not_matching_statements = [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*",
                "Condition": {"Null": {"aws:PrincipalTag/tag1": "true"}},
            },
        ]
        all_statements = matching_statements + not_matching_statements
        policy = {"Version": "2012-10-17", "Statement": all_statements}
        iam_context = {"aws:principaltag/tag1": "some-value"}

        statements = engine.get_applicable_statements(
            required_action=RequiredActionAndResource(
                action="iam:GetUser",
                resource="arn:aws:iam::000000000000:user/test-user",
                account="000000000000",
            ),
            policies=[policy],
            principal=dummy_principal,
            match_account=False,
            iam_context=iam_context,
        )
        for statement in matching_statements:
            assert statement in statements
        assert len(statements) == len(matching_statements)
