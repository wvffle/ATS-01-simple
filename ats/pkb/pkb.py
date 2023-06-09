from ats.ast import nodes
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
    statements_by_type = {
        "procedure": [],
        "variable": [],
        "assign": [],
        "while": [],
        "stmt": [],
        "call": [],
        "if": [],
    }

    statements = {}
    procedures = {}
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
                statements_by_type["variable"].append(node)

            # Find all procedures
            if isinstance(node, nodes.ProcedureNode):
                procedures[node.name] = node
                statements_by_type["procedure"].append(node)

            # Find all statements by type
            if isinstance(node, nodes.StmtNode):
                statements_by_type[node._type].append(node)
                statements_by_type["stmt"].append(node)

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
        "statements_by_type": statements_by_type,
        "statements": statements,
        "procedures": procedures,
        "follows": follows,
        "calls": calls,
    }


def _get_stmt_type(query, parameter, default="stmt"):
    if parameter in query["variables"] and query["variables"][parameter] != "variable":
        return query["variables"][parameter]
    else:
        return default


# TODO: Handle with statements
def process_relation(
    query,
    context,
    relation_cb,
    resolve_node,
    map_result=lambda node: node,
    any_type="stmt",
):
    all_results = set()

    class Break(Exception):
        pass

    def get_needle(stmt_a, stmt_b):
        return stmt_a if query["searching_variable"] == a else stmt_b

    def check_relation(results, stmt_a, stmt_b):
        try:
            if relation_cb(stmt_a, stmt_b):
                if query["searching_variable"] == a or query["searching_variable"] == b:
                    results.add(map_result(get_needle(stmt_a, stmt_b)))

                # NOTE: Edge case: We are querying some unrelated statement
                else:
                    results |= set(
                        map(
                            map_result,
                            context["statements_by_type"][
                                _get_stmt_type(
                                    query, query["searching_variable"], any_type
                                )
                            ],
                        )
                    )
                    raise Break()
        except KeyError:
            pass

    for i, relation in enumerate(query["relations"]):
        results = all_results if i == 0 else set()
        a, b = relation["parameters"]

        try:
            # NOTE: Best case scenario, we do not have to iterate at all, just static lookup
            if not is_variable(query, a) and not is_variable(query, b):
                stmt_a = resolve_node(a)
                stmt_b = resolve_node(b)
                check_relation(results, stmt_a, stmt_b)

            # NOTE: Worst case scenario, we have to iterate over all statements in O(n^2)
            #       We try to optimize it by iterating only over the statements
            #       of the specific type
            elif is_variable(query, a) and is_variable(query, b):
                for stmt_a in context["statements_by_type"][
                    _get_stmt_type(query, a, any_type)
                ]:
                    for stmt_b in context["statements_by_type"][
                        _get_stmt_type(query, b, any_type)
                    ]:
                        check_relation(results, stmt_a, stmt_b)

            # NOTE: We have to iterate over all statements of only one type
            #       This is a case where we have a variable and a statement
            elif is_variable(query, a):
                stmt_b = resolve_node(b)
                for stmt_a in context["statements_by_type"][
                    _get_stmt_type(query, a, any_type)
                ]:
                    check_relation(results, stmt_a, stmt_b)

            # NOTE: We have to iterate over all statements of only one type
            #       This is a case where we have a statement and a variable
            elif is_variable(query, b):
                stmt_a = resolve_node(a)
                for stmt_b in context["statements_by_type"][
                    _get_stmt_type(query, b, any_type)
                ]:
                    check_relation(results, stmt_a, stmt_b)

            # NOTE: Create intersection of results if we have more than
            #       one relation in the query so we can handle AND
            if results != all_results:
                all_results = all_results.intersection(results)

        except Break:
            pass

    return list(all_results)


def process_follows(query, context):
    return process_relation(
        query,
        context,
        lambda node_a, node_b: context["follows"][node_b] == node_a,
        lambda id: context["statements"][id],
        lambda node: node.__stmt_id,
    )


def process_parent(query, context):
    return process_relation(
        query,
        context,
        lambda node_a, node_b: node_b.parent.parent == node_a,
        lambda id: context["statements"][id],
        lambda node: node.__stmt_id,
    )


def process_calls(query, context):
    def resolve_node(param):
        # NOTE: We got a string
        if param[0] == '"':
            return context["procedures"][param[1:-1]]

        # NOTE: We got a procedure name
        return context["procedures"][param]

    return process_relation(
        query,
        context,
        lambda node_a, node_b: node_b in context["calls"]
        and node_a in context["calls"][node_b],
        resolve_node,
        lambda node: node.name,
        any_type="procedure",
    )


def evaluate_query(node: nodes.ProgramNode, query):
    context = preprocess_query(node)
    if query["relations"][0]["relation"] == "Follows":
        return process_follows(query, context)

    if query["relations"][0]["relation"] == "Parent":
        return process_parent(query, context)

    if query["relations"][0]["relation"] == "Calls":
        return process_calls(query, context)

    return []
