import pytest

from ats.pql.pql import Any, parse_query


def test_relation_follows_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Follows(s1, 3)
           """
    )

    assert result[0]["relations"][0]["relation"] == "Follows"


def test_parameters_relation_follows_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Follows('_', 10)
           """
    )

    assert result[0]["relations"][0]["parameters"][0] is Any
    assert result[0]["relations"][0]["parameters"][1] == "10"


def test_relation_follows_star_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Follows*(s1, 2)
           """
    )

    assert result[0]["relations"][0]["relation"] == "Follows*"


def test_parameters_relation_follows_star_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Follows*(20, 30)
           """
    )

    assert result[0]["relations"][0]["parameters"][0] == "20"
    assert result[0]["relations"][0]["parameters"][1] == "30"


def test_not_valid_relation_follows_in_query():
    with pytest.raises(
        ValueError, match="""Token '"ats"' is not valid STMT_REF_TOKEN"""
    ):
        parse_query(
            """ stmt s1;
                Select s1 such that Follows('_', "ats")
               """
        )


def test_not_valid_relation_follows_in_query_2():
    with pytest.raises(
        ValueError, match="""Token '"row"' is not valid STMT_REF_TOKEN"""
    ):
        parse_query(
            """ stmt s1;
                Select s1 such that Follows("row", 3)
               """
        )
