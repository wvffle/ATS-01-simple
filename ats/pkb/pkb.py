from collections.abc import Callable

from ats.ast import nodes

STMT_TYPE_MAP = {
    "stmt": nodes.StmtNode,
    "assign": nodes.StmtAssignNode,
    "while": nodes.StmtWhileNode,
    "if": nodes.StmtIfNode,
}


def dfs(
    node: nodes.ASTNode,
    on_node_enter: Callable[[nodes.ASTNode], None] = lambda _: None,
    on_node_exit: Callable[[nodes.ASTNode], None] = lambda _: None,
):
    on_node_enter(node)

    for child in node.children:
        dfs(child, on_node_enter, on_node_exit)

    on_node_exit(node)


def preprocess_query(tree: nodes.ProgramNode):
    statements = {}
    variables = {}
    follows = {}

    def find_statements():
        stmt_index = 0
        stmt_id = 1

        def on_node_enter(node: nodes.ASTNode):
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

            # Find all variables
            if isinstance(node, nodes.VariableNode):
                variables[node] = node.name

        dfs(tree, on_node_enter=on_node_enter)

    def process_relations():
        def on_node_enter(node: nodes.ASTNode):
            # Build the follows relation map
            if isinstance(node, nodes.StmtNode):
                if node.__stmt_index > 0:
                    follows[node] = node.parent.children[node.__stmt_index - 1]

        dfs(tree, on_node_enter=on_node_enter)

    find_statements()
    process_relations()

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
        return related_statement(statement), statement, related_statement(statement)
    if query["searching_variable"] == b:
        return related_statement(statement), statement, statement
    if not isinstance(a, int) and not isinstance(b, int):
        return related_statement(statement), statement, related_statement(statement)
    return statement, statement, statement


def process_follows(query, context):
    a = query["relations"][0]["parameters"][0]
    b = query["relations"][0]["parameters"][1]
    follows = context["follows"]

    result = set()
    for stmt in context["statements"].values():
        try:

            def relation(statement):
                return follows[statement]

            stmt_a, stmt_b, searching = _resolve_statements(query, a, b, stmt, relation)
            node_a = _get_node(query, context, stmt_a, a)
            node_b = _get_node(query, context, stmt_b, b)

            if relation(node_b) == node_a:
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

            def relation(statement):
                return statement.parent.parent

            stmt_a, stmt_b, searching = _resolve_statements(query, a, b, stmt, relation)
            node_a = _get_node(query, context, stmt_a, a)
            node_b = _get_node(query, context, stmt_b, b)

            if relation(node_b) == node_a:
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
