import pytest

from ats.pql.pql import parse_query


def test_valid_parameters_with_string_in_relations():
    result = parse_query(
        """ while w3; variable v1;
            Select w3 such that Uses(w3, v1)
           """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] == "w3"
    assert result[0]["conditions"]["relations"][0]["parameters"][1] == "v1"


def test_valid_parameters_with_integer_in_relations():
    result = parse_query(
        """ while w3; variable v1;
            Select w3 such that Uses(20, v1)
           """
    )

    assert result[0]["conditions"]["relations"][0]["parameters"][0] == 20
    assert result[0]["conditions"]["relations"][0]["parameters"][1] == "v1"


# def test_simply_with_left_query():
#     result = parse_query(
#         """
#             while w3; variable v1;
#             Select w3 such that Uses(20, v1) with v1.varName = _
#         """
#     )
#
#     assert len(result[0]["conditions"]["attributes"]) == 1
#     assert result[0]["conditions"]["attributes"][0]["left"] == "v1"
#     assert result[0]["conditions"]["attributes"][0]["attr_left"] == "varName"
#     assert result[0]["conditions"]["attributes"][0]["right"] is Any
#     assert result[0]["conditions"]["attributes"][0]["attr_right"] is None
#
#
# def test_simply_with_query():
#     result = parse_query(
#         """
#             while w3; stmt s2; variable v1;
#             Select w3 such that Uses(20, v1) with "x" = s2.stmt#
#         """
#     )
#
#     assert len(result[0]["conditions"]["attributes"]) == 1
#     assert result[0]["conditions"]["attributes"][0]["right"] == "s2"
#     assert result[0]["conditions"]["attributes"][0]["attr_right"] == "stmt#"
#     assert result[0]["conditions"]["attributes"][0]["left"] == '"x"'
#     assert result[0]["conditions"]["attributes"][0]["attr_left"] is None
#
#
# def test_multiply_with_query():
#     result = parse_query(
#         """
#             while w3; stmt s2; procedure p1; variable v1;
#             Select w3 such that Uses(20, v1) with s2.stmt# = "x"
#             and v1.varName = "boligrafo" and "pen" = p1.procName
#         """
#     )
#
#     assert len(result[0]["conditions"]["attributes"]) == 3
#     assert result[0]["conditions"]["attributes"][0]["left"] == "s2"
#     assert result[0]["conditions"]["attributes"][0]["attr_left"] == "stmt#"
#     assert result[0]["conditions"]["attributes"][0]["right"] == '"x"'
#     assert result[0]["conditions"]["attributes"][0]["attr_right"] is None
#
#     assert result[0]["conditions"]["attributes"][1]["left"] == "v1"
#     assert result[0]["conditions"]["attributes"][1]["attr_left"] == "varName"
#     assert result[0]["conditions"]["attributes"][1]["right"] == '"boligrafo"'
#     assert result[0]["conditions"]["attributes"][1]["attr_right"] is None
#
#     assert result[0]["conditions"]["attributes"][2]["left"] == '"pen"'
#     assert result[0]["conditions"]["attributes"][2]["attr_left"] is None
#     assert result[0]["conditions"]["attributes"][2]["right"] == "p1"
#     assert result[0]["conditions"]["attributes"][2]["attr_right"] == "procName"


def test_not_valid_with_parameter_query():
    with pytest.raises(ValueError) as e:
        parse_query(
            """
            while w3; stmt s2; variable v1;
            Select w3 such that Uses(20, v1) with s2.stmt# = =
            and v1.varName = "boligrafo" and "pen" = s2.stmt#

           """
        )

    assert "Token '=' is not valid WITH_PARAMETER_TOKEN" in str(e.value)


def test_not_valid_with_stmt():
    with pytest.raises(ValueError) as e:
        parse_query(
            """
            while w3; stmt s2; variable v1;
            Select w3 such that Uses(20, v1) with w3.attrNName = 30
            and s2.varName = "boligrafo" and "pen" = s2.varName

           """
        )

    assert "Token 'attrNName' is not valid ATTR_NAME_TOKEN" in str(e.value)


def test_not_valid_with_statement_attr():
    with pytest.raises(ValueError) as e:
        parse_query(
            """
            while w3; stmt s2; variable v1;
            Select w3 such that Uses(20, v1) with w3.stmt# = 30
            and s2.varName = "boligrafo" and "pen" = s2.varName

           """
        )

    assert "Statement 's2' does not have attribute 'varName'" in str(e.value)


def test_not_valid_with_call_attr():
    with pytest.raises(ValueError) as e:
        parse_query(
            """
            while w3; stmt s2; call c1; variable v1;
            Select w3 such that Uses(20, v1) with c1.varName = 30
            and s2.varName = "boligrafo" and "pen" = s2.varName

           """
        )

    assert "Call 'c1' does not have attribute 'varName'" in str(e.value)


def test_not_valid_with_procedure_attr():
    with pytest.raises(ValueError) as e:
        parse_query(
            """
            while w3; stmt s2; call c1; procedure p1; variable v1;
            Select w3 such that Uses(p1, v1) with p1.varName = 30
            and s2.varName = "boligrafo" and "pen" = s2.varName

           """
        )

    assert "Procedure 'p1' does not have attribute 'varName'" in str(e.value)


def test_not_valid_with_variable_attr():
    with pytest.raises(ValueError) as e:
        parse_query(
            """
            while w3; stmt s2; call c1; procedure p1; variable v1;
            Select w3 such that Uses(20, v1) with s2.stmt# = "xD"
            and v1.procName = "wow"

           """
        )

    assert "Variable 'v1' does not have attribute 'procName'" in str(e.value)


def test_not_valid_constant_attr():
    with pytest.raises(ValueError) as e:
        parse_query(
            """
            while w3; stmt s2; call c1; procedure p1; variable v1; constant const;
            Select w3 such that Uses(20, v1) with const.stmt# = "xD"
            and v1.procName = "wow"
           """
        )

    assert "Constant 'const' does not have attribute 'stmt#'" in str(e.value)


def test_not_valid_with_procedure_attr_2():
    with pytest.raises(ValueError) as e:
        parse_query(
            """
            while w3; stmt s2; call c1; prog_line pl; variable v1;
            Select w3 such that Next(pl, 5) with pl.varName = 30
            and s2.varName = "boligrafo" and "pen" = s2.varName

           """
        )

    assert """The prog_line 'pl' does not have attribute 'varName'""" in str(e.value)
