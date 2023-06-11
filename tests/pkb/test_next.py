from ats.parser.parser import parse
from ats.pkb.query_evaluator import evaluate_query
from ats.pql.pql import parse_query


def _get_ast_tree():
    return parse(
        """
            procedure test {
                a = a;
                while a {
                    if a then {
                        a = a;
                        a = a;
                    }
                    else {
                        if a then {
                            a = a;
                        }
                        else {
                            while a {
                                a = a;
                            }
                        }
                    }
                }
                call test2;
            }
            procedure test2 {
                while a {
                    a = a;
                }
            }
        """
    )


def test_pkb_next_const_const_1():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(1, 2)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


def test_pkb_next_const_const_2():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(8, 2)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


def test_pkb_next_const_const_3():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(5, 6)")
    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_next_const_const_4():
    tree = _get_ast_tree()
    queries = parse_query("assign a1; Select a1 such that Next(1, 2)")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 4, 5, 7, 9, 12]


def test_pkb_next_const_stmt_1():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(1, s1)")
    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_next_const_stmt_2():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(4, s1)")
    result = evaluate_query(tree, queries[0])
    assert result == [5]


def test_pkb_next_const_stmt_3():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(5, s1)")
    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_next_const_stmt_4():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(8, s1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [2, 9]


def test_pkb_next_const_stmt_5():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(12, s1)")
    result = evaluate_query(tree, queries[0])
    assert result == [11]


def test_pkb_next_const_stmt_6():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(10, s1)")
    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_next_const_while_1():
    tree = _get_ast_tree()
    queries = parse_query("while w1; Select w1 such that Next(5, w1)")
    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_next_const_while_2():
    tree = _get_ast_tree()
    queries = parse_query("while w1; Select w1 such that Next(6, w1)")
    result = evaluate_query(tree, queries[0])
    assert result == [8]


def test_pkb_next_stmt_const_1():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(s1, 2)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 5, 7, 8]


def test_pkb_next_stmt_const_2():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(s1, 8)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [6, 9]


def test_pkb_next_stmt_const_3():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(s1, 10)")
    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_next_stmt_const_4():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1; Select s1 such that Next(s1, 12)")
    result = evaluate_query(tree, queries[0])
    assert result == [11]


def test_pkb_next_if_const_1():
    tree = _get_ast_tree()
    queries = parse_query("if i1; Select i1 such that Next(i1, 4)")
    result = evaluate_query(tree, queries[0])
    assert result == [3]


def test_pkb_next_stmt_stmt_1():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1, s2; Select s1 such that Next(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12]


def test_pkb_next_stmt_stmt_2():
    tree = _get_ast_tree()
    queries = parse_query("stmt s1, s2; Select s2 such that Next(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


def test_pkb_next_if_while_1():
    tree = _get_ast_tree()
    queries = parse_query("if i1; while w1; Select i1 such that Next(i1, w1)")
    result = evaluate_query(tree, queries[0])
    assert result == [6]


def test_pkb_next_if_while_2():
    tree = _get_ast_tree()
    queries = parse_query("if i1; while w1; Select w1 such that Next(i1, w1)")
    result = evaluate_query(tree, queries[0])
    assert result == [8]


def test_pkb_next_assign_while_1():
    tree = _get_ast_tree()
    queries = parse_query("assign a1; while w1; Select a1 such that Next(a1, w1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 5, 7, 9, 12]


def test_pkb_next_assign_while_2():
    tree = _get_ast_tree()
    queries = parse_query("assign a1; while w1; Select w1 such that Next(a1, w1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [2, 8, 11]
