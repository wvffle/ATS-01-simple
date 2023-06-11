# Note this file is for Boolean queries that are not implemented yet
# from ats.parser.parser import parse
# from ats.pkb.pkb import evaluate_query
# from ats.pql.pql import parse_query


# def _get_ast_tree():
#     return parse(
#         """
#             procedure test {
#                 a = b;
#                 while a {
#                     a = c + d + g;
#                     if e then {
#                         b = a + e;
#                     }
#                     else {
#                         c = f + c;
#                     }
#                 }
#                 b = 10;
#                 while a {
#                     c = a + b;
#                     f = c;
#                 }
#             }
#             procedure test2 {
#                 a = b + c;
#                 while d {
#                     if e then {
#                         call test;
#                     }
#                     else {
#                         a = f;
#                     }
#                 }
#                 i = j;
#             }
#             """
#     )


# tree = _get_ast_tree()

# def test_pkb_boolean_with_condition():
#     queries = parse_query("""variable v; procedure p; Select BOOLEAN with v.varName = p.procName """)
#     result = evaluate_query(tree, queries[0])
#     assert result == False


# def test_pkb_boolean_constant_with_condtition():
#     queries = parse_query("""constant c1, c2 Select BOOLEAN with c1.value = c2.value and c2.value = 10 """)
#     result = evaluate_query(tree, queries[0])
#     assert result == False
