from ats_project_simple.parser.parser import parse

if __name__ == "__main__":
    parse(
        """
        procedure test {
            a = 8;
            while a {
                a = a + 1;
                a = a + 1;
                a = a + 1;
                a = a + 1;
                a = a + 1;
            }
        }
        """
    )

    print("All OK")
