import sys
from threading import Timer

from ats.ast.nodes import ProcedureNode, ProgramNode, StmtLstNode, StmtNode
from ats.parser.parser import parse
from ats.pkb.design_extractor import extract
from ats.pkb.query_evaluator import evaluate_query
from ats.pql.pql import parse_query

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # nie powinno być ibm852?
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

        queries = parse_query(
            # """stmt s1; while w1; Select BOOLEAN such that Follows(s1, w1)"""
            """
            procedure p, q;
            Select BOOLEAN such that Calls(_, _)
            """
        )
        context = extract(tree)
        print(evaluate_query(queries[0], context))

    elif len(sys.argv) > 0:  # pragma no cover

        def no_time_left():
            print("\nPreparationTimeout")
            exit(1)

        with open(sys.argv[-1]) as f:
            code = f.read()
            tree = parse(code)
            context = extract(tree)
            print("Ready")
            while True:
                try:
                    t = Timer(60, no_time_left)
                    t.start()
                    query = input() + "\n" + input()
                    t.cancel()

                    queries = parse_query(query)
                    result = evaluate_query(queries[0], context)

                    if isinstance(result, bool):
                        print("true" if result else "false")
                        continue

                    if len(result) == 0:
                        print("none")
                        continue

                    print(", ".join(str(part) for part in result))

                except Exception:
                    import traceback

                    exc_info = traceback.format_exc().replace("\n", "    ")
                    print("#" + exc_info)
