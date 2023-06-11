from ats.parser.parser import parse
from ats.pkb.query_evaluator import evaluate_query
from ats.pql.pql import parse_query


def _get_ast_tree():
    return parse(
        """
            procedure test {
                a = a;
                a = a;
                if a then {
                    a = a;
                    a = a;
                }
                else {
                    while a {
                        a = a;
                        a = a;
                    }
                    a = a;
                }
                while a {
                    if a then {
                        a = a;
                    }
                    else {
                        a = a;
                    }
                }
                a = a;
            }
        """
    )


def test_pkb_next_star_const_const_1():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next*(2, 8)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]


def test_pkb_next_star_const_const_2():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next*(4, 6)")
    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_next_star_const_const_3():
    tree = _get_ast_tree()
    queries = parse_query("while w1; Select w1 such that Next*(5, 10)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [6, 10]


def test_pkb_next_star_const_const_4():
    tree = _get_ast_tree()
    queries = parse_query("if i1; Select i1 such that Next*(9, 14)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [3, 11]


def test_pkb_next_star_const_stmt_1():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next*(1, s1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]


def test_pkb_next_star_const_stmt_2():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next*(4, s1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [5, 10, 11, 12, 13, 14]


def test_pkb_next_star_const_stmt_3():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next*(8, s1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [6, 7, 8, 9, 10, 11, 12, 13, 14]


def test_pkb_next_star_const_stmt_4():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next*(13, s1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [10, 11, 12, 13, 14]


def test_pkb_next_star_const_stmt_5():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next*(14, s1)")
    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_next_star_stmt_const_1():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next*(s1, 1)")
    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_next_star_stmt_const_2():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next*(s1, 14)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]


def test_pkb_next_star_stmt_const_3():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next*(s1, 9)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 2, 3, 6, 7, 8]


def test_pkb_next_star_stmt_stmt_1():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1, s2; Select s1 such that Next*(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]


def test_pkb_next_star_stmt_stmt_2():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1, s2; Select s2 such that Next*(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]


def test_pkb_next_star_while_assign_1():
    tree = _get_ast_tree()
    queries = parse_query("while w1; assign a1; Select w1 such that Next*(w1, a1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [6, 10]


def test_pkb_next_star_while_assign_2():
    tree = _get_ast_tree()
    queries = parse_query("while w1; assign a1; Select a1 such that Next*(w1, a1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [7, 8, 9, 12, 13, 14]
