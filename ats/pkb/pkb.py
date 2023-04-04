from ats.ast import nodes


def process_follows(query, statements):
    import json

    print(json.dumps(query, indent=2))

    return []


def evaluate_query(tree: nodes.ProgramNode, query):
    statements = {}

    i = 1

    def find_statements(node: nodes.ASTNode):
        if isinstance(node, nodes.StmtNode):
            nonlocal i
            statements[i] = node
            i += 1

        for n in node.children:
            find_statements(n)

    find_statements(tree)

    if query["relation"] == "Follows":
        return process_follows(query, statements)
