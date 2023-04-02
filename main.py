from ats.parser.parser import parse
from ats.pkb.follows import follows

if __name__ == "__main__":
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
    follows.follows(tree)
    # parents.parents(tree)
