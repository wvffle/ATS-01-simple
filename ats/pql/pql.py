from ats.parser.parser import parse
from ats.parser.utils import is_integer_token, is_name_token
from ats.pql.utils import (
    define_relationship,
    get_relationship_arg_types,
    is_any_token,
    is_not_empty_string_token,
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

define_relationship("Modifies", "procedure", "variable")
define_relationship("Modifies", "stmt", "variable")
define_relationship("Uses", "procedure", "variable")
define_relationship("Uses", "stmt", "variable")
define_relationship("Calls", "procedure", "procedure")
define_relationship("Calls*", "procedure", "procedure")
define_relationship("Parent", "stmt", "stmt")
define_relationship("Parent*", "stmt", "stmt")
define_relationship("Follows", "stmt", "stmt")
define_relationship("Follows*", "stmt", "stmt")
define_relationship("Next", "prog_line", "prog_line")
define_relationship("Next*", "prog_line", "prog_line")


def parse_query(text: str):
    tokens = tokenize(text)
    current_token = None
    line_number = 1

    def get_next_token() -> str | None:
        nonlocal line_number

        while len(tokens) > 0 and tokens[0] == "\n":
            tokens.pop(0)
            line_number += 1

        if len(tokens) > 0:
            return tokens.pop(0)

        return None

    def assert_token(expected_token: str):
        nonlocal current_token
        if current_token is None:
            raise ValueError(
                f"Expected {expected_token}, got end of file\non line: {line_number}"
            )

    def match_token(token: str):
        assert_token(f"token '{token}'")
        nonlocal current_token
        if current_token != token:
            raise ValueError(
                f"Expected token '{token}', got '{current_token}'\non line: {line_number}"
            )

        current_token = get_next_token()

    def match_variable_type_token():
        assert_token("VARTYPE_TOKEN")
        nonlocal current_token
        var_type = current_token
        if not is_variable_type_token(current_token):
            raise ValueError(
                f"Token '{current_token}' is not a valid VARIABLE_TYPE_TOKEN\non line: {line_number}"
            )

        current_token = get_next_token()

        return var_type

    def match_variable_is_in_list_token(variables):
        assert_token("DECLARED_VARIABLE_TOKEN")
        nonlocal current_token
        if current_token not in variables:
            raise ValueError(
                f"Token '{current_token}' is not declared\non line: {line_number}"
            )

        searchingVariable = current_token
        current_token = get_next_token()

        return searchingVariable

    def match_name_token():
        assert_token("NAME_TOKEN")
        nonlocal current_token
        if not is_name_token(current_token):
            raise ValueError(
                f"Token '{current_token}' is not a valid NAME_TOKEN\non line: {line_number}"
            )

        name = current_token
        current_token = get_next_token()

        return name

    def match_design_entity_relationship():
        assert_token("DESIGN_ENTITY_RELATIONSHIP_TOKEN")
        nonlocal current_token

        relationship = current_token
        current_token = get_next_token()

        if current_token == "*":
            relationship += "*"
            current_token = get_next_token()

        if not is_program_design_entity_relationship_token(relationship):
            raise ValueError(
                f"Token '{relationship}' is not a valid RELATIONSHIP_NAME\non line: {line_number}"
            )

        return relationship

    def match_end_of_declaration_token():
        assert_token("NAME_DECLARATION_TOKEN")
        nonlocal current_token
        if current_token != "," and current_token != ";":
            raise ValueError(
                f"Token '{current_token}' is not a valid NAME_DECLARATION_TOKEN\non line: {line_number}"
            )

        name = current_token
        current_token = get_next_token()

        return name

    def match_var_ref_token(variables):
        assert_token("VARIABLE_PARAMETER_TOKEN")
        nonlocal current_token
        # varRef : synonym | ‘_’ | ‘“’ IDENT ‘“’
        # assign : synonym ‘(’ varRef ‘,’ expression-spec | ‘_’ ‘)’
        # expression-spec : ‘“’ expr ‘“’| ‘_’ ‘“’ expr ‘“’ ‘_’
        # /* ‘synonym’ above must be of type ‘assign’
        # expr must be a well-formed expression in SIMPLE
        # refer to query examples in section 7.5 in the Project Handbook */
        # if : synonym ‘(’ varRef ‘,’ ‘_’ ‘,’ ‘_’ ‘)’
        # // ‘synonym’ above must be of type ‘if’
        # while : synonym ‘(’ varRef ‘,’ ‘_’ ‘)’
        # // ‘synonym’ above must be of type ‘while’

        if not is_any_token(current_token) and current_token not in variables:
            raise ValueError(
                f"Token '{current_token}' is not valid VAR_REF_TOKEN\non line: {line_number}"
            )

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
                f"Token '{current_token}' is not valid WITH_PARAMETER_TOKEN\non line: {line_number}"
            )

        parameter = current_token
        current_token = get_next_token()
        if is_any_token(parameter):
            return Any

        return parameter

    def match_any_token():
        assert_token("ANY_TOKEN")
        nonlocal current_token
        if not is_any_token(current_token):
            raise ValueError(
                f"Token '{current_token}' is not valid ANY_TOKEN\non line: {line_number}"
            )

        current_token = get_next_token()
        return Any

    def match_attr_name_token():
        assert_token("ATTR_NAME_TOKEN")
        nonlocal current_token
        if (
            current_token != "stmt"
            and current_token != "value"
            and current_token != "procName"
            and current_token != "varName"
        ):
            raise ValueError(
                f"Token '{current_token}' is not valid ATTR_NAME_TOKEN\non line: {line_number}"
            )

        if current_token == "stmt":
            current_token = current_token + "#"
            get_next_token()

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
        if current_token == "BOOLEAN":
            searching_variable = "BOOLEAN"
            current_token = get_next_token()
        else:
            searching_variable = match_variable_is_in_list_token(variables)
        withs = []
        relationships = []
        patterns = []
        conditions = process_conditions(variables, withs, relationships, patterns)

        return {
            "conditions": {
                "relations": conditions["relations"],
                "attributes": conditions["withs"],
                "patterns": conditions["patterns"],
            },
            "searching_variable": searching_variable,
            "variables": dict(variables),
        }

    def process_conditions(variables, withs, relationships, patterns):
        nonlocal current_token
        while current_token == "such":
            match_token("such")
            match_token("that")
            process_relationship(variables, relationships)
            while current_token == "and":
                match_token("and")
                process_relationship(variables, relationships)

        if current_token == "pattern":
            match_token("pattern")
            process_pattern(variables, patterns)
            while current_token == "and":
                match_token("and")
                process_pattern(variables, patterns)

        if current_token == "with":
            match_token("with")
            process_optional_with(withs, variables)

        while current_token == "and":
            match_token("and")
            process_optional_with(withs, variables)

        if (
            current_token == "such"
            or current_token == "pattern"
            or current_token == "with"
        ):
            return process_conditions(variables, withs, relationships, patterns)

        return {"relations": relationships, "withs": withs, "patterns": patterns}

    def process_pattern(variables, patterns):
        nonlocal current_token
        if (
            variables[current_token] == "assign"
            or variables[current_token] == "while"
            or variables[current_token] == "if"
        ):
            pattern_variable = current_token
            pattern_type = variables[current_token]
            parameters = process_pattern_clause(variables, pattern_type)

            return patterns.append(
                {
                    "variable": pattern_variable,
                    "parameters": parameters,
                    "type": pattern_type,
                }
            )

    def process_pattern_clause(variables, pattern_type):
        nonlocal current_token
        match_variable_is_in_list_token(variables)
        match_token("(")
        if pattern_type == "assign":
            return process_pattern_assign(variables)
        if pattern_type == "while":
            return process_pattern_while(variables)
        if pattern_type == "if":
            return process_pattern_if(variables)

    def process_pattern_assign(variables):
        nonlocal current_token
        first_parameter = match_var_ref_token(variables)
        match_token(",")

        if current_token == "_":
            match_any_token()

            def is_only_any(expr_node):
                return True

            second_parameter = is_only_any

            if current_token != ")":
                expression = current_token.strip('"')
                tree = parse(f"procedure proc {{ assign = {expression}; }}")
                expr = tree.produces[0].stmt_lst.statements[0].expression

                def is_later(expr_node):
                    return expr_node.as_str().endsWith(expr.as_str())

                second_parameter = is_later
                get_next_token()
        else:
            expression = current_token.strip('"')
            tree = parse(f"procedure proc {{ assign = {expression}; }}")
            expr = tree.produces[0].stmt_lst.statements[0].expression
            current_token = get_next_token()

            def is_exact(expr_node):
                return expr_node.as_str() == expr.as_str()

            second_parameter = is_exact
            if current_token == "_":

                def is_before(expr_node):
                    return expr_node.as_str().startsWith(expr.as_str())

                second_parameter = is_before
                get_next_token()

        match_token(")")
        return [first_parameter, second_parameter]

    def process_pattern_while(variables):
        nonlocal current_token
        first_parameter = match_var_ref_token(variables)
        match_token(",")
        second_parameter = match_any_token()
        match_token(")")

        return [first_parameter, second_parameter]

    def process_pattern_if(variables):
        nonlocal current_token
        first_parameter = match_var_ref_token(variables)
        match_token(",")
        second_parameter = match_any_token()
        match_token(",")
        third_parameter = match_any_token()
        match_token(")")

        return [first_parameter, second_parameter, third_parameter]

    def process_relationship(variables, relationships):
        nonlocal current_token
        relationship = match_design_entity_relationship()

        match_token("(")
        parameters = []

        param_1 = current_token
        current_token = get_next_token()
        match_token(",")
        param_2 = current_token
        current_token = get_next_token()

        params = [param_1, param_2]

        def map_type(param):
            if param in variables:
                param_type = variables[param]
                return (
                    param_type
                    if param_type != "assign"
                    and param_type != "while"
                    and param_type != "if"
                    and param_type != "call"
                    else "stmt"
                )
            return None

        param_types = list(map(map_type, params))
        definitions = get_relationship_arg_types(relationship)

        def raise_empty_param():
            raise ValueError(
                f"String parameter cannot be empty in {relationship}({param_1}, {param_2})\non line: {line_number}"
            )

        for expected_types in definitions:
            result = [None, None]
            for i, param in enumerate(params):
                if param_types[i] == expected_types[i]:
                    result[i] = param
                # NOTE: prog_line is a synonym for stmt
                if param_types[i] == "stmt" and expected_types[i] == "prog_line":
                    result[i] = param
                elif is_any_token(param):
                    result[i] = Any
                elif expected_types[i] == "stmt" and is_integer_token(param):
                    result[i] = int(param)
                elif expected_types[i] == "prog_line" and is_integer_token(param):
                    result[i] = int(param)
                elif expected_types[i] == "procedure" and is_string_token(param):
                    if not is_not_empty_string_token(param):
                        raise_empty_param()
                    result[i] = param
                elif expected_types[i] == "variable" and is_string_token(param):
                    if not is_not_empty_string_token(param):
                        raise_empty_param()
                    result[i] = param

            if None not in result:
                parameters = result
                break

        if len(definitions) > 1:
            for i, param in enumerate(parameters):
                if param == Any:
                    constant_type = definitions[0][i]
                    for expected_types in definitions[1:]:
                        if expected_types[i] != constant_type:
                            valid_types = " | ".join(map(lambda x: x[i], definitions))
                            params = list(
                                map(
                                    lambda x: map_type(x)
                                    if map_type(x) is not None
                                    else x,
                                    params,
                                )
                            )
                            invalid_definition = (
                                f"{relationship}({params[0]}, {params[1]})"
                            )
                            raise ValueError(
                                f"Parameter {i} of the relationship {invalid_definition} cannot be of type Any. Expected one of {valid_types}\non line {line_number}"
                            )

        if len(parameters) == 0:
            valid_definitions = " | ".join(
                map(lambda x: f"{relationship}({x[0]}, {x[1]})", definitions)
            )
            params = list(
                map(lambda x: map_type(x) if map_type(x) is not None else x, params)
            )
            invalid_definition = f"{relationship}({params[0]}, {params[1]})"
            one_of = "one of " if len(definitions) > 1 else ""
            raise ValueError(
                f"Relationship {invalid_definition} is not valid. Expected {one_of}{valid_definitions}\non line {line_number}"
            )

        match_token(")")
        relationships.append(
            {
                "relation": relationship,
                "parameters": parameters,
            }
        )

    def assert_attribute_type(variable, attr, variables):
        if variables[variable] == "call":
            if attr not in ["procName"]:
                raise ValueError(
                    f"Call '{variable}' does not have attribute '{attr}'\non line {line_number}"
                )

        elif variables[variable] == "procedure":
            if attr not in ["procName"]:
                raise ValueError(
                    f"Procedure '{variable}' does not have attribute '{attr}'\non line {line_number}"
                )

        elif variables[variable] == "variable":
            if attr not in ["varName"]:
                raise ValueError(
                    f"Variable '{variable}' does not have attribute '{attr}'\non line {line_number}"
                )

        elif variables[variable] == "constant":
            if attr not in ["value"]:
                raise ValueError(
                    f"Constant '{variable}' does not have attribute '{attr}'\non line {line_number}"
                )

        elif variables[variable] in ["stmt", "while", "if", "assign"]:
            if attr not in ["stmt#"]:
                raise ValueError(
                    f"Statement '{variable}' does not have attribute '{attr}'\non line {line_number}"
                )
        else:
            raise ValueError(
                f"The {variables[variable]} '{variable}' does not have attribute '{attr}'\non line {line_number}"
            )

    def process_optional_with(withs, variables):
        nonlocal current_token
        attr_left = None
        attr_right = None
        print(variables)

        if current_token in variables:
            left = match_variable_is_in_list_token(variables)
            match_token(".")
            attr_left = match_attr_name_token()

            assert_attribute_type(left, attr_left, variables)

        else:
            left = match_with_parameter_token(variables)

        match_token("=")

        if current_token in variables:
            right = match_variable_is_in_list_token(variables)
            match_token(".")
            attr_right = match_attr_name_token()

            assert_attribute_type(right, attr_right, variables)
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
