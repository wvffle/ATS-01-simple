from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
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
                call test1;
            }

            procedure test5 {
                call test5;
            }

            procedure test6 {
                a = a;
            }
            """
    )


tree = _get_ast_tree()


def test_pkb_calls_procedure_any():
    queries = parse_query("""procedure p; Select p such that Calls(p, '_')""")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == ["test1", "test2", "test3", "test4"]


def test_pkb_calls_procedure_any_1():
    queries = parse_query("""procedure q; Select q such that Calls('_', q)""")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == ["test1", "test2", "test3", "test4", "test5"]


def test_pkb_calls_procedure_procedure():
    queries = parse_query("""procedure p, q; Select p such that Calls(p, q)""")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == ["test1", "test2", "test3", "test4"]


def test_pkb_calls_procedure_procedure_1():
    queries = parse_query("""procedure p, q; Select q such that Calls(p, q)""")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == ["test1", "test2", "test3", "test4", "test5"]


def test_pkb_calls_procedure_name_procedure():
    queries = parse_query("""procedure p; Select p such that Calls (p, "test5")""")
    result = evaluate_query(tree, queries[0])
    assert result == ["test3"]


def test_pkb_calls_procedure_name_procedure_1():
    queries = parse_query("""procedure q; Select q such that Calls ("test1", q)""")
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == ["test2", "test4"]


def test_pkb_calls_procedure_name_name():
    queries = parse_query(
        """procedure p; Select p such that Calls ("test3", "test5")"""
    )
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == ["test1", "test2", "test3", "test4", "test5", "test6"]


def test_pkb_calls_procedure_name_name_1():
    queries = parse_query(
        """procedure p; Select p such that Calls ("test4", "test5")"""
    )
    result = evaluate_query(tree, queries[0])
    assert sorted(result) == []
