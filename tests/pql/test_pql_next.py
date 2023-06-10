import pytest

from ats.pql.pql import Any, parse_query


def test_relation_next_in_query():
    result = parse_query(
        """ stmt s1; prog_line pl;
            Select s1 such that Next(pl, 3)
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Next"


def test_parameters_relation_next_in_query():
    result = parse_query(
        """ stmt s1; prog_line pl;
            Select s1 such that Next(pl, 3)
           """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] == "pl"
    assert result[0]["conditions"]["relations"][0]["parameters"][1] == 3


def test_relation_next_star_in_query():
    result = parse_query(
        """ stmt s1; prog_line pl;
            Select s1 such that Next*(pl, 2)
           """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Next*"


def test_parameters_relation_next_star_in_query():
    result = parse_query(
        """ stmt s2; prog_line pl;
            Select s2 such that Next*(pl, _)
           """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] == "pl"
    assert result[0]["conditions"]["relations"][0]["parameters"][1] is Any


def test_not_valid_relation_frst_parameter_next_in_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s1;
                Select s1 such that Next("zmienna", _)
               """
        )

        assert (
            """Relationship Next("zmienna", _) is not valid. Expected Next(prog_line, prog_line)\non line 2"""
            not in str(e.value)
        )


def test_not_valid_relation_second_parameter_next_in_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s2;
                Select s2 such that Next(s2, "x")
               """
        )

        assert """Token '"x"' is not valid STMT_REF_TOKEN""" not in str(e.value)
