import sys

from ats.parser.parser import parse

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    if "--print-test-tree" in sys.argv:
        tree = parse(
            """
            procedure test {
                call test2;
                a = 8;
                b = 1;
                while a {
                    a = a + 1;
                }
                if b then {
                    a = b - 2;
                }
                else {
                    a = a * 3 * 2;
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
