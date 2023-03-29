import pytest

from ats_project_simple.parser import parse


def test_empty_program():
    with pytest.raises(ValueError):
        parse("")
