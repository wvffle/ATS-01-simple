import pytest

from ats.parser.parser import parse


def test_term_simple_const():
    parse(
        """
        procedure proc {
            test = 8;
        }
    """
    )


def test_term_const_times_const():
    parse(
        """
        procedure proc {
            test = 3 * 4;
        }
    """
    )


def test_term_const_times_const_times_const():
    parse(
        """
        procedure proc {
            test = 3 * 3 * 2;
        }
    """
    )


def test_term_const_times_var_times_const():
    parse(
        """
        procedure proc {
            test = 3 * a * 2;
        }
    """
    )


def test_term_var_times_const():
    parse(
        """
        procedure proc {
            test = a * 2;
        }
    """
    )


def test_term_var_times_var():
    parse(
        """
        procedure proc {
            test = a * b;
        }
    """
    )


def test_term_complex():
    term = "8" + " * 1" * 100

    parse(
        f"""
        procedure proc {{
            test = {term};
        }}
    """
    )


def test_term_times():
    parse(
        """
        procedure proc {
            test = a * b;
        }
    """
    )

    with pytest.raises(ValueError, match="Token ';' is not a valid INTEGER_TOKEN"):
        parse(
            """
            procedure proc {
                test = 1 *;
            }
        """
        )
