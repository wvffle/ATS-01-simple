from ats.parser.parser import parse
from ats.pkb.design_extractor import extract
from ats.pkb.query_evaluator import evaluate_query
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
context = extract(tree)


def test_pkb_boolean_with_condition():
    queries = parse_query(
        """
        variable v;
        procedure p;
        Select BOOLEAN with v.varName = p.procName
        """
    )
    result = evaluate_query(queries[0], context)
    assert result is False


def test_pkb_boolean_constant_with_condtition():
    queries = parse_query(
        """
        constant c1, c2;
        Select BOOLEAN with c1.value = c2.value and c2.value = 10
        """
    )
    result = evaluate_query(queries[0], context)
    assert result is False


def test_pkb_boolean_true_stmt_stmt():
    queries = parse_query("stmt s1, s2; Select BOOLEAN such that Follows(s1, s2)")
    result = evaluate_query(queries[0], context)
    assert result is True


def test_pkb_boolean_false_stmt_constant():
    queries = parse_query("stmt s1, s2; Select BOOLEAN such that Follows(s1, 1)")
    result = evaluate_query(queries[0], context)
    assert result is False


def test_pkb_boolean_true_proc_calls():
    queries = parse_query("""procedure p; Select BOOLEAN such that Calls(p, "test")""")
    result = evaluate_query(queries[0], context)
    assert result is True


def test_pkb_boolean_false_stmt_stmt_follows_with_condition():
    queries = parse_query(
        "stmt s1, s2; Select BOOLEAN such that Follows(s1, s2) with s1.stmt# = 1 and s2.stmt# = 3"
    )
    result = evaluate_query(queries[0], context)
    assert result is False


def test_pkb_boolean_true_while_uses():
    queries = parse_query("""while w; Select BOOLEAN such that Uses(w,"f")""")
    result = evaluate_query(queries[0], context)
    assert result is True


def test_pkb_boolean_false_while_uses_condition():
    queries = parse_query(
        """while w; variable v1; Select BOOLEAN such that Uses(w, v1) with v1.varName = "x" """
    )
    result = evaluate_query(queries[0], context)
    assert result is False


def test_pkb_boolean_true_assign_while_next():
    queries = parse_query("assign a; while w; Select BOOLEAN such that Next(a, w)")
    result = evaluate_query(queries[0], context)
    assert result is True


def test_pkb_boolean_false_while_while_next():
    queries = parse_query("while w1, w2; Select BOOLEAN such that Next(w1, w2)")
    result = evaluate_query(queries[0], context)
    assert result is False


def test_pkb_boolean_true():
    tree = parse(
        """
        procedure test1 {
            call test5;
        }
        procedure test3 {
            call test5;
        }
        procedure test5 {
            call test1;
        }
        """
    )
    queries = parse_query(
        """
        procedure p;
        Select BOOLEAN such that Calls ("test3", "test5")
        """
    )
    context = extract(tree)
    result = evaluate_query(queries[0], context)
    assert result is True
