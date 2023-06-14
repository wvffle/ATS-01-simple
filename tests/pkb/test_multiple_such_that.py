from ats.parser.parser import parse
from ats.pkb.design_extractor import extract
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
context = extract(tree)


def test_pkb_follows_complex():
    queries = parse_query(
        """
        stmt s1;
        while w;
        assign a;
        Select s1 such that Follows(s1, a) and Parent(w, s1)
        """
    )
    result = evaluate_query(queries[0], context)
    assert result == [6]


def _get_ast_tree_call():
    return parse(
        """
            procedure First {
                x = 2;
                z = 3;
                call Second;
            }
            procedure Second {
                x = 0;
                i = 5;
                while i {
                    x = x + 2 * y;
                    call Third;
                    i = i - 1;
                }
                if x then {
                    x = x + 1;
                }
                else {
                    z = 1;
                }
                z = z + x + i;
                y = z + 2;
                x = x * y + z;
            }
            procedure Third {
                z = 5;
                v = z;
            }
            """
    )


tree_call = _get_ast_tree_call()
context_call = extract(tree_call)


def test_pkb_parent_and_uses():
    queries = parse_query(
        """
        while w1;
        assign a1;
        Select a1 such that Parent(w1, a1) and Uses(a1, "x")
        """
    )
    result = evaluate_query(queries[0], context_call)
    assert result == [7]


def test_pkb_parent_deep_and_uses():
    queries = parse_query(
        """
        while w1;
        assign a1;
        Select a1 such that Parent*(w1, a1) and Uses(a1, "i")
        """
    )
    result = evaluate_query(queries[0], context_call)
    assert result == [9]


def test_pkb_Next_deep_and_modifies():
    queries = parse_query(
        """
        stmt s1;
        Select s1 such that Next*(13, s1) and Modifies(s1, "x")
        """
    )
    result = evaluate_query(queries[0], context_call)
    assert result == [15]


def test_pkb_Next_deep_and_uses():
    queries = parse_query(
        """
        stmt s1;
        Select s1 such that Next*(13, s1) and Uses(s1, "z")
        """
    )
    result = evaluate_query(queries[0], context_call)
    assert result == [14, 15]


def test_pkb_next_and_modifies():
    queries = parse_query(
        """
        stmt s1;
        assign a1;
        Select s1 such that Next(a1, s1) and Modifies(s1, "z")
        """
    )
    result = evaluate_query(queries[0], context_call)
    assert result == [2, 3, 6, 8, 13]


def test_pkb_next_and_modifies_2():
    queries = parse_query(
        """
        assign a1, a2;
        Select a2 such that Next(a1, a2) and Modifies(a2, "z")
        """
    )
    result = evaluate_query(queries[0], context_call)
    assert result == [2, 13]


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
context2 = extract(tree2)


def test_pkb_modifies_follows():
    queries = parse_query(
        """assign a; while w; Select a such that Modifies(a, "a") and Follows(a, w)"""
    )
    result = evaluate_query(queries[0], context2)
    assert result == [1, 11]


def test_pkb_calls_uses():
    queries = parse_query(
        """procedure p; Select p such that Calls(p,"test") and Uses(p, "e")"""
    )
    result = evaluate_query(queries[0], context2)
    assert result == ["test2"]


def test_pkb_uses_modifies():
    queries = parse_query(
        """while w; Select w such that Uses(w, "e") and Modifies(w, "a")"""
    )
    result = evaluate_query(queries[0], context2)
    assert result == [2, 12]


def test_pkb_parent_modifies_next():
    queries = parse_query(
        """while w; assign a1, a2; Select a1 such that Parent(w, a1) and Modifies(a1, "c") and Next(a1, a2)"""
    )
    result = evaluate_query(queries[0], context2)
    assert result == [9]


def test_pkb_follows_parent_modifies():
    queries = parse_query(
        """procedure p; while w; if if; assign a; Select a such that Parent(w, if) and Follows(w, a) and Modifies(a, "i")"""
    )
    result = evaluate_query(queries[0], context2)
    assert result == [16]


def test_pkb_parent_parent():
    queries = parse_query(
        """stmt s; while w; assign a; Select s such that Parent(w, s) and Parent(s, a)"""
    )
    result = evaluate_query(queries[0], context2)
    assert result == [4, 13]


def test_pkb_next_modifies():
    queries = parse_query(
        """stmt s; assign a; Select a such that Next(a, s) and Modifies(a, "a")"""
    )
    result = evaluate_query(queries[0], context2)
    assert result == [3, 1, 11, 15]


def test_pkb_parent_modifies():
    queries = parse_query(
        """while w; if if; Select w such that Parent(w, if) and Modifies(w, "b")"""
    )
    result = evaluate_query(queries[0], context2)
    assert result == [2, 12]


def test_pkb_calls_parent():
    queries = parse_query(
        """procedure p; if if; while w; Select p such that Calls(p, "test") and Parent(if, w)"""
    )
    result = evaluate_query(queries[0], context2)
    assert result == []


def test_pkb_parent_next():
    queries = parse_query(
        """stmt s1, s2; assign a; Select s2 such that Parent(s1, s2) and Next(s2, a)"""
    )
    result = evaluate_query(queries[0], context2)
    assert result == [9, 4, 13]
