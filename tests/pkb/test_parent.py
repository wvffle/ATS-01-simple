from ats.parser.parser import parse
from ats.pkb.query_evaluator import evaluate_query
from ats.pql.pql import parse_query


def _get_ast_tree():
    return parse(
        """
            procedure test {
                a = 8;
                while a {
                    if b then {
                        a = a + 2;
                    } else {
                        a = a + 3;
                    }
                    a = a + 1;
                }
                b = 10;
            }
            """
    )


tree = _get_ast_tree()


def test_pkb_parent_const_const():
    queries = parse_query("stmt s1; Select s1 such that Parent(2, 3)")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 2, 3, 4, 5, 6, 7]


def test_pkb_parent_const_stmt():
    queries = parse_query("stmt s1; Select s1 such that Parent(2, s1)")
    result = evaluate_query(tree, queries[0])
    assert result == [3, 6]


def test_pkb_parent_const_stmt_2():
    queries = parse_query("assign a1; Select a1 such that Parent(1, a1)")
    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_parent_const_stmt_3():
    queries = parse_query("if if1; Select if1 such that Parent(2, if1)")
    result = evaluate_query(tree, queries[0])
    assert result == [3]


def test_pkb_parent_stmt_const():
    queries = parse_query("stmt s1; Select s1 such that Parent(s1, 3)")
    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_parent_stmt_const_2():
    queries = parse_query("assign a1; Select a1 such that Parent(a1, 2)")
    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_parent_stmt_const_3():
    queries = parse_query("while w1; Select w1 such that Parent(w1, 3)")
    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_parent_stmt_stmt():
    queries = parse_query("stmt s1, s2; Select s1 such that Parent(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 3]


def test_pkb_parent_stmt_stmt_1():
    queries = parse_query("assign a1, a2; Select a2 such that Parent(a1, a2)")
    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_parent_stmt_stmt_2():
    queries = parse_query("assign a1, a2; Select a1 such that Parent(a1, a2)")
    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_parent_stmt_stmt_3():
    queries = parse_query("stmt s1, s2; Select s2 such that Parent(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert result == [3, 4, 5, 6]


def test_pkb_parent_stmt_stmt_5():
    queries = parse_query("stmt s1, s2, s3; Select s3 such that Parent(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 2, 3, 4, 5, 6, 7]


# def test_pkb_parent_stmt_using_with_stmt_hash():
#     queries = parse_query(
#         """
#         stmt s1, s2;
#         Select s1 such that Parent(s1, s2) with s2.stmt# = 4
#         """
#     )
#     result = evaluate_query(tree, queries[0])
#     assert sorted(result) == [3]
