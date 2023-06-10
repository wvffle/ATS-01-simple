import pytest

from ats.pql.pql import parse_query


def test_simple_stmt_declaration():
    result = parse_query(
        """
        stmt s1;
        Select s1 such that Follows(s1, 8)
        """
    )

    assert result[0]["variables"]["s1"] == "stmt"


def test_not_valid_end_of_declaration():
    with pytest.raises(
        ValueError, match="Token '/' is not a valid NAME_DECLARATION_TOKEN"
    ):
        parse_query(
            """ stmt s1; stmt s2/ stmt s3;
                Select s1 such that Follows*(s1, s2)
            """
        )


def test_complex_stmt_declaration():
    result = parse_query(
        """ stmt s1; stmt s2; stmt s3;
            Select s1 such that Follows(s1, 8)
        """
    )

    assert result[0]["variables"]["s1"] == "stmt"
    assert result[0]["variables"]["s2"] == "stmt"
    assert result[0]["variables"]["s3"] == "stmt"


def test_simple_assign_declaration():
    result = parse_query(
        """ assign a1;
            Select a1 such that Follows(a1, 2)
        """
    )

    assert result[0]["variables"]["a1"] == "assign"


def test_complex_assign_declaration():
    result = parse_query(
        """ assign a1; assign a2; assign a3;
            Select a2 such that Follows(a2, a1)
        """
    )

    assert result[0]["variables"]["a1"] == "assign"
    assert result[0]["variables"]["a2"] == "assign"
    assert result[0]["variables"]["a3"] == "assign"


def test_simple_while_declaration():
    result = parse_query(
        """ while w1;
            Select w1 such that Follows(w1, 2)
        """
    )

    assert result[0]["variables"]["w1"] == "while"


def test_complex_while_declaration():
    result = parse_query(
        """ while w1; while w2; while w3;
            Select w3 such that Follows(w1, w2)
        """
    )

    assert result[0]["variables"]["w1"] == "while"
    assert result[0]["variables"]["w2"] == "while"
    assert result[0]["variables"]["w3"] == "while"


def test_complex_stmt_declaration_short():
    result = parse_query(
        """ stmt s1, s2, s3;
            Select s1 such that Follows(s1, 8)
        """
    )

    assert result[0]["variables"]["s1"] == "stmt"
    assert result[0]["variables"]["s2"] == "stmt"
    assert result[0]["variables"]["s3"] == "stmt"


def test_complex_assign_declaration_short():
    result = parse_query(
        """ assign a1, a2, a3;
            Select a2 such that Parent(a3, a1)
        """
    )

    assert result[0]["variables"]["a1"] == "assign"
    assert result[0]["variables"]["a2"] == "assign"
    assert result[0]["variables"]["a3"] == "assign"


def test_complex_while_declaration_short():
    result = parse_query(
        """ while w1, w2, w3;
            Select w3 such that Parent(w2, w1)
        """
    )

    assert result[0]["variables"]["w1"] == "while"
    assert result[0]["variables"]["w2"] == "while"
    assert result[0]["variables"]["w3"] == "while"


def test_complex_variuos_types_declaration():
    result = parse_query(
        """ while w1, w2, w3;
            stmt s1, s2, s3;
            assign a1, a2, a3;
            Select a1 such that Follows(w3, s2)
        """
    )

    assert result[0]["variables"]["s1"] == "stmt"
    assert result[0]["variables"]["s2"] == "stmt"
    assert result[0]["variables"]["s3"] == "stmt"
    assert result[0]["variables"]["a1"] == "assign"
    assert result[0]["variables"]["a2"] == "assign"
    assert result[0]["variables"]["a3"] == "assign"
    assert result[0]["variables"]["w1"] == "while"
    assert result[0]["variables"]["w2"] == "while"
    assert result[0]["variables"]["w3"] == "while"


def test_type_error_declaration():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmd s1;
                Select s1 such that Uses(s1, "x")
            """
        )

    assert "Token 'stmd' is not a valid VARIABLE_TYPE_TOKEN" in str(e.value)


def test_multiple_type_error_declaration():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s1; while w2; asinge a3;
                Select s1 such that Calls(s1, "x")
            """
        )

    assert "Token 'asinge' is not a valid VARIABLE_TYPE_TOKEN" in str(e.value)


def test_varname_error_declaration():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt 31;
                Select s1 such that Calls*(s1, "x")
            """
        )

    assert "Token '31' is not a valid NAME_TOKEN" in str(e.value)


def test_multiple_varname_error_declaration():
    with pytest.raises(ValueError) as e:
        parse_query(
            """ stmt s1, 35;
                Select s1 such that Modifies(s1, "x")
            """
        )

    assert "Token '35' is not a valid NAME_TOKEN" in str(e.value)
