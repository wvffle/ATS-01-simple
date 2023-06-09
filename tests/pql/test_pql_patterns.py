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
