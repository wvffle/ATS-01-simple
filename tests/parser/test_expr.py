import pytest

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


def test_expr_const_plus_const_plus_const():
    parse(
        """
        procedure proc {
            test = 3 + 3 + 2;
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


def test_expr_var_plus_var():
    parse(
        """
        procedure proc {
            test = a + b;
        }
    """
    )


def test_expr_complex():
    expr = "8" + " + 1" * 100

    parse(
        f"""
        procedure proc {{
            test = {expr};
        }}
    """
    )


def test_expr_plus():
    parse(
        """
        procedure proc {
            test = a + b;
        }
    """
    )

    with pytest.raises(ValueError, match="Token ';' is not a valid INTEGER_TOKEN"):
        parse(
            """
            procedure proc {
                test = 1 +;
            }
        """
        )
