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


def test_pkb_parent_const_const():
    tree = _get_ast_tree()
    queries = parse_pql("assign a1; Select a1 such that Uses(a1, a)")
    result = evaluate_query(tree, queries[0])
    assert result == [4, 5]
