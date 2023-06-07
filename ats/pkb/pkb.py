from ats.ast import nodes
from ats.pql.pql import Any

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
    uses = {}
    modifies = {}
    calls = {}
    next = {}

    proc_parents = {}

    def find_all_statements():
        i = 1
        stack = []

        def find_statements_and_procedures(node: nodes.ASTNode):
            if isinstance(node, nodes.StmtNode):
                nonlocal i
                statements[i] = node
                node.__stmt_id = i
                i += 1

            if isinstance(node, nodes.VariableNode):
                modifies[node.name] = []
                uses[node.name] = []

            if isinstance(node, nodes.ProcedureNode):
                calls[node.name] = []
                stack.append(node.name)

            if isinstance(node, nodes.StmtNode):
                next[node.__stmt_id] = []
                stack.append(node.__stmt_id)
                if isinstance(node, nodes.StmtCallNode):
                    if node.name not in calls[stack[0]] and node.name != stack[0]:
                        calls[stack[0]].append(node.name)
                    if node.name in proc_parents:
                        proc_parents[node.name].extend(stack)
                    else:
                        proc_parents[node.name] = stack[:]
                    if stack[0] in proc_parents:
                        proc_parents[node.name].extend(proc_parents[stack[0]])
                    else:
                        ...

            for n in node.children:
                find_statements_and_procedures(n)
                if isinstance(n, (nodes.ProcedureNode, nodes.StmtNode)):
                    stack.pop()

        find_statements_and_procedures(tree)

    def process_all_relations():
        def process_relations(node: nodes.ASTNode):
            if isinstance(node, nodes.StmtLstNode):
                for i, child in enumerate(node.children):
                    if i > 0:
                        follows[child.__stmt_id] = node.children[i - 1].__stmt_id
                        if isinstance(node.children[i - 1], nodes.StmtIfNode):
                            if_while_stack.append(node.children[i - 1])
                            if_while_stack.append(child.__stmt_id)
                        else:
                            next[node.children[i - 1].__stmt_id].append(child.__stmt_id)
                if isinstance(node.parent, nodes.StmtWhileNode):
                    if isinstance(node.children[-1], nodes.StmtIfNode):
                        if_while_stack.append(node.parent)
                        if_while_stack.append(node.parent.__stmt_id)
                    else:
                        next[node.children[-1].__stmt_id].append(node.parent.__stmt_id)

            if isinstance(node, nodes.StmtNode):
                parent = node.parent.parent
                if isinstance(parent, nodes.StmtNode):
                    parents[node.__stmt_id] = parent.__stmt_id

            for child in node.children:
                nodes_stack.append(child)

                if isinstance(child, nodes.ProcedureNode):
                    proc_stmt_stack.append(child.name)

                if isinstance(child, nodes.StmtNode):
                    proc_stmt_stack.append(child.__stmt_id)
                    if child.parent.children[0] == child and isinstance(
                        child.parent.parent, nodes.StmtNode
                    ):
                        next[proc_stmt_stack[-2]].append(child.__stmt_id)

                process_relations(child)

                if len(if_while_stack) > 0:
                    if nodes_stack[-1] == if_while_stack[-2]:
                        if_while_stack.pop()
                        if_while_stack.pop()

                if isinstance(child, nodes.StmtNode):
                    if (
                        not isinstance(child, nodes.StmtIfNode)
                        and child.parent.children[-1] == child
                    ):
                        if child.parent.name == "then" or child.parent.name == "else":
                            if len(if_while_stack) > 0:
                                next[child.__stmt_id].append(if_while_stack[-1])

                if isinstance(nodes_stack[-1], nodes.VariableNode):
                    if nodes_stack[-1].parent.variable == nodes_stack[-1]:
                        modifies[nodes_stack[-1].name].extend(proc_stmt_stack)
                        if proc_stmt_stack[0] in proc_parents:
                            modifies[nodes_stack[-1].name].extend(
                                proc_parents[proc_stmt_stack[0]]
                            )
                    else:
                        uses[nodes_stack[-1].name].extend(proc_stmt_stack)
                        if proc_stmt_stack[0] in proc_parents:
                            uses[nodes_stack[-1].name].extend(
                                proc_parents[proc_stmt_stack[0]]
                            )
                if isinstance(nodes_stack[-1], (nodes.ProcedureNode, nodes.StmtNode)):
                    proc_stmt_stack.pop()

                nodes_stack.pop()

        process_relations(tree)

    nodes_stack = []
    if_while_stack = []
    proc_stmt_stack = []
    find_all_statements()
    process_all_relations()

    for key in modifies:
        modifies[key] = list(set(modifies[key]))
        uses[key] = list(set(uses[key]))

    return {
        "statements": statements,
        "follows": follows,
        "parents": parents,
        "uses": uses,
        "modifies": modifies,
        "calls": calls,
    }


def process_follows(query, context):
    a = query["relations"][0]["parameters"][0]
    b = query["relations"][0]["parameters"][1]
    follows = context["follows"]
    statements = context["statements"]

    result = []

    for stmt in context["statements"].values():
        try:
            # case 1 - constant and constant
            if isinstance(a, int) and isinstance(b, int):
                if follows[b] == a:
                    result.append(stmt.__stmt_id)

            # 2 - constant and variable
            if isinstance(a, int) and not isinstance(b, int):
                # Check the variable type
                if not isinstance(stmt, STMT_TYPE_MAP[query["variables"][b]]):
                    continue

                # Check relation
                if follows[stmt.__stmt_id] == a:
                    result.append(stmt.__stmt_id)

            # case 3 - variable and constant
            if not isinstance(a, int) and isinstance(b, int):
                # Check the variable type
                if not isinstance(stmt, STMT_TYPE_MAP[query["variables"][a]]):
                    continue

                # Check relation
                if follows[b] == stmt.__stmt_id:
                    result.append(stmt.__stmt_id)

            #  case 4 - varibale and variable
            if not isinstance(a, int) and not isinstance(b, int):
                if query["searching_variable"] == a:
                    s2 = stmt
                    s1 = statements[follows[stmt.__stmt_id]]
                elif query["searching_variable"] == b:
                    s2 = statements[follows[stmt.__stmt_id]]
                    s1 = stmt
                else:
                    s2 = stmt
                    s1 = statements[follows[stmt.__stmt_id]]

                # Check the variable a type
                if not isinstance(s1, STMT_TYPE_MAP[query["variables"][a]]):
                    continue

                # Check the variable b type
                if not isinstance(s2, STMT_TYPE_MAP[query["variables"][b]]):
                    continue

                # Check relation
                result.append(s1.__stmt_id)

        except KeyError:
            pass
    return result


def process_follows_star(query, context):
    a = query["relations"][0]["parameters"][0]
    b = query["relations"][0]["parameters"][1]
    follows = context["follows"]
    statements = context["statements"]
    result = []

    for stmt in context["statements"].values():

        def recu_follows_deep(a, b):
            if follows[b] == a:
                result.append(stmt.__stmt_id)
            else:
                b1 = follows[b]
                recu_follows_deep(a, b1)

        def recu_follows_deep_return_a(s1, s2):
            if isinstance(
                statements[s1],
                STMT_TYPE_MAP[query["variables"][query["searching_variable"]]],
            ):
                result.append(s1)

                if follows.get(s1) is not None:
                    recu_follows_deep_return_a(follows[s1], s1)

            elif follows.get(s1) is not None:
                recu_follows_deep_return_a(follows[s1], s1)

        def recu_follows_deep_return_b(s1, s2):
            if isinstance(statements[s1], STMT_TYPE_MAP[query["variables"][a]]):
                result.append(stmt.__stmt_id)

                if follows.get(s1) is not None:
                    recu_follows_deep_return_b(follows[s1], s1)

            elif follows.get(s1) is not None:
                recu_follows_deep_return_b(follows[s1], s1)

        try:
            # case 1 - constant and constant
            if isinstance(a, int) and isinstance(b, int):
                recu_follows_deep(a, b)

            # 2 - constant and variable
            if isinstance(a, int) and not isinstance(b, int):
                # Check the variable type
                if not isinstance(stmt, STMT_TYPE_MAP[query["variables"][b]]):
                    continue

                # Check relation
                recu_follows_deep(a, stmt.__stmt_id)

            # case 3 - variable and constant
            if not isinstance(a, int) and isinstance(b, int):
                # Check the variable type
                if not isinstance(stmt, STMT_TYPE_MAP[query["variables"][a]]):
                    continue

                # Check relation
                recu_follows_deep(stmt.__stmt_id, b)

            #  case 4 - varibale and variable
            if not isinstance(a, int) and not isinstance(b, int):
                s2 = stmt
                s1 = statements[follows[stmt.__stmt_id]]
                if query["searching_variable"] == a:
                    if isinstance(
                        s1, STMT_TYPE_MAP[query["variables"][a]]
                    ) and isinstance(s2, STMT_TYPE_MAP[query["variables"][b]]):
                        result.append(s1.__stmt_id)

                    if isinstance(s2, STMT_TYPE_MAP[query["variables"][b]]):
                        if follows.get(s1.__stmt_id) is not None:
                            recu_follows_deep_return_a(
                                follows[s1.__stmt_id], s1.__stmt_id
                            )

                elif query["searching_variable"] == b:
                    if isinstance(
                        s1, STMT_TYPE_MAP[query["variables"][a]]
                    ) and isinstance(s2, STMT_TYPE_MAP[query["variables"][b]]):
                        result.append(s2.__stmt_id)
                    if isinstance(s2, STMT_TYPE_MAP[query["variables"][b]]):
                        if follows.get(s1.__stmt_id) is not None:
                            recu_follows_deep_return_b(s1.__stmt_id, s2.__stmt_id)

        except KeyError:
            pass
    return result


def process_parent(query, context):
    a = query["relations"][0]["parameters"][0]
    b = query["relations"][0]["parameters"][1]
    parent = context["parents"]
    statements = context["statements"]

    result = []

    for stmt in context["statements"].values():
        try:
            # case 1 - constant and constant
            if isinstance(a, int) and isinstance(b, int):
                if parent[b] == a:
                    result.append(stmt.__stmt_id)

            # 2 - constant and variable
            if isinstance(a, int) and not isinstance(b, int):
                # Check the variable type
                if not isinstance(stmt, STMT_TYPE_MAP[query["variables"][b]]):
                    continue

                # Check relation
                if parent[stmt.__stmt_id] == a:
                    result.append(stmt.__stmt_id)

            # case 3 - variable and constant
            if not isinstance(a, int) and isinstance(b, int):
                # Check the variable type
                if not isinstance(stmt, STMT_TYPE_MAP[query["variables"][a]]):
                    continue

                # Check relation
                if parent[b] == stmt.__stmt_id:
                    result.append(stmt.__stmt_id)

            #  case 4 - varibale and variable
            if not isinstance(a, int) and not isinstance(b, int):
                if query["searching_variable"] == a:
                    s2 = stmt
                    s1 = statements[parent[stmt.__stmt_id]]
                elif query["searching_variable"] == b:
                    s2 = statements[parent[stmt.__stmt_id]]
                    s1 = stmt
                else:
                    s2 = stmt
                    s1 = statements[parent[stmt.__stmt_id]]

                # Check the variable a type
                if not isinstance(s1, STMT_TYPE_MAP[query["variables"][a]]):
                    continue

                # Check the variable b type
                if not isinstance(s2, STMT_TYPE_MAP[query["variables"][b]]):
                    continue

                # Check relation
                result.append(s1.__stmt_id)

        except KeyError:
            pass
    return result


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
            if STMT_TYPE_MAP[searching_variable_type] == nodes.StmtNode:
                for value in uses[b]:
                    if isinstance(value, int):
                        results.append(value)
            else:
                # case 2 - (assign or if or while) and variable
                if STMT_TYPE_MAP[searching_variable_type]:
                    for value in uses[b]:
                        if isinstance(value, int):
                            if isinstance(
                                statements[value], STMT_TYPE_MAP[query["variables"][a]]
                            ):
                                results.append(value)

        if isinstance(a, int) and isinstance(b, str):
            # case 3 - constant and variable - variable is searched for
            if searching_variable_type == "variable":
                for key, value in uses.items():
                    if a in value:
                        results.append(key)
            # case 4 - constant and variable - statement is searched for
            else:
                if a in uses[b]:
                    results.append(a)

    except KeyError:
        try:
            # case 5 - procedure and variable - procedure is searched for
            if searching_variable_type == "procedure":
                for value in uses[b]:
                    if isinstance(value, str):
                        results.append(value)
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
            if STMT_TYPE_MAP[searching_variable_type] == nodes.StmtNode:
                for value in modifies[b]:
                    if isinstance(value, int):
                        results.append(value)
            else:
                # case 2 - (assign or if or while) and variable
                if STMT_TYPE_MAP[searching_variable_type]:
                    for value in modifies[b]:
                        if isinstance(value, int):
                            if isinstance(
                                statements[value], STMT_TYPE_MAP[query["variables"][a]]
                            ):
                                results.append(value)

        if isinstance(a, int) and isinstance(b, str):
            # case 3 - constant and variable - variable is searched for
            if searching_variable_type == "variable":
                for key, value in modifies.items():
                    if a in value:
                        results.append(key)
            # case 4 - constant and variable - statement is searched for
            else:
                if a in modifies[b]:
                    results.append(a)

    except KeyError:
        try:
            # case 5 - procedure and variable - procedure is searched for
            if searching_variable_type == "procedure":
                for value in modifies[b]:
                    if isinstance(value, str):
                        results.append(value)
        except KeyError:
            pass

    results.sort()
    return results


def process_calls(query, context):
    a = query["relations"][0]["parameters"][0]
    b = query["relations"][0]["parameters"][1]
    searching_variable_type = query["variables"][query["searching_variable"]]
    calls = context["calls"]

    results = []

    if searching_variable_type == "procedure":
        # case 1 - procedure and Any
        if isinstance(a, str) and b is Any:
            if a == query["searching_variable"]:
                for key, value in calls.items():
                    if len(value):
                        results.append(key)

        # case 2 - Any and procedure
        elif a is Any and isinstance(b, str):
            if b == query["searching_variable"]:
                for key, value in calls.items():
                    results.extend(value)
                results = list(set(results))

        elif isinstance(a, str) and isinstance(b, str):
            # case 3 - procedure and procedure - a is search for
            if (
                a in query["variables"]
                and b in query["variables"]
                and a == query["searching_variable"]
            ):
                for key, value in calls.items():
                    if len(value):
                        results.append(key)
            # case 4 - procedure and procedure - b is search for
            elif (
                a in query["variables"]
                and b in query["variables"]
                and b == query["searching_variable"]
            ):
                for key, value in calls.items():
                    results.extend(value)
                results = list(set(results))
            # case 5 procedure and procedure name
            elif a == query["searching_variable"]:
                b = b.strip('"')
                for key, value in calls.items():
                    if b in value:
                        results.append(key)
            # case 6 procedure name and procedure
            elif b == query["searching_variable"]:
                a = a.strip('"')
                results.extend(calls[a])

    results.sort()
    return results


def evaluate_query(node: nodes.ASTNode, query):
    context = preprocess_query(node)
    if query["relations"][0]["relation"] == "Follows":
        return process_follows(query, context)
    if query["relations"][0]["relation"] == "Follows*":
        return process_follows_star(query, context)
    if query["relations"][0]["relation"] == "Parent":
        return process_parent(query, context)
    if query["relations"][0]["relation"] == "Uses":
        return process_uses(query, context)
    if query["relations"][0]["relation"] == "Modifies":
        return process_modifies(query, context)
    if query["relations"][0]["relation"] == "Calls":
        return process_calls(query, context)
