from ats.parser.parser import parse
from ats.pkb.query_evaluator import evaluate_query
from ats.pql.pql import parse_query


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


tree = _get_ast_tree()


def test_pkb_follows_complex():
    queries = parse_query(
        """
        stmt s1;
        while w;
        assign a;
        Select s1 such that Follows(s1, a) and Parent(w, s1)
        """
    )
    result = evaluate_query(tree, queries[0])
    assert result == [6]


def _get_ast_tree2():
    return parse(
        """
            procedure test {
                a = b;
                while a {
                    a = c + d + g;
                    if e then {
                        b = a + e;
                    }
                    else {
                        c = f + c;
                    }
                }
                b = 10;
                while a {
                    c = a + b;
                    f = c;
                }
            }
            procedure test2 {
                a = b + c;
                while d {
                    if e then {
                        call test;
                    }
                    else {
                        a = f;
                    }
                }
                i = j;
            }
        """
    )


tree2 = _get_ast_tree2()


def test_pkb_modifies_follows():
    queries = parse_query(
        """assign a; while w; Select a such that Modifies(a, "a") and Follows(a, w)"""
    )
    result = evaluate_query(tree2, queries[0])
    assert result == [1, 11]


def test_pkb_calls_uses():
    queries = parse_query(
        """procedure p; Select p such that Calls(p,"test") and Uses(p, "e")"""
    )
    result = evaluate_query(tree2, queries[0])
    assert result == ["test2"]


def test_pkb_uses_modifies():
    queries = parse_query(
        """while w; Select w such that Uses(w, "e") and Modifies(w, "a")"""
    )
    result = evaluate_query(tree2, queries[0])
    assert result == [2, 12]


def test_pkb_parent_modifies_next():
    queries = parse_query(
        """while w; assign a1, a2; Select a1 such that Parent(w, a1) and Modifies(a1, "c") and Next(a1, a2)"""
    )
    result = evaluate_query(tree2, queries[0])
    assert result == [9]


def test_pkb_follows_parent_modifies():
    queries = parse_query(
        """procedure p; while w; if if; assign a; Select a such that Parent(w, if) and Follows(w, a) and Modifies(a, "i")"""
    )
    result = evaluate_query(tree2, queries[0])
    assert result == [16]


def test_pkb_parent_parent():
    queries = parse_query(
        """stmt s; while w; assign a; Select s such that Parent(w, s) and Parent(s, a)"""
    )
    result = evaluate_query(tree2, queries[0])
    assert result == [4, 13]


def test_pkb_next_modifies():
    queries = parse_query(
        """stmt s; assign a; Select a such that Next(a, s) and Modifies(a, "a")"""
    )
    result = evaluate_query(tree2, queries[0])
    assert result == [3, 1, 11, 15]


def test_pkb_parent_modifies():
    queries = parse_query(
        """while w; if if; Select w such that Parent(w, if) and Modifies(w, "b")"""
    )
    result = evaluate_query(tree2, queries[0])
    assert result == [2, 12]


def test_pkb_calls_parent():
    queries = parse_query(
        """procedure p; if if; while w; Select p such that Calls(p, "test") and Parent(if, w)"""
    )
    result = evaluate_query(tree2, queries[0])
    assert result == []


def test_pkb_parent_next():
    queries = parse_query(
        """stmt s1, s2; assign a; Select s2 such that Parent(s1, s2) and Next(s2, a)"""
    )
    result = evaluate_query(tree2, queries[0])
    assert result == [9, 4, 13]
