import pytest

from ats.pql.pql import parse_query


def test_relation_modifies_in_query():
    result = parse_query(
        """ assign a2;
            Select a2 such that Modifies(a2, "x")
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Modifies"


def test_parameters_relation_modifies_in_query():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Modifies(4, "y")
           """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] == 4
    assert result[0]["conditions"]["relations"][0]["parameters"][1] == '"y"'


def test_not_valid_relation_first_parameter_modifies_in_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s1;
                Select s1 such that Modifies("uno", 4)
               """
        )
    assert 'Relationship Modifies("uno", 4) is not valid.' in str(e.value)


def test_not_valid_relation_second_parameter_modifies_in_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s1;
                Select s1 such that Modifies(s1, 4)
               """
        )
        assert "Relationship Modifies(s1, 4) is not valid." in str(e.value)


def test_not_valid_relation_modifies_star_in_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s1;
                Select s1 such that Modifies*(s1, 4)
            """
        )

        assert (
            "Relationship Modifies(stmt, stmt) is not valid. Expected one of Modifies(procedure, variable) | Modifies(stmt, variable)"
            in str(e.value)
        )
