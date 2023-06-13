from ats.parser.parser import parse
from ats.pkb.design_extractor import extract
from ats.pkb.query_evaluator import evaluate_query
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
                } else {
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


tree = _get_ast_tree()
context = extract(tree)


def test_pkb_follows_star_const_const():
    queries = parse_query("stmt s1; Select s1 such that Follows*(1, 10)")
    result = evaluate_query(queries[0], context)
    assert sorted(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


def test_pkb_follows_star_const_const_1():
    queries = parse_query("stmt s1; Select s1 such that Follows*(5, 6)")
    result = evaluate_query(queries[0], context)
    assert sorted(result) == []


def test_pkb_follows_star_stmt_const():
    queries = parse_query("stmt s1; Select s1 such that Follows*(s1, 10)")
    result = evaluate_query(queries[0], context)
    assert sorted(result) == [1, 2, 8]


def test_pkb_follows_star_stmt_const_1():
    queries = parse_query("assign a1; Select a1 such that Follows*(a1, 10)")
    result = evaluate_query(queries[0], context)
    assert sorted(result) == [1]


def test_pkb_follows_star_stmt_const_2():
    queries = parse_query("assign a1; Select a1 such that Follows*(a1, 5)")
    result = evaluate_query(queries[0], context)
    assert sorted(result) == [3, 4]


def test_pkb_follows_star_const_stmt():
    queries = parse_query("stmt s1; Select s1 such that Follows*(1, s1)")
    result = evaluate_query(queries[0], context)
    assert sorted(result) == [2, 8, 10]


def test_pkb_follows_star_const_stmt_1():
    queries = parse_query("assign a1; Select a1 such that Follows*(3, a1)")
    result = evaluate_query(queries[0], context)
    assert sorted(result) == [4, 5]


def test_pkb_follows_star_const_stmt_2():
    queries = parse_query("while w1;  Select w1 such that Follows*(1, w1)")
    result = evaluate_query(queries[0], context)
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
                } else {
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


tree2 = _get_ast_tree_2()
context2 = extract(tree2)


def test_pkb_follows_star_stmt_stmt():
    queries = parse_query("stmt s1, s2; Select s1 such that Follows*(s1, s2)")
    result = evaluate_query(queries[0], context2)
    assert sorted(result) == [1, 2, 4, 5, 6, 7, 8, 10, 12]


def test_pkb_follows_star_stmt_stmt_1():
    queries = parse_query("assign a1; while w1; Select w1 such that Follows*(a1, w1)")
    result = evaluate_query(queries[0], context2)
    assert sorted(result) == [2, 12, 14]


def test_pkb_follows_star_stmt_stmt_2():
    queries = parse_query("assign a1, a2; Select a1 such that Follows*(a1, a2)")
    result = evaluate_query(queries[0], context2)
    assert sorted(result) == [1, 6, 7, 8, 10]


def test_pkb_follows_star_stmt_stmt_3():
    queries = parse_query("assign a1; while w1; Select a1 such that Follows*(a1, w1)")
    result = evaluate_query(queries[0], context2)
    assert sorted(result) == [1, 4]


def test_pkb_follows_star_stmt_stmt_4():
    queries = parse_query("while w1, w2; Select w1 such that Follows*(w2, w1)")
    result = evaluate_query(queries[0], context2)
    assert sorted(result) == [12, 14]


def test_pkb_follows_star_stmt_stmt_5():
    queries = parse_query("while w1, w2; Select w1 such that Follows*(w1, w2)")
    result = evaluate_query(queries[0], context2)
    assert sorted(result) == [2, 12]


def test_pkb_follows_star_stmt_stmt_6():
    queries = parse_query("assign a1, a2; Select a1 such that Follows*(a2, a1)")
    result = evaluate_query(queries[0], context2)
    assert sorted(result) == [4, 7, 8, 9, 11]


def test_pkb_follows_star_stmt_stmt_7():
    queries = parse_query(
        "assign a1, a2; while w1; Select w1 such that Follows*(a2, a1)"
    )
    result = evaluate_query(queries[0], context2)
    assert sorted(result) == [2, 12, 14]


def test_pkb_follows_follows_star_1():
    queries = parse_query(
        "stmt s1, s2; Select s1 such that Follows(1, s1) and Follows*(s1, s2)"
    )
    result = evaluate_query(queries[0], context2)
    assert sorted(result) == [2]


def test_pkb_follows_star_parent_1():
    queries = parse_query(
        "stmt s1, s2; Select s1 such that Follows*(1, s1) and Parent(2, s2)"
    )
    result = evaluate_query(queries[0], context2)
    assert sorted(result) == [2, 4, 5, 12, 14]
