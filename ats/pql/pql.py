from ats.parser.utils import is_integer_token, is_name_token
from ats.pql.utils import (
    is_any_token,
    is_program_design_entity_relationship_token,
    is_string_token,
    is_variable_type_token,
)
from ats.tokenizer import tokenize


class AnyType:
    def __repr__(self):  # pragma: no cover
        return self.__str__()

    def __str__(self):  # pragma: no cover
        return "Any"


Any = AnyType()


shallow_relationship = ["Modifies", "Uses"]
relationships_stmt_ref_and_stmt_ref = [
    "Parent",
    "Parent*",
    "Follows",
    "Follows*",
    "Next",
    "Next*",
]
relationships_ent_ref_and_ent_ref = ["Calls", "Calls*"]


def parse_query(text: str):
    tokens = tokenize(text)
    current_token = None

    def get_next_token():
        if len(tokens) > 0:
            return tokens.pop(0)

        return None

    def assert_token(expected_token: str):
        nonlocal current_token
        if current_token is None:
            raise ValueError(f"Expected {expected_token}, got end of file")

    def match_token(token: str):
        assert_token(f"token '{token}'")
        nonlocal current_token
        if current_token != token:
            raise ValueError(f"Expected token '{token}', got '{current_token}'")

        current_token = get_next_token()

    def match_variable_type_token():
        assert_token("VARTYPE_TOKEN")
        nonlocal current_token
        var_type = current_token
        if not is_variable_type_token(current_token):
            raise ValueError(
                f"Token '{current_token}' is not a valid VARIABLE_TYPE_TOKEN"
            )

        current_token = get_next_token()

        return var_type

    def match_variable_is_in_list_token(variables):
        assert_token("DECLARED_VARIABLE_TOKEN")
        nonlocal current_token
        if current_token not in variables:
            raise ValueError(f"Token '{current_token}' is not declared")

        searchingVariable = current_token
        current_token = get_next_token()

        return searchingVariable

    def match_name_token():
        assert_token("NAME_TOKEN")
        nonlocal current_token
        if not is_name_token(current_token):
            raise ValueError(f"Token '{current_token}' is not a valid NAME_TOKEN")

        name = current_token
        current_token = get_next_token()

        return name

    def match_design_entity_relationship():
        assert_token("DESIGN_ENTITY_RELATIONSHIP_TOKEN")
        nonlocal current_token

        if not is_program_design_entity_relationship_token(current_token):
            raise ValueError(f"Token '{current_token}' is not a valid NAME_TOKEN")

        relationship = current_token

        current_token = get_next_token()
        if current_token == "*":
            if relationship in shallow_relationship:
                raise ValueError(f"Token '{relationship}*' is not a valid NAME_TOKEN")

            relationship += "*"
            current_token = get_next_token()

        return relationship

    def match_end_of_declaration_token():
        assert_token("NAME_DECLARATION_TOKEN")
        nonlocal current_token
        if current_token != "," and current_token != ";":
            raise ValueError(
                f"Token '{current_token}' is not a valid NAME_DECLARATION_TOKEN"
            )

        name = current_token
        current_token = get_next_token()

        return name

    def match_stmt_ref_token(variables):
        assert_token("RELATIONSHIP_PARAMETER_TOKEN")
        nonlocal current_token
        if (
            not is_integer_token(current_token)
            and not is_any_token(current_token)
            and current_token not in variables
        ):
            raise ValueError(f"Token '{current_token}' is not valid STMT_REF_TOKEN")

        try:
            parameter = int(current_token)
        except Exception:
            parameter = current_token
        current_token = get_next_token()

        if is_any_token(parameter):
            return Any

        return parameter

    def match_ent_ref_token(variables):
        assert_token("RELATIONSHIP_PARAMETER_TOKEN")
        nonlocal current_token
        if (
            not is_string_token(current_token)
            and not is_any_token(current_token)
            and current_token not in variables
        ):
            raise ValueError(f"Token '{current_token}' is not valid ENT_REF_TOKEN")

        parameter = current_token
        current_token = get_next_token()
        if is_any_token(parameter):
            return Any

        return parameter

    def match_with_parameter_token(variables):
        assert_token("RELATIONSHIP_PARAMETER_TOKEN")
        nonlocal current_token
        if (
            not is_name_token(current_token)
            and not is_integer_token(current_token)
            and not is_string_token(current_token)
            and not is_any_token(current_token)
            and current_token not in variables
        ):
            raise ValueError(
                f"Token '{current_token}' is not valid WITH_PARAMETER_TOKEN"
            )

        parameter = current_token
        current_token = get_next_token()
        if is_any_token(parameter):
            return Any

        return parameter

    def match_attr_name_token():
        assert_token("ATTR_NAME_TOKEN")
        nonlocal current_token
        if (
            current_token != "stmt"
            and current_token != "value"
            and current_token != "procName"
            and current_token != "varName"
        ):
            raise ValueError(f"Token '{current_token}' is not valid ATTR_NAME_TOKEN")

        try:
            parameter = int(current_token)
        except Exception:
            parameter = current_token

        current_token = get_next_token()

        return parameter

    def process_pql_code():
        nonlocal current_token
        current_token = get_next_token()
        variables = process_variable({})
        return process_operation([], variables)

    def process_operation(queries, variables):
        nonlocal current_token
        while current_token != "Select":
            variables = process_variable(variables)

        queries.append(process_query(variables))

        if current_token is None:
            return queries

        return queries + process_operation([], variables)

    def process_query(variables):
        nonlocal current_token

        match_token("Select")
        searching_variable = match_variable_is_in_list_token(variables)
        such_thats = []
        such_thats.append(process_such_that(variables))

        while current_token == "such":
            such_thats.append(process_such_that(variables))

        return {
            "such_thats": such_thats,
            "searching_variable": searching_variable,
            "variables": dict(variables),
        }

    def process_such_that(variables):
        match_token("such")
        match_token("that")
        withs = []
        relationships = []
        process_relationship(variables, relationships)

        while current_token == "and":
            match_token("and")
            process_relationship(variables, relationships)

        if current_token == "with":
            match_token("with")
            process_optional_with(withs, variables)

        while current_token == "and":
            match_token("and")
            process_optional_with(withs, variables)

        return {
            "relations": relationships,
            "withs": withs,
        }

    def process_relationship_stmt_ref_and_ent_ref(variables):
        first_parameter = match_stmt_ref_token(variables)
        match_token(",")
        second_parameter = match_ent_ref_token(variables)
        match_token(")")

        return [first_parameter, second_parameter]

    def process_relationship_stmt_ref_and_stmt_ref(variables):
        first_parameter = match_stmt_ref_token(variables)
        match_token(",")
        second_parameter = match_stmt_ref_token(variables)
        match_token(")")

        return [first_parameter, second_parameter]

    def process_relationship_ent_ref_and_ent_ref(variables):
        first_parameter = match_ent_ref_token(variables)
        match_token(",")
        second_parameter = match_ent_ref_token(variables)
        match_token(")")

        return [first_parameter, second_parameter]

    def process_relationship(variables, relationships):
        relationship = match_design_entity_relationship()

        match_token("(")
        parameters = []
        if relationship in shallow_relationship:
            parameters = process_relationship_stmt_ref_and_ent_ref(variables)
        elif relationship in relationships_stmt_ref_and_stmt_ref:
            parameters = process_relationship_stmt_ref_and_stmt_ref(variables)
        elif relationship in relationships_ent_ref_and_ent_ref:
            parameters = process_relationship_ent_ref_and_ent_ref(variables)

        relationships.append({"relation": relationship, "parameters": parameters})

    def process_optional_with(withs, variables):
        nonlocal current_token
        attr_left = None
        attr_right = None

        if current_token in variables:
            left = match_variable_is_in_list_token(variables)

            match_token(".")
            attr_left = match_attr_name_token()
        else:
            left = match_with_parameter_token(variables)

        match_token("=")

        if current_token in variables:
            right = match_variable_is_in_list_token(variables)

            match_token(".")
            attr_right = match_attr_name_token()
        else:
            right = match_with_parameter_token(variables)

        withs.append(
            {
                "left": left,
                "attr_left": attr_left,
                "right": right,
                "attr_right": attr_right,
            }
        )

    def process_variable(variables):
        nonlocal current_token
        var_type = match_variable_type_token()
        variables = process_variable_name(var_type, variables)

        return variables

    def process_variable_name(var_type: str, variables):
        name = match_name_token()
        end_token = match_end_of_declaration_token()
        variables[name] = var_type

        if end_token == ",":
            return process_variable_name(var_type, variables)

        return variables

    return process_pql_code()
