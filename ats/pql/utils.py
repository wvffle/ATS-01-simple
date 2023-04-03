import re


def is_variable_type_token(text: str):
    return True if text == "stmt" or text == "assign" or text == "while" else False

def is_program_design_entity_relationship_token(text: str):
    return text in ["Modifies", "Follows", "Parent"]

def is_string_token(text: str):
    return bool(re.match(r'^"[^"]*"$', text))
