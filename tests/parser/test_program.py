import pytest

from ats.parser.parser import parse


def test_empty_program():
    with pytest.raises(ValueError, match="Expected token 'procedure', got end of file"):
        parse("")


def test_program_expects_procedure():
    with pytest.raises(ValueError, match="Expected token 'procedure', got 'test'"):
        parse("test")


def test_program_dummy_procedure():
    parse("procedure test { dummy = 8; }")


def test_program_multiple_procedures():
    parse(
        """
        procedure test1 { dummy = 8; }
        procedure test2 { dummy = 8; }
    """
    )


def test_program_end_of_file():
    with pytest.raises(ValueError, match="Expected end of file, got 'a'"):
        parse(
            """
            procedure test1 { dummy = 8; }
            a = 2;
        """
        )
