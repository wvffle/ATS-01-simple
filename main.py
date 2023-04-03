import sys

from ats.parser.parser import parse

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

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
