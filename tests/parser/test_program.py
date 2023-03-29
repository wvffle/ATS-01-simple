import pytest

from ats.parser.parser import parse


def test_empty_program():
    with pytest.raises(ValueError, match="Expected token 'procedure', got end of file"):
        parse("")
