import sys

from ats.parser.parser import parse
from ats.pkb.pkb import evaluate_query
from ats.pql.pql import parse_pql

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    if "--print-test-tree" in sys.argv:
        tree = parse(
            """
            procedure test {
                a = 8;
                while a {
                if b then {
                    a = a + 2;
                }
                else {
                    a = a + 3;
                }
                    a = a + 1;
                }
            }
            """
        )

        tree.print_tree()
        queries = parse_pql("stmt s1, s2; Select s1 such that Follows(s1, s2)")
        evaluate_query(tree, queries[0])

    elif len(sys.argv) > 0:
        with open(sys.argv[-1]) as f:
            code = f.read()
            tree = parse(code)
            print("Ready")

            query = input() + "\n" + input()

            # TODO: use PQL and PKB
            print("8")
