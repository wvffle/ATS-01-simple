import pytest

from ats.pql.pql import parse_query


def test_relation_uses_in_query():
    result = parse_query(
        """ while w3; procedure p1; variable v1;
            Select w3 such that Uses(p1, v1)
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Uses"


def test_parameters_relation_uses_in_query():
    result = parse_query(
        """ stmt s1; variable v1;
            Select s1 such that Uses(10, v1)
           """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] == 10
    assert result[0]["conditions"]["relations"][0]["parameters"][1] == "v1"


def test_not_valid_relation_first_parameter_uses_in_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s1;
                Select s1 such that Uses("dos", 109)
               """
        )

        assert (
            """Relationship Uses("dos", 109) is not valid. Expected one of Uses(procedure, variable) | Uses(stmt, variable)\non line 2"""
            in str(e.value)
        )


def test_not_valid_relation_second_parameter_uses_in_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s2; variable v1;
                Select s2 such that Uses(s2, 16)
               """
        )

        assert (
            "Relationship Uses(stmt, 16) is not valid. Expected one of Uses(procedure, variable) | Uses(stmt, variable)\non line 2"
            in str(e.value)
        )


def test_not_valid_relation_uses_star_in_query():
    with pytest.raises(
        ValueError, match="Token 'Uses\\*' is not a valid RELATIONSHIP_NAME"
    ):
        parse_query(
            """ stmt s1; variable v1;
                Select s1 such that Uses*(s1, v1)
               """
        )
