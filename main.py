import sys

from ats.ast.nodes import ProcedureNode, ProgramNode, StmtLstNode, StmtNode
from ats.parser.parser import parse
from ats.pkb.query_evaluator import evaluate_query
from ats.pql.pql import parse_query

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--print-test-tree" in sys.argv:
        tree = parse(
            """
            procedure test {
                a = 8 * (a + c) * 2;
            }

            procedure test2 {
                a = 8;
                if a then {
                    a = b + 3;
                }
                else {
                    c = d + e;
                    call test;
                    a = d + e;
                }

                while a {
                    a = a + 1;
                }
            }
            """
        )

        tree.print_tree(
            filter=lambda node: isinstance(
                node, (ProgramNode, ProcedureNode, StmtLstNode, StmtNode)
            )
        )

        queries = parse_query("""stmt s1, s2; Select s1 such that Follows(s1, s2)""")

        print(evaluate_query(tree, queries[0]))
        print(str(evaluate_query(tree, queries[0])))
        print(*evaluate_query(tree, queries[0]), sep=", ")
    elif len(sys.argv) > 0:
        with open(sys.argv[-1]) as f:
            code = f.read()
            tree = parse(code)
            # TODO: Extract design patterns here!
            print("Ready")

            query = input() + "\n" + input()

            # TODO: use PQL and PKB

            print(*evaluate_query(tree, query[0]), sep=", ")
