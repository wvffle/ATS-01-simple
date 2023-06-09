from itertools import chain

from ats.ast import nodes
from ats.ast.nodes import ProcedureNode
from ats.pkb.utils import is_variable


def _dfs_noop(node: nodes.ASTNode, context: dict):
    ...


def dfs(
    node: nodes.ASTNode,
    on_node_enter=_dfs_noop,
    on_node_exit=_dfs_noop,
):
    stack = []

    def _dfs(node: nodes.ASTNode):
        on_node_enter(node, {"stack": stack})
        stack.append(node)

        for child in node.children:
            _dfs(child)

        stack.pop()
        on_node_exit(node, {"stack": stack})

    _dfs(node)


def preprocess_query(tree: nodes.ProgramNode):
    procedures = {}
    statements = {}
    variables = {}
    follows = {}
    calls = {}

    def find_statements():
        stmt_index = []
        stmt_id = 1

        def on_node_enter(node: nodes.ASTNode, context: dict):
            nonlocal stmt_id

            # Push the index to the stack when entering a statement list
            if isinstance(node, nodes.StmtLstNode):
                stmt_index.append(0)

            # Assign an index and a unique id to each statement
            if isinstance(node, nodes.StmtNode):
                statements[stmt_id] = node
                node.__stmt_id = stmt_id
                node.__stmt_index = stmt_index[-1]

                stmt_index[-1] += 1
                stmt_id += 1

            # Find all variables
            if isinstance(node, nodes.VariableNode):
                variables[node] = node.name

            # Find all procedures
            if isinstance(node, nodes.ProcedureNode):
                procedures[node.name] = node

        def on_node_exit(node: nodes.ASTNode, context):
            # Pop the index from the stack when exiting a statement list
            if isinstance(node, nodes.StmtLstNode):
                stmt_index.pop()

        dfs(
            tree,
            on_node_enter=on_node_enter,
            on_node_exit=on_node_exit,
        )

    def process_relations():
        def on_node_enter(node: nodes.ASTNode, context: dict):
            # Build the follows relation map
            if isinstance(node, nodes.StmtNode):
                if node.__stmt_index > 0:
                    follows[node] = node.parent.children[node.__stmt_index - 1]

            # Build the calls relation map
            if isinstance(node, nodes.StmtCallNode):
                caller = context["stack"][1]
                callee = procedures[node.name]

                # Disable recurrence
                if caller is not callee:
                    if callee not in calls:
                        calls[callee] = set()
                    calls[callee].add(caller)

        dfs(tree, on_node_enter=on_node_enter)

    find_statements()
    process_relations()

    return {
        "statements": statements,
        "procedures": procedures,
        "follows": follows,
        "calls": calls,
    }


def _get_node(query, context, statement, parameter, type="statements"):
    if isinstance(parameter, int):
        # NOTE: We got a statement id
        return context[type][parameter]
    else:
        if not is_variable(query, parameter, statement):
            # NOTE: We got a string
            return context[type][parameter[1:-1]]

        # NOTE: We got a statement
        return statement


def _resolve_statements(query, a, b, statement, related_statement):
    # NOTE: We are focussed on the first variable
    if query["searching_variable"] == a:
        return related_statement(statement), statement, related_statement(statement)

    # NOTE: We are focussed on the second variable
    if query["searching_variable"] == b:
        return related_statement(statement), statement, statement

    # NOTE: We are querying some unrelated statement but both parameters are variables
    if not isinstance(a, int) and not isinstance(b, int):
        return related_statement(statement), statement, related_statement(statement)

    # NOTE: We are querying some unrelated variable
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
        except TypeError:
            pass

    return list(result)


def process_follows_deep(query, context):
    a = query["relations"][0]["parameters"][0]
    b = query["relations"][0]["parameters"][1]
    follows = context["follows"]

    result = set()

    if is_variable(query, a) and is_variable(query, b):
        if query["searching_variable"] == a:
            return list(set(map(lambda stmt: stmt.name, chain(*follows.values()))))

        if query["searching_variable"] == b:
            return map(lambda stmt: stmt.name, follows.keys())

    for stmt in context["statements"].values():
        try:

            def relation(statement):
                return statement

            stmt_a, stmt_b, searching = _resolve_statements(
                query, a, b, stmt, lambda _: stmt
            )
            # stmt_a, stmt_b, searching = _resolve_statements(query, a, b, stmt, relation)
            node_a = _get_node(query, context, stmt_a, a)
            node_b = _get_node(query, context, stmt_b, b)

            node = follows[node_b]
            while node:
                if node == node_a:
                    result.add(searching.__stmt_id)
                node = follows[node]

        except KeyError:
            pass
        except TypeError:
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
        except TypeError:
            pass

    return list(result)


def process_parent_deep(query, context):
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

            node = relation(node_b)
            while not isinstance(node, ProcedureNode):
                if node == node_a:
                    result.add(searching.__stmt_id)
                node = relation(node)

        except KeyError:
            pass
        except TypeError:
            pass

    return list(result)


def process_calls(query, context):
    a = query["relations"][0]["parameters"][0]
    b = query["relations"][0]["parameters"][1]
    calls = context["calls"]

    result = set()

    # NOTE: We got both dynamic parameters
    if is_variable(query, a) and is_variable(query, b):
        # We search for all caller procedures
        if query["searching_variable"] == a:
            return list(set(map(lambda proc: proc.name, chain(*calls.values()))))

        # We search for all callee procedures
        if query["searching_variable"] == b:
            return map(lambda proc: proc.name, calls.keys())

    # NOTE: We got maximum one dynamic parameter
    for proc in context["procedures"].values():
        try:
            stmt_a, stmt_b, searching = _resolve_statements(
                query, a, b, proc, lambda _: proc
            )

            node_a = _get_node(query, context, stmt_a, a, type="procedures")
            node_b = _get_node(query, context, stmt_b, b, type="procedures")

            if node_b in calls and node_a in calls[node_b]:
                result.add(searching.name)

        except KeyError:
            pass
        except TypeError:
            pass

    return list(result)


def evaluate_query(node: nodes.ProgramNode, query):
    context = preprocess_query(node)
    if query["relations"][0]["relation"] == "Follows":
        return process_follows(query, context)

    if query["relations"][0]["relation"] == "Follows*":
        return process_follows_deep(query, context)

    if query["relations"][0]["relation"] == "Parent":
        return process_parent(query, context)

    if query["relations"][0]["relation"] == "Parent*":
        return process_parent_deep(query, context)

    if query["relations"][0]["relation"] == "Calls":
        return process_calls(query, context)

    raise NotImplementedError("Relation not implemented")
    return []
