import pytest
from localstack.pro.core.utils.parsing import parse_comma_separated_variable_assignments
from pyparsing import ParseException


def test_parse_comma_separated_variable_assignments():
    result = parse_comma_separated_variable_assignments(
        'test=123, foo = "bar", bar= \'1, 2\', baz= "3,4", v1= "4=5"'
    )
    assert result == {"bar": "1, 2", "baz": "3,4", "foo": "bar", "test": 123, "v1": "4=5"}

    assert parse_comma_separated_variable_assignments("t1=1, t2='', ") == {"t1": 1, "t2": ""}

    with pytest.raises(ParseException):
        parse_comma_separated_variable_assignments("test=")
