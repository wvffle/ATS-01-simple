import pytest

from ats.pql.pql import parse_pql


def test_simple_evaluator_query():
    parse_pql(
        """ stmt s1;
            Select s1 such that Parent(s1, "x")
        """
    )


def test_searching_variable():
    result = parse_pql(
        """ stmt s1;
            Select s1 such that Parent(s1, "x")
        """
    )

    assert result[0]["searching_variable"] == "s1"


def test_is_valid_searching_variable():
    result = parse_pql(
        """ stmt s1;
            Select s1 such that Parent(s1, "x")
        """
    )

    assert result[0]["searching_variable"] == "s1"


def test_not_valid_searching_variable():
    with pytest.raises(ValueError, match="Token 's4' is not declared"):
        parse_pql(
            """ stmt s1;
                Select s4 such that Parent(s1, "x")
           """
        )


def test_not_valid_select_statement():
    with pytest.raises(
        ValueError, match="Token 'Selekt' is not a valid VARIABLE_TYPE_TOKEN"
    ):
        parse_pql(
            """ stmt s1;
                Selekt s1 such that Parent(s1, "x")
           """
        )


def test_not_valid_such_statement():
    with pytest.raises(ValueError, match="Expected token 'such', got 'sum'"):
        parse_pql(
            """ stmt s1;
                Select s1 sum that Parent(s1, "x")
           """
        )


def test_not_valid_that_statement():
    with pytest.raises(ValueError, match="Expected token 'that', got 'dat'"):
        parse_pql(
            """ stmt s1;
                Select s1 such dat Parent(s1, "x")
           """
        )


def test_relation_parent_in_query():
    result = parse_pql(
        """ stmt s1;
            Select s1 such that Parent(s1, "x")
           """
    )

    assert result[0]["relation"] == "Parent"


def test_relation_parent_star_in_query():
    result = parse_pql(
        """ stmt s1;
            Select s1 such that Parent*(s1, "x")
           """
    )

    assert result[0]["relation"] == "Parent*"


def test_relation_follows_in_query():
    result = parse_pql(
        """ assign a2;
            Select a2 such that Follows(a2, "x")
           """
    )

    assert result[0]["relation"] == "Follows"


def test_relation_follows_star_in_query():
    result = parse_pql(
        """ assign a2;
            Select a2 such that Follows*(a2, "x")
           """
    )

    assert result[0]["relation"] == "Follows*"


def test_relation_modifies_in_query():
    result = parse_pql(
        """ assign a2;
            Select a2 such that Modifies(a2, "x")
           """
    )

    assert result[0]["relation"] == "Modifies"


def test_relation_uses_in_query():
    result = parse_pql(
        """ while w3;
            Select w3 such that Uses(w3, "x")
           """
    )

    assert result[0]["relation"] == "Uses"


def test_not_valid_relation_in_query():
    with pytest.raises(ValueError, match="Token 'Useless' is not a valid NAME_TOKEN"):
        parse_pql(
            """
            while w3;
            Select w3 such that Useless(w3, "x")
            """
        )


def test_valid_parameters_with_string_in_relations():
    result = parse_pql(
        """ while w3;
            Select w3 such that Uses(w3, "x")
           """
    )

    assert result[0]["parameters"][0] == "w3"
    assert result[0]["parameters"][1] == '"x"'


def test_valid_parameters_with_integer_in_relations():
    result = parse_pql(
        """ while w3;
            Select w3 such that Uses(20, w3)
           """
    )

    assert result[0]["parameters"][0] == "20"
    assert result[0]["parameters"][1] == "w3"


def test_not_valid_parameters_in_relations():
    with pytest.raises(ValueError, match="Variable 'xd1' is not declared"):
        parse_pql(
            """
            while w3;
            Select w3 such that Uses(xd1, w3)
            """
        )


def test_complex_query_evaluator():
    parse_pql(
        """
            while w3;
            Select w3 such that Uses(20, w3) with w3.atrrName = "x"
            """
    )


def test_simply_with_left_query():
    result = parse_pql(
        """
            while w3;
            Select w3 such that Uses(20, w3) with w3.atrrName = "x"
        """
    )

    assert len(result[0]["with"]) == 1
    assert result[0]["with"][0]["left"] == "w3"
    assert result[0]["with"][0]["attr_left"] == "atrrName"
    assert result[0]["with"][0]["right"] == '"x"'
    assert result[0]["with"][0]["attr_right"] is None


def test_simply_with_query():
    result = parse_pql(
        """
            while w3;
            Select w3 such that Uses(20, w3) with "x" = w3.atrrName
        """
    )

    assert len(result[0]["with"]) == 1
    assert result[0]["with"][0]["right"] == "w3"
    assert result[0]["with"][0]["attr_right"] == "atrrName"
    assert result[0]["with"][0]["left"] == '"x"'
    assert result[0]["with"][0]["attr_left"] is None


def test_multiply_with_query():
    result = parse_pql(
        """
            while w3; stmt s2;
            Select w3 such that Uses(20, w3) with w3.condition = "x"
            with s2.attrName = "boligrafo"
        """
    )

    assert len(result[0]["with"]) == 2
    assert result[0]["with"][0]["left"] == "w3"
    assert result[0]["with"][0]["attr_left"] == "condition"
    assert result[0]["with"][0]["right"] == '"x"'
    assert result[0]["with"][0]["attr_right"] is None
    assert result[0]["with"][1]["left"] == "s2"
    assert result[0]["with"][1]["attr_left"] == "attrName"
    assert result[0]["with"][1]["right"] == '"boligrafo"'
    assert result[0]["with"][1]["attr_right"] is None


def test_too_fast_end_of_query():
    with pytest.raises(ValueError, match="Expected VARTYPE_TOKEN, got end of file"):
        parse_pql(
            """

            """
        )


def test_query_result():
    result = parse_pql(
        """
            while w3; stmt s2;
            Select w3 such that Uses(20, w3) with w3.condition = "x"
            with s2.attrName = "boligrafo"

            """
    )

    assert result is not None


def test_multiply_select_query():
    parse_pql(
        """
            while w3; stmt s2;
            Select w3 such that Uses(20, w3) with w3.condition = "x"
            with s2.attrName = "boligrafo"
            assign a3;
            Select w3 such that Uses(a3, w3) with w3.condition = "x"
            with s2.attrName = "boligrafo"
            """
    )
