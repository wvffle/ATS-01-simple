from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
from ats.pql.pql import parse_pql


def _get_ast_tree():
    return parse(
        """
            procedure test {
                a = 1;
                b = 1;
                while a {
                    b = 1;
                    if a then {
                        a = 1;
                    }
                    else {
                        a = 1;
                    }
                }
                while a {
                    b = 1;
                }
                if a then {
                    b = 1;
                }
                else {
                    b = 1;
                }
            }
            """
    )


def test_pkb_modifies_assign_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""assign a1; Select a1 such that Modifies(a1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 6, 7]

    queries = parse_pql("""assign a1; Select a1 such that Modifies(a1, "b")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 4, 9, 11, 12]


def test_pkb_modifies_statement_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""stmt s1; Select s1 such that Modifies(s1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == [1, 3, 5]

    queries = parse_pql("""stmt s1; Select s1 such that Modifies(s1, "b")""")
    result = evaluate_query(tree, queries[0])
    assert result == [2, 3, 9, 11, 12]


'''
def test_pkb_modifies_procedure_variable():
    tree = _get_ast_tree()
    queries = parse_pql("""procedure p1; Select p1 such that Modifies(p1, "a")""")
    result = evaluate_query(tree, queries[0])
    assert result == ["test"]

    queries = parse_pql("""variable v1; Select v1 such that Modifies("test", v1)""")
    result = evaluate_query(tree, queries[0])
    assert result == ["a", "b"]
'''

# TODO:
# add to pql the ability to create queries with "procedure" and "variable"
