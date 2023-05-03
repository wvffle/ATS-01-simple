from ats.parser.utils import is_integer_token, is_name_token
from ats.pql.utils import (
    is_program_design_entity_relationship_token,
    is_string_token,
    is_variable_type_token,
)
from ats.tokenizer import tokenize


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
            if relationship == "Modifies" or relationship == "Uses":
                raise ValueError(
                    f"Token '{relationship}*' is not a valid NAME_TOKEN"
                )

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

    def match_stmtref_token(variables):
        assert_token("RELATIONSHIP_PARAMETER_TOKEN")
        nonlocal current_token
        if (
            not is_integer_token(current_token)
            and current_token != "'_'"
            and current_token not in variables
        ):
            raise ValueError(f"Variable '{current_token}' is not valid STMTREF_TOKEN")

        parameter = current_token
        current_token = get_next_token()

        return parameter

    def match_entref_token(variables):
        assert_token("RELATIONSHIP_PARAMETER_TOKEN")
        nonlocal current_token
        if (
            not is_string_token(current_token)
            and current_token != "'_'"
            and current_token not in variables
        ):
            raise ValueError(f"Variable '{current_token}' is not valid ENTREF_TOKEN")

        parameter = current_token
        current_token = get_next_token()

        return parameter

    def match_with_parameter_token(variables):
        assert_token("RELATIONSHIP_PARAMETER_TOKEN")
        nonlocal current_token
        if (
            not is_name_token(current_token)
            and not is_integer_token(current_token)
            and not is_string_token(current_token)
            and current_token != "_"
            and current_token not in variables
        ):
            raise ValueError(
                f"Variable '{current_token}' is not valid WITH_PARAMETER_TOKEN"
            )

        parameter = current_token
        current_token = get_next_token()

        return parameter

    def match_attrname_token():
        assert_token("ATTRNAME_TOKEN")
        nonlocal current_token
        if current_token != "attrName":
            raise ValueError(f"Variable '{current_token}' is not valid ATTRNAME_TOKEN")

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
        match_token("such")
        match_token("that")

        relationships = []
        process_relationship(variables, relationships)
        while current_token == "and":
            match_token("and")
            process_relationship(variables, relationships)

        withs = []
        if current_token == "with":
            match_token("with")
            process_optional_with(withs, variables)

        while current_token == "and":
            match_token("and")
            process_optional_with(withs, variables)

        return {
            "relations": relationships,
            "searching_variable": searching_variable,
            "variables": dict(variables),
            "withs": withs,
        }

    def process_modifies_and_uses(variables):
        first_parameter = match_stmtref_token(variables)
        match_token(",")
        second_parameter = match_entref_token(variables)
        match_token(")")

        return [first_parameter, second_parameter]

    def process_parent_and_follows(variables):
        first_parameter = match_stmtref_token(variables)
        match_token(",")
        second_parameter = match_stmtref_token(variables)
        match_token(")")

        return [first_parameter, second_parameter]

    def process_calls(variables):
        first_parameter = match_entref_token(variables)
        match_token(",")
        second_parameter = match_entref_token(variables)
        match_token(")")

        return [first_parameter, second_parameter]

    def process_relationship(variables, relationships):
        relationship = match_design_entity_relationship()
        match_token("(")
        parameters = []
        if relationship == "Modifies" or relationship == "Uses":
            parameters = process_modifies_and_uses(variables)
        elif (
            relationship == "Parent"
            or relationship == "Parent*"
            or relationship == "Follows"
            or relationship == "Follows*"
        ):
            parameters = process_parent_and_follows(variables)
        elif relationship == "Calls" or relationship == "Calls*":
            parameters = process_calls(variables)

        relationships.append({"relation": relationship, "parameters": parameters})

    def process_optional_with(withs, variables):
        nonlocal current_token
        attr_left = None
        attr_right = None

        if current_token in variables:
            left = match_variable_is_in_list_token(variables)

            match_token(".")
            attr_left = match_attrname_token()
        else:
            left = match_with_parameter_token(variables)

        match_token("=")

        if current_token in variables:
            right = match_variable_is_in_list_token(variables)

            match_token(".")
            attr_right = match_attrname_token()
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
