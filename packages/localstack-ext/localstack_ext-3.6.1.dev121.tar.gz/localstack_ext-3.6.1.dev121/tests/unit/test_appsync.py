import json
import re

import pytest
from airspeed.operators import TemplateExecutionError
from localstack.http import Request
from localstack.pro.core.aws.api.appsync import DataSource, HttpDataSourceConfig, NotFoundException
from localstack.pro.core.services.appsync.data_sources import (
    DataSourceDynamoDB,
    DataSourceHttp,
    DataSourceRelationalDB,
)
from localstack.pro.core.services.appsync.graphql_executor import execute_graphql
from localstack.pro.core.services.appsync.mapping import MappingRenderEngineJS, MappingTemplateType
from localstack.pro.core.services.appsync.models import AppSyncStore
from localstack.pro.core.services.appsync.resolvers import (
    ResolverProcessingContext,
    render_template,
)
from localstack.pro.core.services.appsync.velocity_functions import (
    base64_decode,
    base64_encode,
    default_if_null,
    default_if_null_or_blank,
    default_if_null_or_empty,
    is_boolean,
    is_list,
    is_map,
    is_null,
    is_null_or_blank,
    is_null_or_empty,
    is_number,
    is_string,
    matches,
    parse_json,
    to_binary,
    to_binary_json,
    to_boolean,
    to_boolean_json,
    to_json,
    to_null,
    to_null_json,
    to_number,
    to_number_json,
    to_string,
    to_string_json,
    type_of,
)
from localstack.utils.strings import to_str

TEST_SCHEMA = """
schema {
  query: Query
  mutation: Mutation
}

type Mutation {
  createOrUpdateWalletInfo(input: CreateOrUpdateWalletInfoInput!): WalletInfo
  dumpWalletInfo(input: CreateOrUpdateWalletInfoInput!): WalletInfo
}

type Query {
  getWalletInfo(user_id: String!): WalletInfo
}

type UserIds {
  items: [String]
  nextToken: String
}

type WalletInfo {
  confirmed_balance: Int!
  conio_version: Int!
  unconfirmed_balance: Int!
  user_id: String!
}

input CreateOrUpdateWalletInfoInput {
  confirmed_balance: Int!
  conio_version: Int!
  unconfirmed_balance: Int!
  user_id: String!
}

input TableBooleanFilterInput {
  eq: Boolean
  ne: Boolean
}

input TableFloatFilterInput {
  between: [Float]
  contains: Float
  eq: Float
  ge: Float
  gt: Float
  le: Float
  lt: Float
  ne: Float
  notContains: Float
}

input TableIDFilterInput {
  beginsWith: ID
  between: [ID]
  contains: ID
  eq: ID
  ge: ID
  gt: ID
  le: ID
  lt: ID
  ne: ID
  notContains: ID
}

input TableIntFilterInput {
  between: [Int]
  contains: Int
  eq: Int
  ge: Int
  gt: Int
  le: Int
  lt: Int
  ne: Int
  notContains: Int
}

input TableStringFilterInput {
  beginsWith: String
  between: [String]
  contains: String
  eq: String
  ge: String
  gt: String
  le: String
  lt: String
  ne: String
  notContains: String
}
"""
# ruff: noqa: E501
TEST_SOURCES = [
    {
        "name": "wallet_info",
        "description": "DynamoDB data source",
        "type": "AMAZON_DYNAMODB",
        "serviceRoleArn": "arn:aws:iam::000000000000:role/conio-appsync-dev-GraphQlDswalletinfoRole-OSQXHH034UQ6",
        "dynamodbConfig": {
            "awsRegion": "us-east-1",
            "tableName": "arn:aws:dynamodb:us-east-1:000000000000:table/wallet_info",
            "useCallerCredentials": False,
        },
    }
]
# ruff: noqa: E501
TEST_RESOLVERS = {
    "Query": [
        {
            "fieldName": "getWalletInfo",
            "requestMappingTemplate": '## Below example shows how to look up an item with a Primary Key of "id" from GraphQL arguments\n## The helper $util.dynamodb.toDynamoDBJson automatically converts to a DynamoDB formatted request\n## There is a "context" object with arguments, identity, headers, and parent field information you can access.\n## It also has a shorthand notation avaialable:\n##  - $context or $ctx is the root object\n##  - $ctx.arguments or $ctx.args contains arguments\n##  - $ctx.identity has caller information, such as $ctx.identity.username\n##  - $ctx.request.headers contains headers, such as $context.request.headers.xyz\n##  - $ctx.source is a map of the parent field, for instance $ctx.source.xyz\n## Read more: https://docs.aws.amazon.com/appsync/latest/devguide/resolver-mapping-template-reference.html\n#if ($context.identity.sub == $ctx.args.user_id)\n{\n    "version": "2017-02-28",\n    "operation": "GetItem",\n    "key": {\n        "user_id": $util.dynamodb.toDynamoDBJson($ctx.args.user_id),\n    }\n}\n#else\n$utils.unauthorized()\n#end',
            "responseMappingTemplate": "## Pass back the result from DynamoDB. **\n$util.toJson($ctx.result)",
            "dataSourceName": "wallet_info",
        }
    ],
    "Mutation": [
        {
            "fieldName": "createOrUpdateWalletInfo",
            "requestMappingTemplate": '## Below example shows how to create an object from all provided GraphQL arguments\n## The primary key of the obejct is a randomly generated UUD using the $util.autoId() utility\n## Other utilities include $util.matches() for regular expressions, $util.time.nowISO8601() or\n##   $util.time.nowEpochMilliSeconds() for timestamps, and even List or Map helpers like\n##   $util.list.copyAndRetainAll() $util.map.copyAndRemoveAllKeys() for shallow copies\n## Read more: https://docs.aws.amazon.com/appsync/latest/devguide/resolver-context-reference.html#utility-helpers-in-util\n\n#if ($context.identity.sub == "admin")\n{\n    "version" : "2017-02-28",\n    "operation" : "PutItem",\n    "key" : {\n        "user_id": $util.dynamodb.toDynamoDBJson($context.arguments.input.user_id)\n    },\n    "attributeValues" : $util.dynamodb.toMapValuesJson($context.arguments.input),\n    #if($context.arguments.input.conio_version == 1)\n    "condition" : {\n        "expression"       : "attribute_not_exists(user_id)"\n    }\n    #else\n    "condition" : {\n        "expression"       : "attribute_not_exists(user_id) OR conio_version < :conio_version",\n        "expressionValues" : {\n            ":conio_version": $util.dynamodb.toDynamoDBJson($context.arguments.input.conio_version)\n        }\n    }\n    #end\n}\n#else\n$utils.unauthorized()\n#end',
            "responseMappingTemplate": "## Pass back the result from DynamoDB. **\n$util.toJson($ctx.result)",
            "dataSourceName": "wallet_info",
        },
        {
            "fieldName": "dumpWalletInfo",
            "requestMappingTemplate": '#if ($context.identity.sub == "admin")\n{\n    "version" : "2017-02-28",\n    "operation" : "PutItem",\n    "key" : {\n        "user_id": $util.dynamodb.toDynamoDBJson($context.arguments.input.user_id),\n    },\n    "attributeValues" : $util.dynamodb.toMapValuesJson($context.arguments.input)\n}\n#else\n$utils.unauthorized()\n#end\n',
            "responseMappingTemplate": "## Pass back the result from DynamoDB. **\n$util.toJson($ctx.result)",
            "dataSourceName": "wallet_info",
        },
    ],
    "Subscription": [
        {
            "fieldName": "onCreateOrUpdateWalletInfo",
            "requestMappingTemplate": '#if ($context.identity.sub == $ctx.args.user_id)\n{\n    "version": "2017-02-28",\n    "operation": "GetItem",\n    "key": {\n        "user_id": $util.dynamodb.toDynamoDBJson($ctx.args.user_id),\n    }\n}\n#else\n$utils.unauthorized()\n#end',
            "responseMappingTemplate": "## Pass back the result from DynamoDB. **\n$util.toJson($ctx.result)",
            "dataSourceName": "wallet_info",
        }
    ],
}
TEST_QUERY = """
mutation {
createOrUpdateWalletInfo(input: {confirmed_balance: 0, unconfirmed_balance: 100, conio_version: 1, user_id: "7a1a6078-ef27-4755-9ba8-220edf1bba44"}){user_id}
}
"""


class TestAppSync:
    def run_graphql_mutation(self):
        # TODO: move to integration tests; prepare DDB table to contain required data to render the request
        result = execute_graphql(TEST_QUERY, TEST_SCHEMA, TEST_SOURCES, TEST_RESOLVERS)
        assert "user_id" in result.data.get("createOrUpdateWalletInfo", {})

    def test_api_metadata(self):
        backend = AppSyncStore()
        assert len(backend.api_metadata) == 0
        api_id = "some_api_id"
        api_metadata = {"some_key": "some_value"}
        backend.set_api_metadata(api_id, api_metadata)
        assert len(backend.api_metadata) == 1
        assert api_id in backend.api_metadata
        assert backend.get_api_metadata(api_id) == api_metadata
        assert backend.pop_api_metadata(api_id) == api_metadata
        assert len(backend.api_metadata) == 0

    def test_domain_configs(self):
        backend = AppSyncStore()
        assert len(backend.domain_configs) == 0
        domain_name = "some_domain_name"
        domain_config = {"some_key": "some_value"}
        backend.set_domain_config(domain_name, domain_config)
        assert len(backend.domain_configs) == 1
        assert domain_name in backend.domain_configs
        assert backend.get_domain_config(domain_name) == domain_config
        assert backend.pop_domain_configs(domain_name) == domain_config
        assert len(backend.domain_configs) == 0

    def test_set_api_associations_fails_when_api_id_is_unknown(self):
        backend = AppSyncStore()
        api_id = "some_api_id"
        domain_name = "some_domain_name"
        api_association = {"apiId": api_id}
        backend.set_domain_config(domain_name, {})
        with pytest.raises(NotFoundException) as e:
            backend.set_api_association(domain_name, api_association)

    def test_set_api_associations_fails_when_domain_name_is_unknown(self):
        backend = AppSyncStore()
        api_id = "some_api_id"
        domain_name = "some_domain_name"
        api_association = {"apiId": api_id}
        backend.set_api_metadata(api_id, {})
        with pytest.raises(NotFoundException) as e:
            backend.set_api_association(domain_name, api_association)

    def test_api_associations(self):
        backend = AppSyncStore()
        assert len(backend.api_metadata) == 0
        assert len(backend.domain_configs) == 0
        assert len(backend.api_associations) == 0
        api_id = "some_api_id"
        domain_name = "some_domain_name"
        api_association = {"apiId": api_id}
        backend.set_api_metadata(api_id, {})
        backend.set_domain_config(domain_name, {})
        backend.set_api_association(domain_name, api_association)
        assert len(backend.api_associations) == 1
        assert domain_name in backend.api_associations
        assert backend.get_api_association(domain_name) == api_association
        assert backend.pop_api_associations(domain_name) == api_association
        assert len(backend.api_associations) == 0

    def test_api_id_removal_removes_its_associations(self):
        backend = AppSyncStore()
        api_id = "some_api_id"
        domain_name = "some_domain_name"
        api_association = {"apiId": api_id}
        backend.set_api_metadata(api_id, {})
        backend.set_domain_config(domain_name, {})
        backend.set_api_association(domain_name, api_association)

        # Keys for associations are domain names, so looking up them even if we delete API IDs
        assert domain_name in backend.api_associations
        assert backend.get_api_association(domain_name)["apiId"] == api_id
        backend.pop_api_metadata(api_id)
        assert domain_name not in backend.api_associations

    def test_domain_name_removal_removes_its_associations(self):
        backend = AppSyncStore()
        api_id = "some_api_id"
        domain_name = "some_domain_name"
        api_association = {"apiId": api_id}
        backend.set_api_metadata(api_id, {})
        backend.set_domain_config(domain_name, {})
        backend.set_api_association(domain_name, api_association)

        assert domain_name in backend.api_associations
        backend.pop_domain_configs(domain_name)
        assert domain_name not in backend.api_associations


class TestAppSyncUtils:
    def test_to_json(self):
        json_obj = {"abc": "123", "def": "456"}
        res = to_json(json_obj)

        assert isinstance(res, str)

    def test_parse_json(self):
        json_obj = {"abc": "123", "def": "456"}
        stringified_json = to_json(json_obj)
        parsed_json = parse_json(stringified_json)

        assert parsed_json == json_obj

    def test_base64_encode_decode(self):
        message = "This is a test message"
        encoded_message = message.encode("utf-8")
        base64_encoded = base64_encode(encoded_message)
        base64_decoded = base64_decode(base64_encoded)

        assert isinstance(base64_encoded, str)
        assert isinstance(base64_decoded, str)
        assert base64_decoded == message

    def test_is_null(self):
        res1 = is_null(None)
        res2 = is_null("Test")

        assert res1
        assert not res2

    def test_is_null_or_empty(self):
        assert is_null_or_empty("")
        assert is_null_or_empty(None)
        assert not is_null_or_empty("None")

    def test_is_null_or_blank(self):
        assert is_null_or_blank("  ")
        assert is_null_or_blank(None)
        assert not is_null_or_blank("Not None")

    def test_default_if_null(self):
        obj1 = "Test String One"
        obj2 = "Test String Two"
        obj3 = None

        assert default_if_null(obj1, obj2) == obj1
        assert default_if_null(obj3, obj2) == obj2

    def test_default_if_null_or_empty(self):
        obj1 = "Test String One"
        obj2 = "Test String Two"
        obj3 = ""
        obj4 = None

        assert default_if_null_or_empty(obj4, obj2) == obj2
        assert default_if_null_or_empty(obj3, obj2) == obj2
        assert default_if_null_or_empty(obj1, obj2) == obj1

    def test_default_if_null_or_blank(self):
        obj1 = "Test String One"
        obj2 = "Test String Two"
        obj3 = "   "
        obj4 = None

        assert default_if_null_or_blank(obj4, obj2) == obj2
        assert default_if_null_or_blank(obj3, obj2) == obj2
        assert default_if_null_or_blank(obj1, obj2) == obj1

    def test_is_string(self):
        obj1 = "Test String One"
        obj2 = ["1", "2", "3"]

        assert is_string(obj1)
        assert not is_string(obj2)

    def test_is_number(self):
        obj1 = "Test String One"
        obj2 = 1648
        obj3 = 16.48

        assert not is_number(obj1)
        assert is_number(obj2)
        assert is_number(obj3)

    def test_is_boolean(self):
        obj1 = "Test String One"
        obj2 = False

        assert not is_boolean(obj1)
        assert is_boolean(obj2)

    def test_is_list(self):
        obj1 = "Test String One"
        obj2 = ["1", "2", "3"]

        assert not is_list(obj1)
        assert is_list(obj2)

    def test_is_map(self):
        assert not is_map([1, 2, 3])
        assert not is_map("map")
        assert not is_map("dict")
        assert is_map({})
        assert is_map({"foo": "bar"})

    def test_type_of(self):
        obj1 = [1, 2, 3]
        obj2 = "String Type"
        obj3 = {"foo": "bar"}
        obj4 = True
        obj5 = 1221
        obj6 = 12.21
        obj7 = None

        assert type_of(obj1) == "List"
        assert type_of(obj2) == "String"
        assert type_of(obj3) == "Map"
        assert type_of(obj4) == "Boolean"
        assert type_of(obj5) == "Number"
        assert type_of(obj6) == "Number"
        assert type_of(obj7) == "Null"

    def test_matches(self):
        re = "^l.c.l...c.$"
        message1 = "localstack"
        message2 = "localstack-ext"

        assert matches(re, message1)
        assert not matches(re, message2)

    def test_to_string(self):
        op1 = to_string("localstack")
        op2 = to_string(12345)
        expected_output = {"S": "localstack"}
        assert op1 == expected_output
        assert op2 is None

    def test_to_string_json(self):
        op1 = to_string_json("localstack")
        op2 = to_string_json(12345)
        expected_output = json.dumps({"S": "localstack"})
        assert op1 == expected_output
        assert op2 is None

    def test_to_number(self):
        op1 = to_number(12345)
        op2 = to_number("localstack")
        expected_output = {"N": 12345}
        assert op1 == expected_output
        assert op2 is None

    def test_to_number_json(self):
        op1 = to_number_json(12345)
        op2 = to_number_json("localstack")
        expected_output = json.dumps({"N": 12345})
        assert op1 == expected_output
        assert op2 is None

    def test_to_binary(self):
        op1 = to_binary("binary_data")
        op2 = to_binary({"K": "V"})
        expected_output = {"B": "binary_data"}
        assert op1 == expected_output
        assert op2 is None

    def test_to_binary_json(self):
        op1 = to_binary_json("binary_data")
        op2 = to_binary_json({"K": "V"})
        expected_output = json.dumps({"B": "binary_data"})
        assert op1 == expected_output
        assert op2 is None

    def test_to_boolean(self):
        op1 = to_boolean(True)
        op2 = to_boolean("true")
        expected_output = {"BOOL": True}
        assert op1 == expected_output
        assert op2 is None

    def test_to_boolean_json(self):
        op1 = to_boolean_json(True)
        op2 = to_boolean_json("true")
        expected_output = json.dumps({"BOOL": True})
        assert op1 == expected_output
        assert op2 is None

    def test_to_null(self):
        op1 = to_null(None)
        op2 = to_null("null")
        expected_output = {"NULL": None}
        assert op1 == expected_output
        assert op2 is None

    def test_to_null_json(self):
        op1 = to_null_json(None)
        op2 = to_null_json("null")
        expected_output = json.dumps({"NULL": None})
        assert op1 == expected_output
        assert op2 is None


class TestTemplating:
    def test_resolver_functions(self):
        template = '$util.dynamodb.toDynamoDB({ "foo": "bar", "baz" : 1234, "beep": [ "boop"] })'
        result = render_template(template)
        expected = {
            "M": {"foo": {"S": "bar"}, "baz": {"N": "1234"}, "beep": {"L": [{"S": "boop"}]}}
        }
        assert result == str(expected)
        result = render_template(template.replace("toDynamoDB", "toDynamoDBJson"))
        assert result == expected

    def test_put_map_to_json(self):
        template = """
        #set($v1 = {})\n#set($discard = $v1.put('value', 'hi2'))\n$util.toJson($v1)
        """
        result = render_template(template, as_json=False).strip()
        assert result == '{"value": "hi2"}'

    def test_set_variables_in_foreach_loop(self):
        template = """
        #foreach($x in [1, 2, 3])
            #if($x == 1 or $x == 3)
                #set($context.stash.return__val = "loop$x")
                #set($context.stash.return__flag = true)
                #return($context.stash.return__val)
            #end
        #end
        #return('end')
        """
        result = render_template(template, as_json=False).strip()
        result = re.sub(r"\s+", " ", result).strip()
        assert result == "loop1 loop3 end"

    def test_auto_id_util(self):
        template = "$util.autoId()"
        result = render_template(template, as_json=False)
        assert result.strip()

    def test_quiet_run(self):
        template = "$util.qr('test')"
        result = render_template(template, as_json=False)
        assert not result.strip()

    def test_put_result_to_dict(self):
        context = ResolverProcessingContext()
        context.result = {"foo": "bar"}

        template = "$ctx.result"
        result = render_template(template, context, as_json=False).strip()
        assert result == str({"foo": "bar"})

        template = """
        $util.qr($ctx.result.put("test", 123))
        $util.toJson($ctx.result)
        """
        result = render_template(template, context, as_json=False).strip()
        result = json.loads(result)
        assert result == {"foo": "bar", "test": 123}

    def test_match_regex_pattern(self):
        template = r"""
        #set($valid = $util.matches("^[a-zA-Z0-9_.+-]+@(?:(?:[a-zA-Z0-9-]+\\.)?[a-zA-Z]+\\.)?(local)\.stack", $context.stash.email))
        #if ($valid)
            matches!
        #end
        """
        context = ResolverProcessingContext()
        context.stash = {"email": "test123"}
        result = render_template(template, context)
        assert not result.strip()
        context.stash = {"email": "test@local.stack"}
        result = render_template(template, context)
        assert result.strip() == "matches!"

    def test_nested_items(self):
        context = ResolverProcessingContext()
        stash_expected = context.stash["value"] = 20
        prev = ResolverProcessingContext()
        expected = prev.result = {"a": 10}
        context.prev = prev

        d = context.to_dict()

        assert isinstance(d["prev"], dict)

        assert d["stash"]["value"] == stash_expected
        assert d["prev"]["result"] == expected

    def test_render_template(self):
        template = r"""
        #set($valid = $util.matches("^[a-zA-Z0-9_.+-]+@(?:(?:[a-zA-Z0-9-]+\.)?[a-zA-Z]+\.)?(local)\.stack", $ctx.stash.email))
        #if (!$valid)
            $util.error("$ctx.stash.email is not a valid email.")
        #end
        $ctx.stash.email
        """
        context = ResolverProcessingContext()

        context.stash = {"email": "test123"}
        with pytest.raises(TemplateExecutionError):
            render_template(template, context)

        context.stash = {"email": "stacky@local.stack"}
        result = render_template(template, context)
        assert result.strip() == "stacky@local.stack"

    def test_context_arguments(self):
        context = ResolverProcessingContext()
        # without any arguments, the "args" key is not present
        assert "args" not in context.to_dict()

        context.arguments["foo"] = "bar"
        context_dict = context.to_dict()

        assert context_dict["arguments"]["foo"] == "bar"
        # we have arguments, so the "args" key is present
        assert context_dict["args"]["foo"] == "bar"


class TestMappingRenderEngine:
    @pytest.mark.parametrize("code_response", ["null", "undefined", "", "dict"])
    @pytest.mark.parametrize(
        "template_type", [MappingTemplateType.REQUEST, MappingTemplateType.RESPONSE]
    )
    def test_render_template_with_null_response(self, code_response, template_type):
        engine = MappingRenderEngineJS()
        context = ResolverProcessingContext()

        # test request mapping template JS code with different response values
        code_response_str = code_response
        if code_response == "dict":
            if template_type == MappingTemplateType.REQUEST:
                code_response_str = "{payload: {foo: 'bar'}}"
            else:
                code_response_str = "{foo: 'bar'}"

        code = f"export function {template_type}(ctx) {{ return {code_response_str}; }}"

        result = engine.render(context, code=code, template_type=template_type)

        if code_response == "dict":
            if template_type == MappingTemplateType.REQUEST:
                assert result == {"payload": {"foo": "bar"}}
            else:
                assert result == {"foo": "bar"}
        else:
            assert result is None


class TestDataSources:
    @pytest.mark.parametrize("http_path", [None, "/test/path/123"])
    @pytest.mark.parametrize("http_method", ["GET", "POST"])
    def test_http_data_source(self, http_path, http_method, httpserver):
        requests = []

        def _handler(_request: Request):
            requests.append({**_request.__dict__, "body": to_str(_request.data)})

        httpserver.expect_request("").respond_with_handler(_handler)

        ds = DataSourceHttp()
        source = DataSource()
        source["httpConfig"] = http_config = HttpDataSourceConfig()
        http_config["endpoint"] = httpserver.url_for("/")
        request = {
            "resourcePath": http_path,
            "method": http_method,
            "params": {"headers": {"h1": "test 123"}, "body": "test foo bar"},
        }
        ds.send_request(source, request)
        result = requests[0]
        assert result["method"] == http_method
        assert result["path"] == http_path or "/"
        assert result["headers"]["h1"] == "test 123"
        assert result["body"] == "test foo bar"

    @pytest.mark.parametrize(
        "input,output",
        [
            (None, {"isNull": True}),
            (False, {"booleanValue": False}),
            (42.0, {"doubleValue": 42.0}),
            ("test", {"stringValue": "test"}),
            (42, {"longValue": 42}),
            (
                [1, 2, [3, 4]],
                {
                    "arrayValues": [
                        {"longValue": 1},
                        {"longValue": 2},
                        {
                            "arrayValues": [
                                {"longValue": 3},
                                {"longValue": 4},
                            ]
                        },
                    ]
                },
            ),
        ],
    )
    def test_deduce_parameter_types(self, input, output):
        assert DataSourceRelationalDB._deduce_parameter_value(input) == output

    def test_dynamo_next_token_round_trip(self):
        last_evaluated_key = {"pk": {"S": "abc"}, "sk": {"S": "123"}}
        next_token = DataSourceDynamoDB._last_evaluated_key_to_next_token(last_evaluated_key)
        assert (
            DataSourceDynamoDB._next_token_to_last_evaluated_key(next_token) == last_evaluated_key
        )
