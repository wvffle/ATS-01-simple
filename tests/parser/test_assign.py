import pytest

from ats.parser.parser import parse


def test_assign_restricted_keyword_as_var():
    for x in ["then", "else", "procedure"]:
        with pytest.raises(ValueError, match=f"Token '{x}' is a reserved keyword"):
            parse(f"procedure proc {{ {x} = 8; }}")
