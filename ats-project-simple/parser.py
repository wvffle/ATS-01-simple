import re

from tokenizer import tokenize


def parse(text: str):
    tokens = tokenize(text)
    next_token = None

    def get_next_token():
        if len(tokens) > 0:
            return tokens.pop(0)

        return None

    def match_token(token: str):
        nonlocal next_token
        if next_token != token:
            raise ValueError(f"Expected token {token}, got {next_token}")

        next_token = get_next_token()

    def match_name_token():
        nonlocal next_token
        if next_token is None:
            raise ValueError("Expected name token, got end of file")

        if re.fullmatch(r"\w(\w|#)*", next_token) is None:
            raise ValueError(f"Token {next_token} is not a valid name token")

        next_token = get_next_token()

    def process_program():
        nonlocal next_token
        next_token = get_next_token()
        process_procedure()

    def process_procedure():
        match_token("procedure")
        match_name_token()
        match_token("{")
        process_stmt_lst()
        match_token("}")

    def process_stmt_lst():
        process_stmt()

        nonlocal next_token
        if next_token != "}":
            process_stmt_lst()

    def process_stmt():
        nonlocal next_token
        if next_token == "while":
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
        match_name_token()

        nonlocal next_token
        if next_token == "+":
            match_token("+")
            process_expr()

    # Parse the text
    process_program()
