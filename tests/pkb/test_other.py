from ats.parser.parser import parse
from ats.pkb.design_extractor import extract
from ats.pkb.query_evaluator import evaluate_query
from ats.pql.pql import parse_query

tree = parse(
    """
    procedure proc {
        a = 8 + 1;
        a = a;
    }
    """
)


def test_assign():
    context = extract(tree)
    queries = parse_query("assign c; Select c")
    result = evaluate_query(queries[0], context)
    assert result == [1, 2]


def test_constants():
    context = extract(tree)
    queries = parse_query("constant c; Select c")
    result = evaluate_query(queries[0], context)
    assert sorted(result) == [1, 8]


def test_prog_line():
    context = extract(tree)
    queries = parse_query("prog_line c; Select c")
    result = evaluate_query(queries[0], context)
    assert sorted(result) == [1, 2]
