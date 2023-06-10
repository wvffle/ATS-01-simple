import pytest

from ats.pql.pql import parse_query


def test_simple_evaluator_query():
    parse_query(
        """ stmt s1;
            Select s1 such that Modifies(s1, "x")
        """
    )


def test_searching_variable():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Uses(s1, "x")
        """
    )

    assert result[0]["searching_variable"] == "s1"


def test_is_valid_searching_variable():
    result = parse_query(
        """ stmt s1;
            Select s1 such that Calls(s1, "x")
        """
    )

    assert result[0]["searching_variable"] == "s1"


def test_not_valid_searching_variable():
    with pytest.raises(ValueError, match="Token 's4' is not declared"):
        parse_query(
            """ stmt s1;
                Select s4 such that Calls*(s1, "x")
           """
        )


def test_not_valid_select_statement():
    with pytest.raises(
        ValueError, match="Token 'Selekt' is not a valid VARIABLE_TYPE_TOKEN"
    ):
        parse_query(
            """ stmt s1;
                Selekt s1 such that Modifies(s1, "x")
           """
        )


def test_not_valid_that_statement():
    with pytest.raises(ValueError, match="Expected token 'that', got 'dat'"):
        parse_query(
            """ stmt s1;
                Select s1 such dat Calls(s1, "x")
           """
        )


def test_not_valid_relation_in_query():
    with pytest.raises(ValueError, match="Token 'Useless' is not a valid NAME_TOKEN"):
        parse_query(
            """
            while w3;
            Select w3 such that Useless(w3, "x")
            """
        )


def test_complex_query_evaluator():
    parse_query(
        """
            while w3; procedure p1;
            Select w3 such that Uses(20, w3) with p1.procName = "xDDD"
        """
    )


def test_too_fast_end_of_query():
    with pytest.raises(ValueError, match="Expected VARTYPE_TOKEN, got end of file"):
        parse_query(
            """
            """
        )


def test_query_result():
    result = parse_query(
        """
            while w3; stmt s2; variable v1; procedure p1;
            Select w3 such that Uses(20, w3) with v1.varName = "best"
            and p1.procName = "boligrafo"
        """
    )

    assert result is not None


def test_multiply_relations_select_query():
    parse_query(
        """
            while w3; stmt s2;
            Select w3 such that Uses(20, w3) and Modifies(20, w3) and Follows(w3, s2)
            assign a3;
            Select w3 such that Uses(a3, w3) and Calls*("not", "me")
            """
    )


def test_multiply_relations_select_query_values():
    result = parse_query(
        """
            while w3; stmt s2;
            Select w3 such that Uses(20, w3) and Modifies(20, w3) and Follows*(w3, s2)
            assign a3;
            Select w3 such that Uses(a3, w3) and Calls*("not", "me")
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Uses"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Modifies"
    assert result[0]["conditions"]["relations"][2]["relation"] == "Follows*"
    assert result[1]["conditions"]["relations"][0]["relation"] == "Uses"
    assert result[1]["conditions"]["relations"][1]["relation"] == "Calls*"


def test_multiply_relations_parameters_select_query_values():
    result = parse_query(
        """
            while w3; stmt s2;
            Select w3 such that Uses(20, w3) and Modifies(20, w3) and Follows*(w3, s2)
            assign a3;
            Select w3 such that Uses(a3, w3) and Calls*("not", "me")
            """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] == 20
    assert result[0]["conditions"]["relations"][0]["parameters"][1] == "w3"

    assert result[0]["conditions"]["relations"][1]["parameters"][0] == 20
    assert result[0]["conditions"]["relations"][1]["parameters"][1] == "w3"

    assert result[0]["conditions"]["relations"][2]["parameters"][0] == "w3"
    assert result[0]["conditions"]["relations"][2]["parameters"][1] == "s2"

    assert result[1]["conditions"]["relations"][0]["parameters"][0] == "a3"
    assert result[1]["conditions"]["relations"][0]["parameters"][1] == "w3"

    assert result[1]["conditions"]["relations"][1]["parameters"][0] == '"not"'
    assert result[1]["conditions"]["relations"][1]["parameters"][1] == '"me"'


def test_multiply_relations_and_multiply_with_select_query():
    parse_query(
        """
            while w3; stmt s2, s3; variable v1;
            Select w3 such that Uses(20, w3) and Modifies(20, w3) and Follows(w3, s2)
            with s2.stmt# = "xdd" and v1.varName = "boligrafo"
            assign a3;
            Select w3 such that Uses(a3, w3) and Calls*("not", "me") with s3.stmt# = "x"
            and v1.varName = "boligrafo"
        """
    )


def test_multiply_relations_and_multiply_with_select_query_values():
    parse_query(
        """
            while w3; stmt s2; procedure p1; variable v1;
            Select w3 such that Uses(20, w3) and Modifies(20, w3) and Follows(w3, s2)
            with p1.procName = "allow" and s2.stmt# = "boligrafo"
            assign a3;
            Select w3 such that Uses(a3, w3) and Calls*("not", "me") with v1.varName = "y"
            and s2.stmt# = "boligrafo"
        """
    )


def test_multiply_relations_and_multiply_patterns_and_with():
    result = parse_query(
        """
                while w3; variable v1; assign a3;
                Select w3 such that Parent(10, 20) and Modifies(_, _) pattern a3(a3, "x + y + z") with v1.varName = "y"
            """
    )

    assert result[0]["conditions"]["relations"][0]["relation"] == "Parent"
    assert result[0]["conditions"]["relations"][1]["relation"] == "Modifies"
    assert result[0]["conditions"]["patterns"][0]["variable"] == "a3"
    assert result[0]["conditions"]["patterns"][0]["type"] == "assign"
    assert result[0]["conditions"]["patterns"][0]["parameters"][0] == "a3"
    assert result[0]["conditions"]["patterns"][0]["parameters"][1] == '"x + y + z"'
    assert result[0]["conditions"]["attributes"][0]["left"] == "v1"
    assert result[0]["conditions"]["attributes"][0]["attr_left"] == "varName"
    assert result[0]["conditions"]["attributes"][0]["right"] == '"y"'
