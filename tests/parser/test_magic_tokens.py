from ats.parser.utils import is_integer_token, is_name_token


def test_name_token():
    assert is_name_token("n")


def test_name_token_1():
    assert is_name_token("name")


def test_name_token_2():
    assert is_name_token("n4")


def test_name_token_3():
    assert is_name_token("n4m3")


def test_name_token_4():
    assert not is_name_token("1n4m3")


def test_name_token_5():
    assert not is_name_token("1")


def test_name_token_6():
    assert not is_name_token("-")


def test_name_token_7():
    assert not is_name_token("na-me")


def test_name_token_8():
    assert not is_name_token("na_me")


def test_name_token_9():
    assert not is_name_token("name#")


def test_integer_token():
    assert is_integer_token("1")


def test_integer_token_1():
    assert is_integer_token("666")


def test_integer_token_2():
    assert is_integer_token("123231")


def test_integer_token_3():
    assert not is_integer_token("n")


def test_integer_token_4():
    assert not is_integer_token("name")


def test_integer_token_5():
    assert not is_integer_token("n4")


def test_integer_token_6():
    assert not is_integer_token("n4m3")


def test_integer_token_7():
    assert not is_integer_token("1n4m3")


def test_integer_token_8():
    assert not is_integer_token("-")


def test_integer_token_9():
    assert not is_integer_token("na-me")


def test_integer_token_10():
    assert not is_integer_token("na_me")


def test_integer_token_11():
    assert not is_integer_token("name#")
