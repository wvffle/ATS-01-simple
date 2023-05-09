from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
from ats.pql.pql import parse_pql


def _get_ast_tree():
    return parse(
        """
            procedure proc {
                a = 1;
                a = 1;
                a = 1;
                a = 1;

                while a {
                    a = 1;
                    a = 1;
                }
            }
            """
    )


def test_pkb_follows_const_const():
    tree = _get_ast_tree()
    queries = parse_pql("stmt s1; Select s1 such that Follows(1, 2)")

    result = evaluate_query(tree, queries[0])
    assert result == [1, 2, 3, 4, 5, 6, 7]

    queries = parse_pql("stmt s1; Select s1 such that Follows(2, 1)")

    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_follows_stmt_const():
    tree = _get_ast_tree()
    queries = parse_pql("stmt s1; Select s1 such that Follows(s1, 2)")

    result = evaluate_query(tree, queries[0])
    assert result == [1]


def test_pkb_follows_const_stmt():
    tree = _get_ast_tree()
    queries = parse_pql("stmt s1; Select s1 such that Follows(1, s1)")

    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_follows_const_assign():
    tree = _get_ast_tree()
    queries = parse_pql("assign a1; Select a1 such that Follows(1, a1)")

    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_follows_const_while():
    tree = _get_ast_tree()
    queries = parse_pql("while w1; Select w1 such that Follows(1, w1)")

    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_follows_stmt_stmt():
    tree = _get_ast_tree()
    queries = parse_pql("stmt s1, s2; Select s1 such that Follows(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 2, 3, 4, 6]

    queries = parse_pql("assign a1, a2; Select a1 such that Follows(a1, a2)")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 2, 3, 6]

    queries = parse_pql("stmt s1, s2; Select s2 such that Follows(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 3, 4, 5, 7]

    queries = parse_pql("stmt s1, s2, s3; Select s3 such that Follows(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 2, 3, 4, 6]
