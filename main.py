import sys

from ats.parser.parser import parse
from ats.pql.pql import evaluate_query

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    if "--print-test-tree" in sys.argv:
        tree = parse(
            """
            procedure test {
                a = 8;
                while a {
                    a = a + 1;
                }
                if b then {
                    a = a + 2;
                }
                else {
                    a = a + 3;
                }
            }
            """
        )

        tree.print_tree()

    elif len(sys.argv) > 0:
        with open(sys.argv[-1]) as f:
            code = f.read()
            tree = parse(code)
            print("Ready")

            query = input() + "\n" + input()

            # TODO: use PQL and PKB
            print("8")
