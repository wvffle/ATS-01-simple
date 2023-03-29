from ats.parser.utils import is_integer_token, is_name_token
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

    def match_token(token: str):
        assert_token(f"token '{token}'")

        nonlocal current_token
        if current_token != token:
            raise ValueError(f"Expected token '{token}', got '{current_token}'")

        current_token = get_next_token()

    def match_name_token():
        assert_token("NAME_TOKEN")

        nonlocal current_token
        if not is_name_token(current_token):
            raise ValueError(f"Token '{current_token}' is not a valid NAME_TOKEN")

        current_token = get_next_token()

    def match_integer_token():
        assert_token("INTEGER_TOKEN")

        nonlocal current_token
        if not is_integer_token(current_token):
            raise ValueError(f"Token '{current_token}' is not a valid INTEGER_TOKEN")

        current_token = get_next_token()

    #
    # TOKEN PROCESSING
    #

    def process_program():
        nonlocal current_token
        current_token = get_next_token()
        process_procedure()

    def process_procedure():
        match_token("procedure")
        match_name_token()
        match_token("{")
        process_stmt_lst()
        match_token("}")

    def process_stmt_lst():
        process_stmt()

        nonlocal current_token
        if current_token != "}":
            process_stmt_lst()

    def process_stmt():
        nonlocal current_token
        if current_token == "while":
            return process_while()

        process_assign()

    def process_while():
        match_token("while")
        match_name_token()
        match_token("{")
        process_stmt_lst()
        match_token("}")

    def process_assign():
        match_name_token()
        match_token("=")
        process_expr()
        match_token(";")

    def process_expr():
        if tokens[0] == "+":
            # NOTE: Following commented code is 100% compliant with spec but causes an infinite loop
            # process_expr()
            # match_token("+")
            # return process_factor()

            # NOTE: The code below does not have aforementioned problem
            process_factor()
            match_token("+")
            return process_expr()

        process_factor()

    def process_factor():
        nonlocal current_token
        if is_integer_token(current_token):
            return match_integer_token()

        match_name_token()

    # NOTE: Parse the text
    process_program()
