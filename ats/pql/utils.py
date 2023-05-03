import re

from ats.parser.utils import is_integer_token, is_name_token


def is_variable_type_token(text: str):
    return text in ["stmt", "assign", "while"]


def is_program_design_entity_relationship_token(text: str):
    return text in ["Modifies", "Follows", "Parent", "Uses", "Calls"]


def is_string_token(text: str):
    return bool(re.match(r'^"[^"]*"$', text))


def is_stmtref(text: str):
    return is_name_token(text) or text == "_" or is_integer_token(text)


def is_entref(text: str):
    return is_name_token(text) or text == "_"
