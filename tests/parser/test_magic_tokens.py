from ats.parser.utils import is_integer_token, is_name_token


def test_name_token():
    assert is_name_token("n")
    assert is_name_token("name")
    assert is_name_token("n4")
    assert is_name_token("n4m3")

    assert not is_name_token("1n4m3")
    assert not is_name_token("1")
    assert not is_name_token("-")
    assert not is_name_token("na-me")
    assert not is_name_token("na_me")
    assert not is_name_token("name#")


def test_integer_token():
    assert is_integer_token("1")
    assert is_integer_token("666")
    assert is_integer_token("123231")

    assert not is_integer_token("n")
    assert not is_integer_token("name")
    assert not is_integer_token("n4")
    assert not is_integer_token("n4m3")
    assert not is_integer_token("1n4m3")
    assert not is_integer_token("-")
    assert not is_integer_token("na-me")
    assert not is_integer_token("na_me")
    assert not is_integer_token("name#")
