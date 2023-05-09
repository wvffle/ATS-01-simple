from ats.parser.parser import parse


def test_expr_simple_const():
    parse(
        """
        procedure proc {
            test = 8;
        }
    """
    )


def test_expr_const_plus_const():
    parse(
        """
        procedure proc {
            test = 4 + 4;
        }
    """
    )


def test_expr_const_minus_const():
    parse(
        """
        procedure proc {
            test = 4 - 4;
        }
    """
    )


def test_expr_const_plus_const_plus_const():
    parse(
        """
        procedure proc {
            test = 3 + 3 + 2;
        }
    """
    )


def test_expr_const_minus_const_plus_const():
    parse(
        """
        procedure proc {
            test = 3 - 3 - 2;
        }
    """
    )


def test_expr_var_plus_const():
    parse(
        """
        procedure proc {
            test = a + 2;
        }
    """
    )


def test_expr_var_minus_const():
    parse(
        """
        procedure proc {
            test = a - 2;
        }
    """
    )


def test_expr_var_plus_var():
    parse(
        """
        procedure proc {
            test = a + b;
        }
    """
    )


def test_expr_var_minus_var():
    parse(
        """
        procedure proc {
            test = a - b;
        }
    """
    )


def test_expr_const_plus_var():
    parse(
        """
        procedure proc {
            test = 2 + b;
        }
    """
    )


def test_expr_const_minus_var():
    parse(
        """
        procedure proc {
            test = 2 - b;
        }
    """
    )


def test_expr_complex():
    expr = "8" + " + 1 - 1" * 100

    parse(
        f"""
        procedure proc {{
            test = {expr};
        }}
    """
    )
