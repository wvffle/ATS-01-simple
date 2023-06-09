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
            """
    )


tree = _get_ast_tree()


def test_pkb_uses_const_variable():
    queries = parse_query("""while w1; Select w1 such that Uses(1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == []


def test_pkb_uses_const_variable_1():
    queries = parse_query("""variable v1; Select v1 such that Uses(1, v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["b"]


def test_pkb_uses_const_variable_2():
    queries = parse_query("""while w1; Select w1 such that Uses(2, "x")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_uses_const_variable_3():
    queries = parse_query("""variable v1; Select v1 such that Uses(2, v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["a", "c", "d", "e", "f", "g", "x"]


def test_pkb_uses_const_variable_4():
    queries = parse_query("""variable v1; Select v1 such that Uses(12, v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["a", "b", "c", "d", "e", "f", "g", "x"]


def test_pkb_uses_assign_variable():
    queries = parse_query("""assign a1; Select a1 such that Uses(a1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [5, 9]


def test_pkb_uses_assign_variable_1():
    queries = parse_query("""assign a1; Select a1 such that Uses(a1, "c")""")
    result = evaluate_query(tree, queries[0])
    assert result == [3, 6, 10, 11]


def test_pkb_uses_while_variable():
    queries = parse_query("""while w1; Select w1 such that Uses(w1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 8, 12]


def test_pkb_uses_if_variable():
    queries = parse_query("""if i1; Select i1 such that Uses(i1, "f")""")
    result = evaluate_query(tree, queries[0])
    assert result == [4, 13]


def test_pkb_uses_statements_variable():
    queries = parse_query("""stmt s1; Select s1 such that Uses(s1, "c")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 3, 4, 6, 8, 10, 11, 12, 13, 14]


def test_pkb_uses_procedure_variable():
    queries = parse_query("""procedure p1; Select p1 such that Uses(p1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == ["test", "test2"]


def test_pkb_uses_procedure_variable_1():
    queries = parse_query("""procedure p1; Select p1 such that Uses(p1, "j")""")
    result = evaluate_query(tree, queries[0])
    assert result == ["test2"]


def test_pkb_uses_procedure_variable_2():
    queries = parse_query("""procedure p1; Select p1 such that Uses(p1, "q")""")
    result = evaluate_query(tree, queries[0])
    assert result == []


def _get_ast_tree_call():
    return parse(
        """
            procedure test1 {
                a = b;
                while a {
                    call test2;
                }
            }
            procedure test2 {
               call test3;
            }
            procedure test3 {
                c = d;
            }
            procedure test4 {
                e = f;
            }
            procedure test5 {
                call test4;
            }
            procedure test6 {
                call test5;
            }
            procedure test7 {
                call test8;
                call test9;
            }
            procedure test8 {
                call test7;
            }
            procedure test9 {
                call test8;
            }
            """
    )


tree_call = _get_ast_tree_call()


def test_pkb_uses_call_procedure_variable():
    queries = parse_query("""procedure p1; Select p1 such that Uses(p1, "d")""")
    result = evaluate_query(tree_call, queries[0])
    assert result == ["test1", "test2", "test3"]


def test_pkb_uses_call_procedure_variable_1():
    queries = parse_query("""procedure p1; Select p1 such that Uses(p1, "f")""")
    result = evaluate_query(tree_call, queries[0])
    assert result == ["test4", "test5", "test6"]


def test_pkb_uses_call_stmt_variable():
    queries = parse_query("""stmt s1; Select s1 such that Uses(s1, "d")""")
    result = evaluate_query(tree_call, queries[0])
    assert result == [2, 3, 4, 5]


def test_pkb_uses_call_stmt_variable_1():
    queries = parse_query("""stmt s1; Select s1 such that Uses(s1, "f")""")
    result = evaluate_query(tree_call, queries[0])
    assert result == [6, 7, 8]
