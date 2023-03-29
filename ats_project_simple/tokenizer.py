import tokenize as tk
from io import BytesIO


def tokenize(text: str):
    tokens = list(tk.tokenize(BytesIO(text.encode("utf-8")).readline))
    tokens = [
        token.string.strip()
        for token in tokens
        if token.type != tk.NEWLINE and token.string.strip() != ""
    ]
    tokens.pop(0)
    return tokens
