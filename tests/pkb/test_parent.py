from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
from ats.pql.pql import parse_pql


def _get_ast_tree():
    return parse(
        """
            procedure test {
                a = 8;
                while a {
                    if b then {
                        a = a + 2;
                    }
                    else {
                        a = a + 3;
                    }
                    a = a + 1;
                }
                b = 10;
            }
            """
    )


def test_pkb_parent_const_const():
    tree = _get_ast_tree()
    queries = parse_pql("stmt s1; Select s1 such that Parent(2, 3)")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 2, 3, 4, 5, 6, 7]


def test_pkb_parent_const_stmt():
    tree = _get_ast_tree()
    queries = parse_pql("stmt s1; Select s1 such that Parent(2, s1)")

    result = evaluate_query(tree, queries[0])
    assert result == [3, 6]


def test_pkb_parent_stmt_const():
    tree = _get_ast_tree()
    queries = parse_pql("stmt s1; Select s1 such that Parent(s1, 3)")

    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_parent_stmt_stmt():
    tree = _get_ast_tree()
    queries = parse_pql("stmt s1, s2; Select s1 such that Parent(s1, s2)")

    result = evaluate_query(tree, queries[0])
    assert result == [2, 3, 3, 2]


"""
def test_pkb_parent_follows():
    tree = _get_ast_tree()
    queries = parse_pql("stmt s1; Select s1 such that Parent(2, 3) and Follows(1, 2)")

    result = evaluate_query(tree, queries[0])
    assert result == [1, 2, 3, 4, 5, 6, 7]
"""
