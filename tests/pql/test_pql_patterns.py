import pytest

from ats.pql.pql import Any, parse_query


def test_basic_pattern():
    parse_query(
        """
        assign a2;
        Select a2 pattern a2(a2, _)
        """
    )


def test_assign_pattern_assert():
    result = parse_query(
        """
        assign a2;
        Select a2 pattern a2(a2, "x + y + 6")
        """
    )

    assert result[0]["conditions"]["patterns"][0]["variable"] == "a2"
    assert result[0]["conditions"]["patterns"][0]["type"] == "assign"
    assert result[0]["conditions"]["patterns"][0]["parameters"][0] == "a2"
    assert result[0]["conditions"]["patterns"][0]["parameters"][1] == '"x + y + 6"'


def test_if_pattern_assert():
    result = parse_query(
        """
        if i;
        Select i pattern i(i, _, _)
        """
    )

    assert result[0]["conditions"]["patterns"][0]["variable"] == "i"
    assert result[0]["conditions"]["patterns"][0]["type"] == "if"
    assert result[0]["conditions"]["patterns"][0]["parameters"][0] == "i"
    assert result[0]["conditions"]["patterns"][0]["parameters"][1] is Any
    assert result[0]["conditions"]["patterns"][0]["parameters"][2] is Any


def test_while_pattern_assert():
    result = parse_query(
        """
        while w3;
        Select w3 pattern w3(_, _)
        """
    )

    assert result[0]["conditions"]["patterns"][0]["variable"] == "w3"
    assert result[0]["conditions"]["patterns"][0]["type"] == "while"
    assert result[0]["conditions"]["patterns"][0]["parameters"][0] is Any
    assert result[0]["conditions"]["patterns"][0]["parameters"][1] is Any


def test_double_assign_pattern_assert():
    result = parse_query(
        """
        assign a1, a2;
        Select a2 pattern a2(a2, "x + y + 6") and a1(a1, _)
        """
    )

    assert result[0]["conditions"]["patterns"][0]["variable"] == "a2"
    assert result[0]["conditions"]["patterns"][0]["type"] == "assign"
    assert result[0]["conditions"]["patterns"][0]["parameters"][0] == "a2"
    assert result[0]["conditions"]["patterns"][0]["parameters"][1] == '"x + y + 6"'
    assert result[0]["conditions"]["patterns"][1]["variable"] == "a1"
    assert result[0]["conditions"]["patterns"][1]["type"] == "assign"
    assert result[0]["conditions"]["patterns"][1]["parameters"][0] == "a1"
    assert result[0]["conditions"]["patterns"][1]["parameters"][1] is Any


def test_triple_assign_pattern_assert():
    result = parse_query(
        """
        assign a1, a2, a3;
        Select a2 pattern a2(a2, "x + y + 6") and a1(a1, _) and a3(_, _)
        """
    )

    assert result[0]["conditions"]["patterns"][0]["variable"] == "a2"
    assert result[0]["conditions"]["patterns"][0]["type"] == "assign"
    assert result[0]["conditions"]["patterns"][0]["parameters"][0] == "a2"
    assert result[0]["conditions"]["patterns"][0]["parameters"][1] == '"x + y + 6"'

    assert result[0]["conditions"]["patterns"][1]["variable"] == "a1"
    assert result[0]["conditions"]["patterns"][1]["type"] == "assign"
    assert result[0]["conditions"]["patterns"][1]["parameters"][0] == "a1"
    assert result[0]["conditions"]["patterns"][1]["parameters"][1] is Any

    assert result[0]["conditions"]["patterns"][2]["variable"] == "a3"
    assert result[0]["conditions"]["patterns"][2]["type"] == "assign"
    assert result[0]["conditions"]["patterns"][2]["parameters"][0] is Any
    assert result[0]["conditions"]["patterns"][2]["parameters"][1] is Any


def test_double_while_pattern_assert():
    result = parse_query(
        """
        while w1, w2;
        Select w2 pattern w2(w2, _) and w1(_, _)
        """
    )

    assert result[0]["conditions"]["patterns"][0]["variable"] == "w2"
    assert result[0]["conditions"]["patterns"][0]["type"] == "while"
    assert result[0]["conditions"]["patterns"][0]["parameters"][0] == "w2"
    assert result[0]["conditions"]["patterns"][0]["parameters"][1] is Any
    assert result[0]["conditions"]["patterns"][1]["variable"] == "w1"
    assert result[0]["conditions"]["patterns"][1]["type"] == "while"
    assert result[0]["conditions"]["patterns"][1]["parameters"][0] is Any
    assert result[0]["conditions"]["patterns"][1]["parameters"][1] is Any


def test_triple_while_pattern_assert():
    result = parse_query(
        """
        while w1, w2, w3;
        Select w2 pattern w2(w2, _) and w1(w1, _) and w3(_, _)
        """
    )

    assert result[0]["conditions"]["patterns"][0]["variable"] == "w2"
    assert result[0]["conditions"]["patterns"][0]["type"] == "while"
    assert result[0]["conditions"]["patterns"][0]["parameters"][0] == "w2"
    assert result[0]["conditions"]["patterns"][0]["parameters"][1] is Any

    assert result[0]["conditions"]["patterns"][1]["variable"] == "w1"
    assert result[0]["conditions"]["patterns"][1]["type"] == "while"
    assert result[0]["conditions"]["patterns"][1]["parameters"][0] == "w1"
    assert result[0]["conditions"]["patterns"][1]["parameters"][1] is Any

    assert result[0]["conditions"]["patterns"][2]["variable"] == "w3"
    assert result[0]["conditions"]["patterns"][2]["type"] == "while"
    assert result[0]["conditions"]["patterns"][2]["parameters"][0] is Any
    assert result[0]["conditions"]["patterns"][2]["parameters"][1] is Any


def test_double_if_pattern_assert():
    result = parse_query(
        """
        if i1, i2;
        Select i2 pattern i2(i2, _, _) and i1(_, _, _)
        """
    )

    assert result[0]["conditions"]["patterns"][0]["variable"] == "i2"
    assert result[0]["conditions"]["patterns"][0]["type"] == "if"
    assert result[0]["conditions"]["patterns"][0]["parameters"][0] == "i2"
    assert result[0]["conditions"]["patterns"][0]["parameters"][1] is Any
    assert result[0]["conditions"]["patterns"][0]["parameters"][2] is Any
    assert result[0]["conditions"]["patterns"][1]["variable"] == "i1"
    assert result[0]["conditions"]["patterns"][1]["type"] == "if"
    assert result[0]["conditions"]["patterns"][1]["parameters"][0] is Any
    assert result[0]["conditions"]["patterns"][1]["parameters"][1] is Any
    assert result[0]["conditions"]["patterns"][1]["parameters"][2] is Any


def test_triple_if_pattern_assert():
    result = parse_query(
        """
        if i1, i2, i3;
        Select i2 pattern i2(i2, _, _) and i1(i1, _, _) and i3(_, _, _)
        """
    )

    assert result[0]["conditions"]["patterns"][0]["variable"] == "i2"
    assert result[0]["conditions"]["patterns"][0]["type"] == "if"
    assert result[0]["conditions"]["patterns"][0]["parameters"][0] == "i2"
    assert result[0]["conditions"]["patterns"][0]["parameters"][1] is Any
    assert result[0]["conditions"]["patterns"][0]["parameters"][2] is Any

    assert result[0]["conditions"]["patterns"][1]["variable"] == "i1"
    assert result[0]["conditions"]["patterns"][1]["type"] == "if"
    assert result[0]["conditions"]["patterns"][1]["parameters"][0] == "i1"
    assert result[0]["conditions"]["patterns"][1]["parameters"][1] is Any
    assert result[0]["conditions"]["patterns"][1]["parameters"][2] is Any

    assert result[0]["conditions"]["patterns"][2]["variable"] == "i3"
    assert result[0]["conditions"]["patterns"][2]["type"] == "if"
    assert result[0]["conditions"]["patterns"][2]["parameters"][0] is Any
    assert result[0]["conditions"]["patterns"][2]["parameters"][1] is Any
    assert result[0]["conditions"]["patterns"][2]["parameters"][2] is Any


def test_triple_different_patterns_assert():
    result = parse_query(
        """
            if i1; while w1; assign a1;
            Select a1 pattern i1(i1, _, _) and w1(_, _) and a1(a1, "x + x + x + x + x")
            """
    )

    assert result[0]["conditions"]["patterns"][0]["variable"] == "i1"
    assert result[0]["conditions"]["patterns"][0]["type"] == "if"
    assert result[0]["conditions"]["patterns"][0]["parameters"][0] == "i1"
    assert result[0]["conditions"]["patterns"][0]["parameters"][1] is Any
    assert result[0]["conditions"]["patterns"][0]["parameters"][2] is Any

    assert result[0]["conditions"]["patterns"][1]["variable"] == "w1"
    assert result[0]["conditions"]["patterns"][1]["type"] == "while"
    assert result[0]["conditions"]["patterns"][1]["parameters"][0] is Any
    assert result[0]["conditions"]["patterns"][1]["parameters"][1] is Any

    assert result[0]["conditions"]["patterns"][2]["variable"] == "a1"
    assert result[0]["conditions"]["patterns"][2]["type"] == "assign"
    assert result[0]["conditions"]["patterns"][2]["parameters"][0] == "a1"
    assert (
        result[0]["conditions"]["patterns"][2]["parameters"][1] == '"x + x + x + x + x"'
    )


def not_valid_var_ref_parameter():
    with pytest.raises(
        ValueError, match="Token '2' is not valid VAR_REF_TOKEN\non line: 2"
    ):
        parse_query(
            """
            assign a1;
            Select a1 pattern a1(2, a1)
            """
        )
