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


def test_pkb_parent_and_uses():
    queries = parse_query(
        """
        while w1;
        assign a1;
        Select a1 such that Parent(w1, a1) and Uses(a1, "x")
        """
    )
    result = evaluate_query(tree_call, queries[0])
    assert result == [7]


def test_pkb_parent_deep_and_uses():
    queries = parse_query(
        """
        while w1;
        assign a1;
        Select a1 such that Parent*(w1, a1) and Uses(a1, "i")
        """
    )
    result = evaluate_query(tree_call, queries[0])
    assert result == [9]


def test_pkb_Next_deep_and_modifies():
    queries = parse_query(
        """
        stmt s1;
        Select s1 such that Next*(13, s1) and Modifies(s1, "x")
        """
    )
    result = evaluate_query(tree_call, queries[0])
    assert result == [15]


def test_pkb_Next_deep_and_uses():
    queries = parse_query(
        """
        stmt s1;
        Select s1 such that Next*(13, s1) and Uses(s1, "z")
        """
    )
    result = evaluate_query(tree_call, queries[0])
    assert result == [14, 15]


def test_pkb_next_and_modifies():
    queries = parse_query(
        """
        stmt s1;
        assign a1;
        Select s1 such that Next(a1, s1) and Modifies(s1, "z")
        """
    )
    result = evaluate_query(tree_call, queries[0])
    assert result == [2, 3, 6, 8, 13]


def test_pkb_next_and_modifies_2():
    queries = parse_query(
        """
        assign a1, a2;
        Select a2 such that Next(a1, a2) and Modifies(a2, "z")
        """
    )
    result = evaluate_query(tree_call, queries[0])
    assert result == [2, 13]
