from ats.parser.parser import parse
from ats.pkb.query_evaluator import evaluate_query
from ats.pql.pql import parse_query


def _get_ast_tree():
    return parse(
        """
            procedure test1 {
                call test2;
                call test4;
            }
            procedure test2 {
                call test3;
            }
            procedure test3 {
                call test5;
            }
            procedure test4 {
                call test6;
            }
            procedure test5 {
                call test6;
            }
            procedure test6 {
                a = a;
            }
            """
    )


tree = _get_ast_tree()


def test_pkb_calls_star_name_name():
    queries = parse_query(
        """procedure p, q; Select p such that Calls* ("test2", "test5")"""
    )
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == ["test1", "test2", "test3", "test4", "test5", "test6"]


def test_pkb_calls_star_name_name_1():
    queries = parse_query(
        """procedure p, q; Select p such that Calls* ("test6", "test1")"""
    )
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == []


def test_pkb_calls_star_procedure_name():
    queries = parse_query("""procedure p, q; Select p such that Calls* (p, "test5")""")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == ["test1", "test2", "test3"]


def test_pkb_calls_star_name_procedure():
    queries = parse_query("""procedure q; Select q such that Calls* ("test1", q)""")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == ["test2", "test3", "test4", "test5", "test6"]


def test_pkb_calls_star_name_procedure_1():
    queries = parse_query("""procedure q; Select q such that Calls* ("test2", q)""")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == ["test3", "test5", "test6"]


def _get_ast_tree2():
    return parse(
        """
            procedure test1 {
                call test2;
            }
            procedure test2 {
                call test3;
            }
            procedure test3 {
                call test5;
            }
            procedure test4 {
                call test6;
            }
            procedure test5 {
                call test7;
            }
            procedure test6 {
                a = a;
            }
            procedure test7 {
                a = b;
            }
            """
    )


tree2 = _get_ast_tree2()


def test_pkb_calls_procedure_procedure_2():
    queries = parse_query("""procedure p, q; Select p such that Calls(p, q)""")
    result = evaluate_query(tree2, queries[0])
    assert sorted(result) == ["test1", "test2", "test3", "test4", "test5"]


def test_pkb_calls_procedure_procedure_3():
    queries = parse_query("""procedure p, q; Select q such that Calls(p, q)""")
    result = evaluate_query(tree2, queries[0])
    assert sorted(result) == ["test2", "test3", "test5", "test6", "test7"]


def _get_ast_tree3():
    return parse(
        """
            procedure test1 {
                a = a + 3;
            }
            procedure test2 {
                a = b + c;
                call test1;
            }
            """
    )


tree3 = _get_ast_tree3()


def test_pkb_calls_star_name_name_3():
    queries = parse_query(
        """procedure p, q; Select p such that Calls* ("test1", "test2")"""
    )
    result = evaluate_query(tree3, queries[0])
    assert sorted(result) == []
