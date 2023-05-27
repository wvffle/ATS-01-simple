import pytest

from ats.pql.pql import parse_pql


def test_relation_modifies_in_query():
    result = parse_pql(
        """ assign a2;
            Select a2 such that Modifies(a2, "x")
           """
    )

    assert result[0]["relations"][0]["relation"] == "Modifies"


def test_parameters_relation_modifies_in_query():
    result = parse_pql(
        """ stmt s1;
            Select s1 such that Modifies(4, "y")
           """
    )

    assert result[0]["relations"][0]["parameters"][0] == "4"
    assert result[0]["relations"][0]["parameters"][1] == '"y"'


def test_not_valid_relation_first_parameter_modifies_in_query():
    with pytest.raises(
        ValueError, match="""Token '"uno"' is not valid STMT_REF_TOKEN"""
    ):
        parse_pql(
            """ stmt s1;
                Select s1 such that Modifies("uno", 4)
               """
        )


def test_not_valid_relation_second_parameter_modifies_in_query():
    with pytest.raises(ValueError, match="Token '4' is not valid ENT_REF_TOKEN"):
        parse_pql(
            """ stmt s1;
                Select s1 such that Modifies(s1, 4)
               """
        )


def test_not_valid_relation_modifies_star_in_query():
    with pytest.raises(
        ValueError, match="Token 'Modifies\\*' is not a valid NAME_TOKEN"
    ):
        parse_pql(
            """ stmt s1;
                Select s1 such that Modifies*(s1, 4)
               """
        )
