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

        if token.type == tk.NEWLINE:
            tokens.append("\n")
            continue

        if len(token.string) > 0 and token.string[-1] == "\n":
            if len(token.string.strip()) > 1:
                tokens.append(token.string.strip())
            tokens.append("\n")
            continue

        if token.string.strip() != "":
            tokens.append(token.string.strip())

    return tokens
