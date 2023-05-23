from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
from ats.pql.pql import parse_pql


def _get_ast_tree():
    return parse(
        """
            procedure test {
                a = b;
                while a {
                    a = c + d + g;
                    if e then {
                        a = a + e;
                    }
                    else {
                        a = f + c;
                    }
                }
                b = 10;
                while a {
                    c = a + b;
                    f = c;
                }
            }
            """
    )


def test_pkb_uses_const_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""while w1; Select w1 such that Uses(1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == []
    queries = parse_pql("""variable v1; Select v1 such that Uses(1, v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["b"]

    queries = parse_pql("""while w1; Select w1 such that Uses(2, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2]
    queries = parse_pql("""variable v1; Select v1 such that Uses(2, v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["a", "c", "d", "e", "f", "g"]


def test_pkb_uses_assign_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""assign a1; Select a1 such that Uses(a1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [5, 9]

    queries = parse_pql("""assign a1; Select a1 such that Uses(a1, "c")""")
    result = evaluate_query(tree, queries[0])
    assert result == [3, 6, 10]


def test_pkb_uses_while_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""while w1; Select w1 such that Uses(w1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 8]


def test_pkb_uses_if_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""if i1; Select i1 such that Uses(i1, "f")""")
    result = evaluate_query(tree, queries[0])
    assert result == [4]


def test_pkb_uses_statements_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""stmt s1; Select s1 such that Uses(s1, "c")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 3, 4, 6, 8, 10]


def test_pkb_uses_procedure_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""procedure p1; Select p1 such that Uses(p1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == ["test"]
    queries = parse_pql("""variable v1; Select v1 such that Uses("test", v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["a", "b", "c", "d", "e", "f", "g"]
