from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
from ats.pql.pql import parse_query


def _get_ast_tree():
    return parse(
        """
            procedure test {
                if a then {
                    a = b + 3;
                    while a {
                        c = d + e;
                        while a {
                            c = d + e;
                        }
                    }
                } else {
                    a = b + 3;
                    while a {
                        c = d + e;
                        while a {
                            c = d + e;
                        }
                    }
                }
                while a {
                    c = d + e;
                    while a {
                        c = d + e;
                    }
                }
            }
            """
    )


tree = _get_ast_tree()


def test_pkb_parent_star_const_const():
    queries = parse_query("stmt s1; Select s1 such that Parent*(1, 6)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


def test_pkb_parent_star_stmt_const():
    queries = parse_query("stmt s1; Select s1 such that Parent*(s1, 11)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 8, 10]


def test_pkb_parent_star_stmt_const_1():
    queries = parse_query("assign a1; Select a1 such that Parent*(a1, 10)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == []


def test_pkb_parent_star_stmt_const_2():
    queries = parse_query("while w1; Select w1 such that Parent*(w1, 6)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [3, 5]


def test_pkb_parent_star_const_stmt():
    queries = parse_query("stmt s1; Select s1 such that Parent*(1, s1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


def test_pkb_parent_star_const_stmt_1():
    queries = parse_query("assign a1; Select a1 such that Parent*(1, a1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [2, 4, 6, 7, 9, 11]


def test_pkb_parent_star_const_stmt_2():
    queries = parse_query("while w1;  Select w1 such that Parent*(12, w1)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [14]


def test_pkb_parent_star_stmt_stmt():
    queries = parse_query("stmt s1, s2; Select s1 such that  Parent*(s1, s2)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [1, 3, 5, 8, 10, 12, 14]


def test_pkb_parent_star_stmt_stmt_1():
    queries = parse_query("if if; while w; Select w such that  Parent*(if, w)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == [3, 5, 8, 10]


def test_pkb_parent_star_stmt_stmt_2():
    queries = parse_query("if if; while w; Select if such that  Parent*(w, if)")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == []
