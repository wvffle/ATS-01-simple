from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
from ats.pql.pql import parse_query


def _get_ast_tree():
    return parse(
        """
            procedure test {
                a = b;
                while x {
                    a = c + d + g;
                    if e then {
                        a = a;
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

            procedure test3 {
                a = a;
                call test3;
            }
            """
    )


def test_pkb_uses_const_variable():
    tree = _get_ast_tree()
    queries = parse_query("""while w1; Select w1 such that Uses(1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == []
    queries = parse_query("""variable v1; Select v1 such that Uses(1, v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["b"]

    queries = parse_query("""while w1; Select w1 such that Uses(2, "x")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2]
    queries = parse_query("""variable v1; Select v1 such that Uses(2, v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["a", "c", "d", "e", "f", "g", "x"]
    queries = parse_query("""variable v1; Select v1 such that Uses(12, v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["a", "b", "c", "d", "e", "f", "g", "x"]


def test_pkb_uses_assign_variable():
    tree = _get_ast_tree()
    queries = parse_query("""assign a1; Select a1 such that Uses(a1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [5, 9, 17]

    queries = parse_query("""assign a1; Select a1 such that Uses(a1, "c")""")
    result = evaluate_query(tree, queries[0])
    assert result == [3, 6, 10, 11]


def test_pkb_uses_while_variable():
    tree = _get_ast_tree()
    queries = parse_query("""while w1; Select w1 such that Uses(w1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 8, 12]


def test_pkb_uses_if_variable():
    tree = _get_ast_tree()
    queries = parse_query("""if i1; Select i1 such that Uses(i1, "f")""")
    result = evaluate_query(tree, queries[0])
    assert result == [4, 13]


def test_pkb_uses_statements_variable():
    tree = _get_ast_tree()
    queries = parse_query("""stmt s1; Select s1 such that Uses(s1, "c")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 3, 4, 6, 8, 10, 11, 12, 13, 14]


def test_pkb_uses_procedure_variable():
    tree = _get_ast_tree()
    queries = parse_query("""procedure p1; Select p1 such that Uses(p1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == ["test", "test2", "test3"]
    queries = parse_query("""procedure p1; Select p1 such that Uses(p1, "j")""")
    result = evaluate_query(tree, queries[0])
    assert result == ["test2"]
    queries = parse_query("""procedure p1; Select p1 such that Uses(p1, "q")""")
    result = evaluate_query(tree, queries[0])
    assert result == []
