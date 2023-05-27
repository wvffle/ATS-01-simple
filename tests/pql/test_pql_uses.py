import pytest

from ats.pql.pql import parse_query


def test_relation_uses_in_query():
    result = parse_query(
        """ while w3;
            Select w3 such that Uses(w3, "x")
           """
    )

    assert result[0]["relations"][0]["relation"] == "Uses"


def test_parameters_relation_uses_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Uses(10, "z")
           """
    )

    assert result[0]["relations"][0]["parameters"][0] == "10"
    assert result[0]["relations"][0]["parameters"][1] == '"z"'


def test_not_valid_relation_first_parameter_uses_in_query():
    with pytest.raises(
        ValueError, match="""Token '"dos"' is not valid STMT_REF_TOKEN"""
    ):
        parse_query(
            """ stmt s1;
                Select s1 such that Uses("dos", 109)
               """
        )


def test_not_valid_relation_second_parameter_uses_in_query():
    with pytest.raises(ValueError, match="Token '16' is not valid ENT_REF_TOKEN"):
        parse_query(
            """ stmt s2;
                Select s2 such that Uses(s2, 16)
               """
        )


def test_not_valid_relation_uses_star_in_query():
    with pytest.raises(ValueError, match="Token 'Uses\\*' is not a valid NAME_TOKEN"):
        parse_query(
            """ stmt s1;
                Select s1 such that Uses*(s1, 4)
               """
        )
