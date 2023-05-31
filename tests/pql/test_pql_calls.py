import pytest

from ats.pql.pql import Any, parse_query


def test_relation_calls_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Calls(s1, "hi")
           """
    )

    assert result[0]["relations"][0]["relation"] == "Calls"


def test_parameters_relation_calls_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Calls('_', s1)
           """
    )

    assert result[0]["relations"][0]["parameters"][0] is Any
    assert result[0]["relations"][0]["parameters"][1] == "s1"


def test_relation_calls_star_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Calls*(s1, "temp")
           """
    )

    assert result[0]["relations"][0]["relation"] == "Calls*"


def test_parameters_relation_calls_star_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Calls*("tres", "cuatro")
           """
    )

    assert result[0]["relations"][0]["parameters"][0] == '"tres"'
    assert result[0]["relations"][0]["parameters"][1] == '"cuatro"'


def test_not_valid_relation_calls_in_query():
    with pytest.raises(ValueError, match="Token '90' is not valid ENT_REF_TOKEN"):
        parse_query(
            """
                stmt s1;
                Select s1 such that Calls('_', 90)
            """
        )


def test_not_valid_relation_calls_in_query_2():
    with pytest.raises(ValueError, match="Token '5' is not valid ENT_REF_TOKEN"):
        parse_query(
            """ stmt s1;
                Select s1 such that Calls(5, 3)
            """
        )
