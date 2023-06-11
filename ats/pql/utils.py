import re


def is_variable_type_token(text: str):
    return text in ["stmt", "procedure", "variable", "if", "assign", "while"]


def is_program_design_entity_relationship_token(text: str):
    return text in ["Modifies", "Follows", "Parent", "Uses", "Calls", "Next"]


def is_string_token(text: str):
    return bool(re.match(r'^"[^"]*"$', text))


def is_any_token(text: str):
    return text == "'_'"
