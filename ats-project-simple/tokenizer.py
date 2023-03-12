def tokenize(text: str):
    tokens = text.split()
    tokens = [[token[:-1], ";"] if token[-1] == ";" else [token] for token in tokens]
    tokens = sum(tokens, [])
    return tokens
