import pytest

from ats.pql.pql import Any, parse_query


def test_valid_parameters_with_string_in_relations():
    result = parse_query(
        """ while w3;
            Select w3 such that Uses(w3, "x")
           """
    )

    assert result[0]["such_thats"][0]["relations"][0]["parameters"][0] == "w3"
    assert result[0]["such_thats"][0]["relations"][0]["parameters"][1] == '"x"'


def test_valid_parameters_with_integer_in_relations():
    result = parse_query(
        """ while w3;
            Select w3 such that Uses(20, w3)
           """
    )

    assert result[0]["such_thats"][0]["relations"][0]["parameters"][0] == 20
    assert result[0]["such_thats"][0]["relations"][0]["parameters"][1] == "w3"


def test_simply_with_left_query():
    result = parse_query(
        """
            while w3;
            Select w3 such that Uses(20, w3) with w3.varName = '_'
        """
    )

    assert len(result[0]["such_thats"][0]["withs"]) == 1
    assert result[0]["such_thats"][0]["withs"][0]["left"] == "w3"
    assert result[0]["such_thats"][0]["withs"][0]["attr_left"] == "varName"
    assert result[0]["such_thats"][0]["withs"][0]["right"] is Any
    assert result[0]["such_thats"][0]["withs"][0]["attr_right"] is None


def test_simply_with_query():
    result = parse_query(
        """
            while w3;
            Select w3 such that Uses(20, w3) with "x" = w3.varName
        """
    )

    assert len(result[0]["such_thats"][0]["withs"]) == 1
    assert result[0]["such_thats"][0]["withs"][0]["right"] == "w3"
    assert result[0]["such_thats"][0]["withs"][0]["attr_right"] == "varName"
    assert result[0]["such_thats"][0]["withs"][0]["left"] == '"x"'
    assert result[0]["such_thats"][0]["withs"][0]["attr_left"] is None


def test_multiply_with_query():
    result = parse_query(
        """
            while w3; stmt s2;
            Select w3 such that Uses(20, w3) with w3.varName = "x"
            and s2.varName = "boligrafo" and "pen" = s2.varName
        """
    )

    assert len(result[0]["such_thats"][0]["withs"]) == 3
    assert result[0]["such_thats"][0]["withs"][0]["left"] == "w3"
    assert result[0]["such_thats"][0]["withs"][0]["attr_left"] == "varName"
    assert result[0]["such_thats"][0]["withs"][0]["right"] == '"x"'
    assert result[0]["such_thats"][0]["withs"][0]["attr_right"] is None

    assert result[0]["such_thats"][0]["withs"][1]["left"] == "s2"
    assert result[0]["such_thats"][0]["withs"][1]["attr_left"] == "varName"
    assert result[0]["such_thats"][0]["withs"][1]["right"] == '"boligrafo"'
    assert result[0]["such_thats"][0]["withs"][1]["attr_right"] is None

    assert result[0]["such_thats"][0]["withs"][2]["left"] == '"pen"'
    assert result[0]["such_thats"][0]["withs"][2]["attr_left"] is None
    assert result[0]["such_thats"][0]["withs"][2]["right"] == "s2"
    assert result[0]["such_thats"][0]["withs"][2]["attr_right"] == "varName"


def test_not_valid_with_parameter_query():
    with pytest.raises(ValueError, match="Token '=' is not valid WITH_PARAMETER_TOKEN"):
        parse_query(
            """
            while w3; stmt s2;
            Select w3 such that Uses(20, w3) with w3.varName = =
            and s2.varName = "boligrafo" and "pen" = s2.varName

           """
        )


def test_not_valid_with_stmt():
    with pytest.raises(
        ValueError, match="Token 'attrNName' is not valid ATTR_NAME_TOKEN"
    ):
        parse_query(
            """
            while w3; stmt s2;
            Select w3 such that Uses(20, w3) with w3.attrNName = 30
            and s2.varName = "boligrafo" and "pen" = s2.varName

           """
        )
