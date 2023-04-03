import pytest

from ats.pql.pql import evaluate_query


def test_simple_stmt_declaration():
    result = evaluate_query(
        """ stmt s1;
            Select s1 such that Parent(s1, "x")
        """
    )

    assert result[0]["variables"]["s1"] == "stmt"


def test_not_valid_end_of_declaration():
    with pytest.raises(
        ValueError, match="Token '/' is not a valid NAME_DECLARATION_TOKEN"
    ):
        evaluate_query(
            """ stmt s1; stmt s2/ stmt s3;
                Select s1 such that Parent(s1, "x")
            """
        )


def test_complex_stmt_declaration():
    result = evaluate_query(
        """ stmt s1; stmt s2; stmt s3;
            Select s1 such that Parent(s1, "x")
        """
    )

    assert result[0]["variables"]["s1"] == "stmt"
    assert result[0]["variables"]["s2"] == "stmt"
    assert result[0]["variables"]["s3"] == "stmt"


def test_simple_assign_declaration():
    result = evaluate_query(
        """ assign a1;
            Select a1 such that Parent(a1, "pen")
        """
    )

    assert result[0]["variables"]["a1"] == "assign"


def test_complex_assign_declaration():
    result = evaluate_query(
        """ assign a1; assign a2; assign a3;
            Select a2 such that Parent(a2, "ls")
        """
    )

    assert result[0]["variables"]["a1"] == "assign"
    assert result[0]["variables"]["a2"] == "assign"
    assert result[0]["variables"]["a3"] == "assign"


def test_simple_while_declaration():
    result = evaluate_query(
        """ while w1;
            Select w1 such that Parent(w1, "r2")
        """
    )

    assert result[0]["variables"]["w1"] == "while"


def test_complex_while_declaration():
    result = evaluate_query(
        """ while w1; while w2; while w3;
            Select w3 such that Parent(w3, "iusearchbtw")
        """
    )

    assert result[0]["variables"]["w1"] == "while"
    assert result[0]["variables"]["w2"] == "while"
    assert result[0]["variables"]["w3"] == "while"


def test_complex_stmt_declaration_short():
    result = evaluate_query(
        """ stmt s1, s2, s3;
            Select s1 such that Parent(s1, "x")
        """
    )

    assert result[0]["variables"]["s1"] == "stmt"
    assert result[0]["variables"]["s2"] == "stmt"
    assert result[0]["variables"]["s3"] == "stmt"


def test_complex_assign_declaration_short():
    result = evaluate_query(
        """ assign a1; assign a2; assign a3;
            Select a2 such that Parent(a2, "ls")
        """
    )

    assert result[0]["variables"]["a1"] == "assign"
    assert result[0]["variables"]["a2"] == "assign"
    assert result[0]["variables"]["a3"] == "assign"


def test_complex_while_declaration_short():
    result = evaluate_query(
        """ while w1, w2, w3;
            Select w3 such that Parent(w3, "iusearchbtw")
        """
    )

    assert result[0]["variables"]["w1"] == "while"
    assert result[0]["variables"]["w2"] == "while"
    assert result[0]["variables"]["w3"] == "while"


def test_complex_variuos_types_declaration():
    result = evaluate_query(
        """ while w1, w2, w3; stmt s1, s2, s3; assign a1, a2, a3;
            Select w3 such that Parent(w3, "iusearchbtw")
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
    with pytest.raises(
        ValueError, match="Token 'stmd' is not a valid VARIABLE_TYPE_TOKEN"
    ):
        evaluate_query(
            """ stmd s1;
                Select s1 such that Parent(s1, "x")
            """
        )


def test_multiple_type_error_declaration():
    with pytest.raises(
        ValueError, match="Token 'asinge' is not a valid VARIABLE_TYPE_TOKEN"
    ):
        evaluate_query(
            """ stmt s1; while w2; asinge a3;
                Select s1 such that Parent(s1, "x")
            """
        )


def test_varname_error_declaration():
    with pytest.raises(ValueError, match="Token '31' is not a valid NAME_TOKEN"):
        evaluate_query(
            """ stmt 31;
                Select s1 such that Parent(s1, "x")
            """
        )


def test_multiple_varname_error_declaration():
    with pytest.raises(ValueError, match="Token '35' is not a valid NAME_TOKEN"):
        evaluate_query(
            """ stmt s1, 35;
                Select s1 such that Parent(s1, "x")
            """
        )
