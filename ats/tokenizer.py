import tokenize as tk
from io import BytesIO


def tokenize(text: str):
    tokens = []
    for token in tk.tokenize(BytesIO(text.encode("utf-8")).readline):
        if token.type == tk.ENCODING:
            continue

        if token.type == tk.COMMENT:
            tokens.append("#")
            tokens += tokenize(token.string[1:])
            continue

        if token.type != tk.NEWLINE and token.string.strip() != "":
            tokens.append(token.string)

    return tokens
