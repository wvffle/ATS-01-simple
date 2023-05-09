from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
from ats.pql.pql import parse_pql


def _get_ast_tree():
    return parse(
        """
            procedure test {
                a = 8;
                while a {
                    if b then {
                        a = a + 2;
                    }
                    else {
                        a = a + 3;
                    }

                }
                b = 10;
            }
            """
    )


def test_pkb_uses_assign_variable():
    tree = _get_ast_tree()
    queries = parse_pql("assign a1; Select a1 such that Uses(a1, a)")
    result = evaluate_query(tree, queries[0])
    assert result == [4, 5]


def test_pkb_uses_while_variable():
    tree = _get_ast_tree()
    queries = parse_pql("while w1; Select w1 such that Uses(w1, a)")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 4, 5]


def test_pkb_uses_if_variable():
    tree = _get_ast_tree()
    queries = parse_pql("if i1; Select i1 such that Uses(i1, b)")
    result = evaluate_query(tree, queries[0])
    assert result == [3]
