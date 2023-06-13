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


def test_pkb_follows_const_const():
    queries = parse_query("stmt s1; Select s1 such that Follows(1, 2)")
    result = evaluate_query(queries[0], context)
    assert result == [1, 2, 3, 4, 5, 6, 7]


def test_pkb_follows_const_const_1():
    queries = parse_query("stmt s1; Select s1 such that Follows(2, 1)")
    result = evaluate_query(queries[0], context)
    assert result == []


def test_pkb_follows_stmt_const():
    queries = parse_query("stmt s1; Select s1 such that Follows(s1, 2)")
    result = evaluate_query(queries[0], context)
    assert result == [1]


def test_pkb_follows_stmt_const_1():
    queries = parse_query("assign a1; Select a1 such that Follows(a1, 2)")
    result = evaluate_query(queries[0], context)
    assert result == [1]


def test_pkb_follows_stmt_const_2():
    queries = parse_query("while w1; Select w1 such that Follows(w1, 2)")
    result = evaluate_query(queries[0], context)
    assert result == []


def test_pkb_follows_const_stmt():
    queries = parse_query("stmt s1; Select s1 such that Follows(1, s1)")
    result = evaluate_query(queries[0], context)
    assert result == [2]


def test_pkb_follows_const_stmt_1():
    queries = parse_query("assign a1; Select a1 such that Follows(1, a1)")
    result = evaluate_query(queries[0], context)
    assert result == [2]


def test_pkb_follows_const_stmt_2():
    queries = parse_query("while w1; Select w1 such that Follows(1, w1)")
    result = evaluate_query(queries[0], context)
    assert result == []


def test_pkb_follows_stmt_stmt():
    queries = parse_query("stmt s1, s2; Select s1 such that Follows(s1, s2)")
    result = evaluate_query(queries[0], context)
    assert result == [1, 2, 3, 4, 6]


def test_pkb_follows_stmt_stmt_1():
    queries = parse_query("assign a1, a2; Select a1 such that Follows(a1, a2)")
    result = evaluate_query(queries[0], context)
    assert result == [1, 2, 3, 6]


def test_pkb_follows_stmt_stmt_2():
    queries = parse_query("assign a1, a2; Select a2 such that Follows(a1, a2)")
    result = evaluate_query(queries[0], context)
    assert result == [2, 3, 4, 7]


def test_pkb_follows_stmt_stmt_3():
    queries = parse_query("stmt s1, s2; Select s2 such that Follows(s1, s2)")
    result = evaluate_query(queries[0], context)
    assert result == [2, 3, 4, 5, 7]


def test_pkb_follows_stmt_stmt_4():
    queries = parse_query("stmt s1, s2, s3; Select s3 such that Follows(s1, s2)")
    result = evaluate_query(queries[0], context)
    assert result == [1, 2, 3, 4, 5, 6, 7]


def _get_ast_tree_if():
    return parse(
        """
            procedure proc {
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
                if b then {
                    a = a + 2;
                }
                else {
                    a = a + 3;
                }
                a = a + 1;
            }
            """
    )


tree_if = _get_ast_tree_if()
context_if = extract(tree_if)


def test_pkb_follows_stmt_stmt_if():
    queries = parse_query(
        "stmt s1; assign a1; if i1; Select s1 such that Follows(a1, i1)"
    )
    result = evaluate_query(queries[0], context_if)
    assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


def test_pkb_follows_stmt_stmt_if_1():
    queries = parse_query("assign a1; if i1; Select i1 such that Follows(i1, a1)")
    result = evaluate_query(queries[0], context_if)
    assert sorted(result) == [3, 8]


def test_pkb_follows_stmt_stmt_if_2():
    queries = parse_query("assign a1; if i1; Select i1 such that Follows(a1, i1)")
    result = evaluate_query(queries[0], context_if)
    assert sorted(result) == [8]


def test_pkb_follows_stmt_invalid_id_1():
    queries = parse_query("""stmt p; Select p such that Follows(p, 99999)""")
    result = evaluate_query(queries[0], context_if)
    assert sorted(result) == []


def test_pkb_boolean_follows_with_condition():
    queries = parse_query(
        """
        if i1, i2;
        Select BOOLEAN such that Follows* (i1, i2) with i2.stmt# = i1.stmt#
    """
    )

    result = evaluate_query(queries[0], context_if)
    assert result is False


def _get_ast_tree3():
    return parse(
        """
            procedure test {
                a = b;
                b = 10;
                while a {
                    x = 2 * a + b;
                    f = c;
                }
                while x {
                    if e then {
                        a = a;
                    } else {
                        a = f + c;
                    }
                    b = c + 3 * a;
                }
            }
            """
    )


tree3 = _get_ast_tree()


def test_pkb_follows_modifies():
    queries = parse_query(
        """stmt s1, s2; while w1; Select w1 such that
        Follows(s1, s2) and Modifies(s1, "a")"""
    )
    result = evaluate_query(tree3, queries[0])
    assert result == [5]


def test_pkb_follows_modifies_2():
    queries = parse_query(
        """stmt s1, s2; while w1; Select s1 such that
        Follows(s1, w1) and Modifies(w1, "a")"""
    )
    result = evaluate_query(tree3, queries[0])
    assert result == [4]


def test_pkb_follows_modifies_next():
    queries = parse_query(
        """stmt s1, s2; assign a1; Select s1 such that
        Follows(s1, s2) and Modifies(a1, "a") and Next(a1, 2)"""
    )
    result = evaluate_query(tree3, queries[0])
    assert result == [1, 2, 3, 4, 6]


def test_pkb_follows_modifies_next_2():
    queries = parse_query(
        """stmt s1, s2; assign a1; Select a1 such that
        Follows(1, s2) and Modifies(1, "c") and Next(a1, 2)"""
    )
    result = evaluate_query(tree3, queries[0])
    assert result == []


def test_pkb_follows_uses():
    queries = parse_query(
        """stmt s1, s2; while w1; Select s1 such that
        Follows(s1, w1) and Uses(w1, "a")"""
    )
    result = evaluate_query(tree3, queries[0])
    assert result == [4]


def test_pkb_follows_uses_2():
    queries = parse_query(
        """stmt s1, s2; assign a1; Select a1 such that
        Follows(a1, s1) and Uses(s1, "a")"""
    )
    result = evaluate_query(tree3, queries[0])
    assert result == [1, 2, 3, 4, 6]


def test_pkb_follows_uses_parent():
    queries = parse_query(
        """stmt s1, s2; while w1; Select s1 such that
        Follows(s1, s2) and Uses(w1, "a") and Parent(s2, s1)"""
    )
    result = evaluate_query(tree3, queries[0])
    assert result == [6]


def test_pkb_follows_uses_parent_2():
    queries = parse_query(
        """stmt s1, s2; while w1; Select w1 such that
        Follows(s1, s2) and Uses(w1, "a") and Parent(s1, s2)"""
    )
    result = evaluate_query(tree3, queries[0])
    assert result == [5]
