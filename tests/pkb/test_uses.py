from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
from ats.pql.pql import parse_pql


def _get_ast_tree():
    return parse(
        """
            procedure test {
                a = c + 8;
                while a {
                    if b then {
                        a = a + 2;
                    }
                    else {
                        a = c + 3;
                    }
                }
                b = 10;
                while a {
                    c = a + b;
                }
            }
            """
    )


def test_pkb_uses_const_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""while w1; Select w1 such that Uses(1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == []

    queries = parse_pql("""while w1; Select w1 such that Uses(2, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_uses_assign_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""assign a1; Select a1 such that Uses(a1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [4, 8]

    queries = parse_pql("""assign a1; Select a1 such that Uses(a1, "c")""")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 5]


def test_pkb_uses_while_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""while w1; Select w1 such that Uses(w1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 7]


def test_pkb_uses_statements_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""stmt s1; Select s1 such that Uses(s1, "c")""")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 2, 3, 5]


'''
def test_pkb_uses_if_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""if i1; Select i1 such that Uses(i1, "b")""")
    result = evaluate_query(tree, queries[0])
    assert result == [3]
'''
