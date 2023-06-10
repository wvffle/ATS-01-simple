import pytest

from ats.pql.pql import Any, parse_query


def test_relation_follows_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Follows(s1, 3)
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Follows"


def test_parameters_relation_follows_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Follows(_, 10)
           """
    )

    anything = result[0]["conditions"]["relations"][0]["parameters"][0]
    assert anything is Any
    assert result[0]["conditions"]["relations"][0]["parameters"][1] == 10


def test_relation_follows_star_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Follows*(s1, 2)
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Follows*"


def test_parameters_relation_follows_star_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Follows*(20, 30)
           """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] == 20
    assert result[0]["conditions"]["relations"][0]["parameters"][1] == 30


def test_not_valid_relation_follows_in_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s1;
                Select s1 such that Follows(_, "ats")
               """
        )

    assert 'Relationship Follows(_, "ats") is not valid.' in str(e.value)


def test_not_valid_relation_follows_in_query_2():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s1;
                Select s1 such that Follows("row", 3)
               """
        )
    assert 'Relationship Follows("row", 3) is not valid.' in str(e.value)
