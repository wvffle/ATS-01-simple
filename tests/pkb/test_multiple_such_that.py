from ats.parser.parser import parse
from ats.pkb.query_evaluator import evaluate_query
from ats.pql.pql import parse_query


def _get_ast_tree():
    return parse(
        """
            procedure proc {
                a = 1;
                a = 1;
                a = 1;
                a = 1;

                while a {
                    a = 1;
                    a = 1;
                }
            }
            """
    )


tree = _get_ast_tree()


def test_pkb_follows_complex():
    queries = parse_query(
        """
        stmt s1;
        while w;
        assign a;
        Select s1 such that Follows(s1, a) and Parent(w, s1)
        """
    )
    result = evaluate_query(tree, queries[0])
    assert result == [6]
