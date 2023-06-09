from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
from ats.pql.pql import parse_query


def _get_ast_tree():
    return parse(
        """
            procedure test {
                a = 8;
                if a then {
                    a = b + 3;
                    a = b + 3;
                    a = b + 3;
                }
                else {
                    c = d + e;
                    c = d + e;
                }
                while a {
                    c = d + e;
                }
                while a {
                    c = d + e;
                }
            }
            """
    )


def test_pkb_follows_star_const_const():
    tree = _get_ast_tree()

    queries = parse_query("stmt s1; Select s1 such that Follows*(1, 10)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    queries = parse_query("stmt s1; Select s1 such that Follows*(5, 6)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == []


def test_pkb_follows_star_stmt_const():
    tree = _get_ast_tree()

    queries = parse_query("stmt s1; Select s1 such that Follows*(s1, 10)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 2, 8]

    queries = parse_query("assign a1; Select a1 such that Follows*(a1, 10)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1]

    queries = parse_query("assign a1; Select a1 such that Follows*(a1, 5)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [3, 4]


def test_pkb_follows_star_const_stmt():
    tree = _get_ast_tree()

    queries = parse_query("stmt s1; Select s1 such that Follows*(1, s1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [2, 8, 10]

    queries = parse_query("assign a1; Select a1 such that Follows*(3, a1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [4, 5]

    queries = parse_query("while w1;  Select w1 such that Follows*(1, w1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [8, 10]


def _get_ast_tree_2():
    return parse(
        """
            procedure test {
                a = 8;
                while a {
                    c = d + e;
                }
                a = 9;
                if a then {
                    a = b + 3;
                    a = b + 3;
                    a = b + 3;
                    a = b + 3;
                }
                else {
                    c = d + e;
                    c = d + e;
                }
                while a {
                    c = d + e;
                }
                while a {
                    c = d + e;
                }
            }
            """
    )


def test_pkb_follows_star_stmt_stmt():
    tree = _get_ast_tree_2()

    queries = parse_query("stmt s1, s2; Select s1 such that Follows*(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 2, 4, 5, 6, 7, 8, 10, 12]

    queries = parse_query("assign a1; while w1; Select a1 such that Follows*(a1, w1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 4]

    queries = parse_query("assign a1; while w1; Select w1 such that Follows*(a1, w1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [2, 12, 14]

    queries = parse_query("assign a1, a2; Select a1 such that Follows*(a1, a2)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 6, 7, 8, 10]
