import re


def is_name_token(token: str):
    return re.fullmatch(r"[a-zA-Z][a-zA-Z0-9]*", token) is not None


def is_integer_token(token: str):
    return re.fullmatch(r"[0-9]*", token) is not None
