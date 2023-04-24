from ats.ast import nodes

STMT_TYPE_MAP = {
    "stmt": nodes.StmtNode,
    "assign": nodes.StmtAssignNode,
    "while": nodes.StmtWhileNode,
    "if": nodes.StmtIfNode,
}


def preprocess_query(tree: nodes.ProgramNode):
    statements = {}
    follows = {}
    parents = {}

    def find_all_statements():
        i = 1

        def find_statements(node: nodes.ASTNode):
            if isinstance(node, nodes.StmtNode):
                nonlocal i
                statements[i] = node
                node.__stmt_id = i
                i += 1

            for n in node.children:
                find_statements(n)

        find_statements(tree)

    def process_all_relations():
        def process_relations(node: nodes.ASTNode):
            if isinstance(node, nodes.StmtLstNode):
                for i, child in enumerate(node.children):
                    if i > 0:
                        follows[child.__stmt_id] = node.children[i - 1].__stmt_id

            if isinstance(node, nodes.StmtNode):
                parent = node.parent.parent
                if isinstance(parent, nodes.StmtNode):
                    parents[node.__stmt_id] = parent.__stmt_id

            for child in node.children:
                process_relations(child)

        process_relations(tree)

    find_all_statements()
    process_all_relations()

    return {
        "follows": follows,
        "parents": parents,
        "statements": statements,
    }


def process_follows(query, context):
    a = query["parameters"][0]
    b = query["parameters"][1]
    follows = context["follows"]

    result = []

    for stmt in context["statements"].values():
        # przypadek 1 - stala i stala
        if isinstance(a, int) and isinstance(b, int):
            if a not in follows:
                continue

            if follows[a] == b:
                result.append(stmt.__stmt_id)

        # przypadek 2 - stala i zmienna

        # przypadek 3 - zmienna i stala
        if not isinstance(a, int) and isinstance(b, int):
            # Check the variable type
            if not isinstance(stmt, STMT_TYPE_MAP[query["variables"][a]]):
                continue

            # Check if searching
            if stmt.__stmt_id not in follows:
                continue

            # Check relation
            if follows[stmt.__stmt_id] == b:
                result.append(stmt.__stmt_id)

        # przypadek 4 - zmienna i zmienna

    return result


def evaluate_query(node: nodes.ASTNode, query):
    context = preprocess_query(node)

    if query["relation"] == "Follows":
        return process_follows(query, context)
