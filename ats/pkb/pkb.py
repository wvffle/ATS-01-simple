from ats.ast import nodes

STMT_TYPE_MAP = {
    "stmt": nodes.StmtNode,
    "assign": nodes.StmtAssignNode,
    "while": nodes.StmtWhileNode,
    "if": nodes.StmtIfNode,
}


def preprocess_query(tree: nodes.ProgramNode):
    statements = {}
    variables = {}
    follows = {}

    def find_all_statements():
        stmt_index = 0
        stmt_id = 1

        def find_statements_and_variables(node: nodes.ASTNode):
            nonlocal stmt_index
            nonlocal stmt_id

            # Reset the index when we enter a new statement list
            if isinstance(node, nodes.StmtLstNode):
                stmt_index = 0

            # Assign an index and a unique id to each statement
            if isinstance(node, nodes.StmtNode):
                statements[stmt_id] = node
                node.__stmt_id = stmt_id
                node.__stmt_index = stmt_index

                stmt_index += 1
                stmt_id += 1

            if isinstance(node, nodes.VariableNode):
                variables[node] = node.name

            for n in node.children:
                find_statements_and_variables(n)

        find_statements_and_variables(tree)

    def process_all_relations():
        def process_relations(node: nodes.ASTNode):
            # NOTE: Enter current node

            # Build the follows relation map
            if isinstance(node, nodes.StmtNode):
                if node.__stmt_index > 0:
                    follows[node] = node.parent.children[node.__stmt_index - 1]

            # NOTE: Process children in DFS
            for child in node.children:
                process_relations(child)

            # NOTE: Exit current node
            ...

        process_relations(tree)

    find_all_statements()
    process_all_relations()

    return {
        "statements": statements,
        "follows": follows,
    }


def _get_node(query, context, statement, parameter):
    if isinstance(parameter, int):
        return context["statements"][parameter]
    else:
        if not isinstance(statement, STMT_TYPE_MAP[query["variables"][parameter]]):
            raise KeyError("Invalid variable type")

        return statement


def _resolve_statements(query, a, b, statement, related_statement):
    if query["searching_variable"] == a:
        return related_statement(), statement, related_statement()
    if query["searching_variable"] == b:
        return related_statement(), statement, statement
    if not isinstance(a, int) and not isinstance(b, int):
        return related_statement(), statement, related_statement()
    return statement, statement, statement


def process_follows(query, context):
    a = query["relations"][0]["parameters"][0]
    b = query["relations"][0]["parameters"][1]
    follows = context["follows"]

    result = set()
    for stmt in context["statements"].values():
        try:
            stmt_a, stmt_b, searching = _resolve_statements(
                query, a, b, stmt, lambda: follows[stmt]
            )
            node_a = _get_node(query, context, stmt_a, a)
            node_b = _get_node(query, context, stmt_b, b)

            if follows[node_b] == node_a:
                result.add(searching.__stmt_id)

        except KeyError:
            pass

    return list(result)


def process_parent(query, context):
    a = query["relations"][0]["parameters"][0]
    b = query["relations"][0]["parameters"][1]

    result = set()
    for stmt in context["statements"].values():
        try:
            stmt_a, stmt_b, searching = _resolve_statements(
                query, a, b, stmt, lambda: stmt.parent.parent
            )
            node_a = _get_node(query, context, stmt_a, a)
            node_b = _get_node(query, context, stmt_b, b)

            if node_b.parent.parent == node_a:
                result.add(searching.__stmt_id)

        except KeyError:
            pass

    return list(result)


def evaluate_query(node: nodes.ProgramNode, query):
    context = preprocess_query(node)
    if query["relations"][0]["relation"] == "Follows":
        return process_follows(query, context)
    if query["relations"][0]["relation"] == "Parent":
        return process_parent(query, context)
