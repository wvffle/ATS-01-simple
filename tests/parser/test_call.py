import pytest

from ats.parser.parser import parse
from ats.parser.utils import RESTRICTED_TOKENS


def test_empty_call_no_proc_name():
    with pytest.raises(ValueError, match="Token ';' is not a valid NAME_TOKEN"):
        parse(
            """
            procedure proc {
                call;
            }
        """
        )


def test_call_restricted_keyword_as_var():
    for x in RESTRICTED_TOKENS:
        with pytest.raises(ValueError, match=f"Token '{x}' is a reserved keyword"):
            parse(f"procedure proc {{ call {x} }}")
