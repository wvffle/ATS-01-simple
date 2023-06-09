from ats.ast import nodes
from ats.pkb.utils import NODE_TYPE_MAP, is_variable


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
    modifies = {}
    uses = {}
    next = {}

    def find_statements():
        stmt_index = []
        stmt_id = 1
        proc_stmt_stack = []
        call_order = []

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

                proc_stmt_stack.append(node)
                next[node] = []

                # procedure parents
                if isinstance(node, nodes.StmtCallNode):
                    if node.name in proc_parents:
                        proc_parents[node.name].extend(proc_stmt_stack)
                    else:
                        proc_parents[node.name] = proc_stmt_stack[:]
                    # determining the order of call
                    # proc_stmt_stack[0] - procedure name in which is call
                    # node.name - call name
                    if (
                        proc_stmt_stack[0].name not in call_order
                        and node.name not in call_order
                    ):
                        call_order.append(proc_stmt_stack[0].name)
                        call_order.append(node.name)
                    elif (
                        proc_stmt_stack[0].name not in call_order
                        and node.name in call_order
                    ):
                        call_order.insert(
                            call_order.index(node.name), proc_stmt_stack[0].name
                        )
                    elif (
                        proc_stmt_stack[0].name in call_order
                        and node.name not in call_order
                    ):
                        call_order.insert(
                            call_order.index(proc_stmt_stack[0].name) + 1, node.name
                        )
                    else:
                        if call_order.index(node.name) < call_order.index(
                            proc_stmt_stack[0].name
                        ):
                            call_order.insert(
                                call_order.index(proc_stmt_stack[0].name) + 1, node.name
                            )
                        if call_order.index(node.name) > call_order.index(
                            proc_stmt_stack[0].name
                        ):
                            call_order.insert(
                                call_order.index(node.name), proc_stmt_stack[0].name
                            )

            # Find all variables
            if isinstance(node, nodes.VariableNode):
                variables[node] = node.name
                statements_by_type["variable"].append(node)

            # Find all procedures
            if isinstance(node, nodes.ProcedureNode):
                procedures[node.name] = node
                statements_by_type["procedure"].append(node)         
                proc_stmt_stack.append(node)

            # Find all statements by type
            if isinstance(node, nodes.StmtNode):
                statements_by_type[node._type].append(node)
                statements_by_type["stmt"].append(node)

        def on_node_exit(node: nodes.ASTNode, context):
            # Pop the index from the stack when exiting a statement list
            if isinstance(node, nodes.StmtLstNode):
                stmt_index.pop()
            if isinstance(node, (nodes.ProcedureNode, nodes.StmtNode)):
                proc_stmt_stack.pop()

        dfs(
            tree,
            on_node_enter=on_node_enter,
            on_node_exit=on_node_exit,
        )

        # extending procedure parents with nested calls
        extend_parents = []
        for name in call_order:
            if name in proc_parents:
                proc_parents[name].extend(extend_parents)
                proc_parents[name] = list(set(proc_parents[name]))
                extend_parents.extend(proc_parents[name])
            else:
                extend_parents = []

    def process_relations():
        # Build stack with procedures name and statements id
        def on_node_enter(node: nodes.ASTNode, context: dict):
            if isinstance(node, nodes.ProcedureNode):
                proc_stmt_stack.append(node)

            if isinstance(node, nodes.StmtNode):
                proc_stmt_stack.append(node)

                # dict Next
                # if the node is the first child and its parent is statement
                # then the node is next for the parent
                if node.parent.children[0] == node and isinstance(
                    node.parent.parent, nodes.StmtNode
                ):
                    next[proc_stmt_stack[-2]].append(node)

            # dict Next
            if isinstance(node, nodes.StmtNode):
                if node.__stmt_index > 0:
                    # if previous stmt in stmtLst is if stmt
                    # then add to stack if stmt node and id current node
                    if isinstance(
                        node.parent.children[node.__stmt_index - 1], nodes.StmtIfNode
                    ):
                        if_while_stack.append(node.children[node.__stmt_index - 1])
                        if_while_stack.append(node)
                    # add current node to next for previous stmt in stmtLst
                    else:
                        next[node.parent.children[node.__stmt_index - 1]].append(node)

            # dict Next
            if isinstance(node, nodes.StmtLstNode):
                if isinstance(node.parent, nodes.StmtWhileNode):
                    # if last child in while is if
                    # then add to stack while stmt node and its id
                    if isinstance(node.children[-1], nodes.StmtIfNode):
                        if_while_stack.append(node.parent)
                        if_while_stack.append(node.parent)
                    # while is next for the last child
                    else:
                        next[node.children[-1]].append(node.parent)

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

        def on_node_exit(node: nodes.ASTNode, context):
            # if current node is the same as the last node on the stack
            if len(if_while_stack) > 0:
                if node == if_while_stack[-2]:
                    if_while_stack.pop()
                    if_while_stack.pop()

            # dict Next
            if isinstance(node, nodes.StmtNode):
                if (
                    not isinstance(node, nodes.StmtIfNode)
                    and node.parent.children[-1] == node
                ):
                    # node is the last child in then stmtLst or else stmtLst
                    if node.parent.name == "then" or node.parent.name == "else":
                        if len(if_while_stack) > 0:
                            next[node].append(if_while_stack[-1])

            # modifies and uses
            if isinstance(node, nodes.VariableNode):
                # modifies
                if node.parent.variable == node:
                    if node.name not in modifies:
                        modifies[node.name] = []
                    # adding the parents of the variable
                    modifies[node.name] = list(
                        set(proc_stmt_stack + modifies[node.name])
                    )
                    # extension of the dictionary with the parents of the current procedure
                    if proc_stmt_stack[0].name in proc_parents:
                        modifies[node.name] = list(
                            set(
                                proc_parents[proc_stmt_stack[0].name]
                                + modifies[node.name]
                            )
                        )
                # uses
                else:
                    if node.name not in uses:
                        uses[node.name] = []
                    # adding the parents of the variable
                    uses[node.name] = list(set(proc_stmt_stack + uses[node.name]))
                    # extension of the dictionary with the parents of the current procedure
                    if proc_stmt_stack[0].name in proc_parents:
                        uses[node.name] = list(
                            set(proc_parents[proc_stmt_stack[0].name] + uses[node.name])
                        )

            if isinstance(node, (nodes.ProcedureNode, nodes.StmtNode)):
                proc_stmt_stack.pop()

        dfs(tree, on_node_enter=on_node_enter, on_node_exit=on_node_exit)

    proc_stmt_stack = []
    if_while_stack = []
    proc_parents = {}
    find_statements()
    process_relations()

    return {
        "statements_by_type": statements_by_type,
        "statements": statements,
        "procedures": procedures,
        "follows": follows,
        "calls": calls,
        "uses": uses,
        "modifies": modifies,  
        "next": next,
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


def process_uses(query, context):
    a = query["relations"][0]["parameters"][0]
    b = query["relations"][0]["parameters"][1].strip('"')
    searching_variable_type = query["variables"][query["searching_variable"]]
    uses = context["uses"]
    statements = context["statements"]

    results = []

    try:
        if isinstance(a, str) and isinstance(b, str):
            # case 1 - statement and variable
            if NODE_TYPE_MAP[searching_variable_type] == nodes.StmtNode:
                for value in uses[b]:
                    if isinstance(value, int):
                        results.append(value)
            # case 2 - procedure and variable - procedure is searched for
            elif NODE_TYPE_MAP[searching_variable_type] == nodes.ProcedureNode:
                for value in uses[b]:
                    if isinstance(value, str):
                        results.append(value)
            else:
                # case 3 - (assign or if or while) and variable
                if NODE_TYPE_MAP[searching_variable_type]:
                    for value in uses[b]:
                        if isinstance(value, int):
                            if isinstance(
                                statements[value], NODE_TYPE_MAP[query["variables"][a]]
                            ):
                                results.append(value)

        if isinstance(a, int) and isinstance(b, str):
            # case 4 - constant and variable - variable is searched for
            if searching_variable_type == "variable":
                for key, value in uses.items():
                    if a in value:
                        results.append(key)
            # case 5 - constant and variable - statement is searched for
            else:
                if a in uses[b]:
                    results.append(a)

    except KeyError:
        pass

    results.sort()
    return results


def process_modifies(query, context):
    a = query["relations"][0]["parameters"][0]
    b = query["relations"][0]["parameters"][1].strip('"')
    searching_variable_type = query["variables"][query["searching_variable"]]
    modifies = context["modifies"]
    statements = context["statements"]

    results = []

    try:
        if isinstance(a, str) and isinstance(b, str):
            # case 1 - statement and variable
            if NODE_TYPE_MAP[searching_variable_type] == nodes.StmtNode:
                for value in modifies[b]:
                    if isinstance(value, int):
                        results.append(value)
            # case 2 - procedure and variable - procedure is searched for
            elif NODE_TYPE_MAP[searching_variable_type] == nodes.ProcedureNode:
                for value in modifies[b]:
                    if isinstance(value, str):
                        results.append(value)
            else:
                # case 3 - (assign or if or while) and variable
                if NODE_TYPE_MAP[searching_variable_type]:
                    for value in modifies[b]:
                        if isinstance(value, int):
                            if isinstance(
                                statements[value], NODE_TYPE_MAP[query["variables"][a]]
                            ):
                                results.append(value)

        if isinstance(a, int) and isinstance(b, str):
            # case 4 - constant and variable - variable is searched for
            if searching_variable_type == "variable":
                for key, value in modifies.items():
                    if a in value:
                        results.append(key)
            # case 5 - constant and variable - statement is searched for
            else:
                if a in modifies[b]:
                    results.append(a)

    except KeyError:
        pass

    results.sort()
    return results


def evaluate_query(node: nodes.ProgramNode, query):
    context = preprocess_query(node)
    if query["relations"][0]["relation"] == "Follows":
        return process_follows(query, context)

    if query["relations"][0]["relation"] == "Parent":
        return process_parent(query, context)

    if query["relations"][0]["relation"] == "Calls":
        return process_calls(query, context)

    return []
