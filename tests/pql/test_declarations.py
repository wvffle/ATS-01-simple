from ats.pql.pql import evaluate_query


def test_simple_stmt_declaration():
    evaluate_query(
        """ stmt s1;
            Select s1 such that Parent(s1, "x")
        """
    )
