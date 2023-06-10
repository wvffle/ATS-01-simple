import pytest

from ats.pql.pql import Any, parse_query


def test_relation_parent_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Parent(s1, 3)
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Parent"


def test_parameters_relation_parent_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Parent(s1, 3)
           """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] == "s1"
    assert result[0]["conditions"]["relations"][0]["parameters"][1] == 3


def test_relation_parent_star_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Parent*(s1, 2)
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Parent*"


def test_parameters_relation_parent_star_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Parent*(s1, _)
           """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] == "s1"
    assert result[0]["conditions"]["relations"][0]["parameters"][1] is Any


def test_not_valid_relation_frst_parameter_parent_in_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s1;
                Select s1 such that Parent("zmienna", _)
               """
        )

    assert """Relationship Parent("zmienna", _) is not valid.""" in str(e.value)


def test_not_valid_relation_second_parameter_parent_in_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s1;
                Select s1 such that Parent(s1, "x")
               """
        )

    assert """Relationship Parent(stmt, "x") is not valid.""" in str(e.value)
