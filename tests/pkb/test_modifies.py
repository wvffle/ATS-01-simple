from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
from ats.pql.pql import parse_query


def _get_ast_tree():
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


tree = _get_ast_tree()


def test_pkb_modifies_const_variable():
    queries = parse_query("""while w1; Select w1 such that Modifies(1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [1]


def test_pkb_modifies_const_variable_1():
    queries = parse_query("""variable v1; Select v1 such that Modifies(1, v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["a"]


def test_pkb_modifies_const_variable_2():
    queries = parse_query("""while w1; Select w1 such that Modifies(2, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2]


def test_pkb_modifies_const_variable_3():
    queries = parse_query("""variable v1; Select v1 such that Modifies(2, v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["a", "b", "c"]


def test_pkb_modifies_assign_variable():
    queries = parse_query("""assign a1; Select a1 such that Modifies(a1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 3, 11, 15]


def test_pkb_modifies_assign_variable_1():
    queries = parse_query("""assign a1; Select a1 such that Modifies(a1, "c")""")
    result = evaluate_query(tree, queries[0])
    assert result == [6, 9]


def test_pkb_modifies_while_variable():
    queries = parse_query("""while w1; Select w1 such that Modifies(w1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 12]


def test_pkb_modifies_if_variable():
    queries = parse_query("""if i1; Select i1 such that Modifies(i1, "c")""")
    result = evaluate_query(tree, queries[0])
    assert result == [4, 13]


def test_pkb_modifies_if_variable_1():
    queries = parse_query("""if i1; Select i1 such that Modifies(i1, "f")""")
    result = evaluate_query(tree, queries[0])
    assert result == [13]


def test_pkb_modifies_statements_variable():
    queries = parse_query("""stmt s1; Select s1 such that Modifies(s1, "c")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 4, 6, 8, 9, 12, 13, 14]


def test_pkb_modifies_procedure_variable():
    queries = parse_query("""procedure p1; Select p1 such that Modifies(p1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == ["test", "test2"]


def test_pkb_modifies_procedure_variable_1():
    queries = parse_query("""procedure p1; Select p1 such that Modifies(p1, "i")""")
    result = evaluate_query(tree, queries[0])
    assert result == ["test2"]


def test_pkb_modifies_procedure_variable_2():
    queries = parse_query("""procedure p1; Select p1 such that Modifies(p1, "q")""")
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


def test_pkb_modifies_call_procedure_variable():
    queries = parse_query("""procedure p1; Select p1 such that Modifies(p1, "c")""")
    result = evaluate_query(tree_call, queries[0])
    assert result == ["test1", "test2", "test3"]


def test_pkb_modifies_call_procedure_variable_1():
    queries = parse_query("""procedure p1; Select p1 such that Modifies(p1, "e")""")
    result = evaluate_query(tree_call, queries[0])
    assert result == ["test4", "test5", "test6"]


def test_pkb_modifies_call_stmt_variable():
    queries = parse_query("""stmt s1; Select s1 such that Modifies(s1, "c")""")
    result = evaluate_query(tree_call, queries[0])
    assert result == [2, 3, 4, 5]


def test_pkb_modifies_call_stmt_variable_1():
    queries = parse_query("""stmt s1; Select s1 such that Modifies(s1, "e")""")
    result = evaluate_query(tree_call, queries[0])
    assert result == [6, 7, 8]
