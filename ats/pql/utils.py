import re


def is_variable_type_token(text: str):
    return text in [
        "stmt",
        "procedure",
        "variable",
        "if",
        "assign",
        "while",
        "constant",
        "prog_line",
        "call",
        "stmtLst",
        "plus",
        "minus",
        "times",
    ]


def is_program_design_entity_relationship_token(text: str):
    return text in ["Modifies", "Follows", "Parent", "Uses", "Calls", "Next"]


def is_string_token(text: str):
    return bool(re.match(r'^"[^"]*"$', text))


def is_any_token(text: str):
    return text == "_"


# def is_term_token(text: str):
#     if is_factor_token(text):
#         return True


# def is_factor_token(text: str):
#     if is_variable_type_token(text):
#         return True
#     if is_string_token(text):
#         return True
#     if is_any_token(text):
#         return True
#     if is_number_token(text):
#         return True
#     return False
