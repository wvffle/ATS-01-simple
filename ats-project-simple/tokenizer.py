import tokenize
from io import BytesIO


def tokenize_code(text: str):
    tokens = list(tokenize.tokenize(BytesIO(text.encode("utf-8")).readline))
    tokens = [
        token.string.strip()
        for token in tokens
        if token.type != tokenize.NEWLINE and token.string.strip() not in ["utf-8", ""]
    ]
    return tokens
