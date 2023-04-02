from ats.ast import nodes
from ats.parser.utils import is_integer_token, is_name_token, is_reserved_keyword
from ats.tokenizer import tokenize


def parse(text: str):
    tokens = tokenize(text)
    current_token = None

    def get_next_token():
        if len(tokens) > 0:
            return tokens.pop(0)

        return None

    #
    # TOKEN MATCHING
    #

    def assert_token(expected_token: str):
        nonlocal current_token
        if current_token is None:
            raise ValueError(f"Expected {expected_token}, got end of file")

    def assert_no_tokens_left():
        nonlocal current_token
        if current_token is not None:
            raise ValueError(f"Expected end of file, got '{current_token}'")

    def match_token(token: str):
        assert_token(f"token '{token}'")

        nonlocal current_token
        if current_token != token:
            raise ValueError(f"Expected token '{token}', got '{current_token}'")

        current_token = get_next_token()

    def match_name_token():
        assert_token("NAME_TOKEN")

        nonlocal current_token
        if is_reserved_keyword(current_token):
            raise ValueError(f"Token '{current_token}' is a reserved keyword")

        if not is_name_token(current_token):
            raise ValueError(f"Token '{current_token}' is not a valid NAME_TOKEN")

        name = current_token
        current_token = get_next_token()
        return name

    def match_integer_token():
        assert_token("INTEGER_TOKEN")

        nonlocal current_token
        if not is_integer_token(current_token):
            raise ValueError(f"Token '{current_token}' is not a valid INTEGER_TOKEN")

        value = current_token
        current_token = get_next_token()
        return value

    #
    # TOKEN PROCESSING
    #

    def process_program():
        nonlocal current_token
        current_token = get_next_token()

        node = process_procedure()
        assert_no_tokens_left()

        return nodes.ProgramNode(node)

    def process_procedure():
        match_token("procedure")
        name = match_name_token()
        match_token("{")
        node = process_stmt_lst()
        match_token("}")

        return nodes.ProcedureNode(name, node)

    def process_stmt_lst(statements=None):
        statements = [] if statements is None else statements
        statements += [process_stmt()]

        nonlocal current_token
        if current_token != "}":
            process_stmt_lst(statements)

        return nodes.StmtLstNode(statements)

    def process_stmt():
        nonlocal current_token
        if current_token == "while":
            return process_while()

        if current_token == "if":
            return process_if()

        return process_assign()

    def process_while():
        match_token("while")
        condition = match_name_token()
        match_token("{")
        node = process_stmt_lst()
        match_token("}")

        return nodes.StmtWhileNode(nodes.VariableNode(condition), node)

    def process_if():
        match_token("if")
        match_name_token()
        match_token("then")
        match_token("{")
        process_stmt_lst()
        match_token("}")
        match_token("else")
        match_token("{")
        process_stmt_lst()
        match_token("}")

        return nodes.StmtIfNode(
            nodes.VariableNode(condition), then_stmt_lst, else_stmt_lst
        )

    def process_assign():
        variable = match_name_token()
        match_token("=")
        expr = process_expr()
        match_token(";")

        return nodes.StmtAssignNode(nodes.VariableNode(variable), expr)

    def process_expr():
        if tokens[0] == "+":
            # NOTE: Following commented code is 100% compliant with spec but causes an infinite loop
            # process_expr()
            # match_token("+")
            # return process_factor()

            # NOTE: The code below does not have aforementioned problem
            left = process_factor()
            match_token("+")
            right = process_expr()
            return nodes.ExprPlusNode(left, right)

        return process_factor()

    def process_factor():
        nonlocal current_token
        if is_name_token(current_token):
            var_name = match_name_token()
            return nodes.VariableNode(var_name)

        const_value = match_integer_token()
        return nodes.ConstantNode(const_value)

    # NOTE: Parse the text
    return process_program()
