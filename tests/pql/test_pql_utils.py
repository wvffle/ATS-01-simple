import pytest

from ats.pql.utils import define_relationship


def test_invalid_relationship_param():
    with pytest.raises(ValueError) as e:
        define_relationship("invalid", "not valid", "maybe valid")

    assert (
        "Parameter 'not valid' at index 0 of the definition of relationship 'invalid' is not a valid design entity."
        in str(e.value)
    )


def test_invalid_relationship_param_2():
    with pytest.raises(ValueError) as e:
        define_relationship("invalid", "stmt", "maybe valid")

    assert (
        "Parameter 'maybe valid' at index 1 of the definition of relationship 'invalid' is not a valid design entity."
        in str(e.value)
    )
