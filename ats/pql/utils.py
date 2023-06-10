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


def is_string_token(text: str):
    return bool(re.match(r'^"[^"]*"$', text))


def is_any_token(text: str):
    return text == "_"


DEFINED_RELATIONSHIPS = {}


def define_relationship(name, param_1, param_2):
    if not is_variable_type_token(param_1):
        raise ValueError(
            f"Parameter '{param_1}' at index 0 of the definition of relationship '{name} ' is not a valid design entity."
        )

    if not is_variable_type_token(param_2):
        raise ValueError(
            f"Parameter '{param_2}' at index 1 of the definition of relationship '{name} ' is not a valid design entity."
        )

    if name not in DEFINED_RELATIONSHIPS:
        DEFINED_RELATIONSHIPS[name] = []

    DEFINED_RELATIONSHIPS[name].append((param_1, param_2))


def is_program_design_entity_relationship_token(text: str):
    return text in DEFINED_RELATIONSHIPS.keys()


def get_relationship_arg_types(text: str):
    return DEFINED_RELATIONSHIPS[text]
