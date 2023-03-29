import pytest

from ats.parser.parser import parse


def test_empty_procedure_no_name():
    with pytest.raises(ValueError, match="Token '{' is not a valid NAME_TOKEN"):
        parse("procedure {}")


def test_empty_procedure_no_brackets():
    with pytest.raises(ValueError, match="Expected token '{', got end of file"):
        parse("procedure proc")
