import pytest

from ats.pql.pql import Any, parse_query


def test_relation_calls_in_query():
    result = parse_query(
        """ procedure s1;
            Select s1 such that Calls(s1, "hi")
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Calls"


def test_parameters_relation_calls_in_query():
    result = parse_query(
        """ procedure s1;
            Select s1 such that Calls(_, s1)
           """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] is Any
    assert result[0]["conditions"]["relations"][0]["parameters"][1] == "s1"


def test_relation_calls_star_in_query():
    result = parse_query(
        """ procedure s1;
            Select s1 such that Calls*(s1, "temp")
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Calls*"


def test_parameters_relation_calls_star_in_query():
    result = parse_query(
        """ procedure s1;
            Select s1 such that Calls*("tres", "cuatro")
           """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] == '"tres"'
    assert result[0]["conditions"]["relations"][0]["parameters"][1] == '"cuatro"'


def test_not_valid_relation_calls_in_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """
                procedure s1;
                Select s1 such that Calls(_, 90)
            """
        )
    assert "Relationship Calls(_, 90) is not valid." in str(e.value)


def test_not_valid_relation_calls_in_query_2():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ procedure s1;
                Select s1 such that Calls(5, 3)
            """
        )
    assert "Relationship Calls(5, 3) is not valid." in str(e.value)
