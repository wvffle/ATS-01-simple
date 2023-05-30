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
    parents = {}
    uses = {}
    modifies = {}

    def find_all_statements():
        i = 1

        def find_statements_and_variables(node: nodes.ASTNode):
            if isinstance(node, nodes.StmtNode):
                nonlocal i
                statements[i] = node
                node.__stmt_id = i
                i += 1

            if isinstance(node, nodes.VariableNode):
                variables[node] = node.name

            for n in node.children:
                find_statements_and_variables(n)

        find_statements_and_variables(tree)

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

            if isinstance(
                node, (nodes.StmtNode, nodes.StmtLstNode, nodes.ProcedureNode)
            ):
                uses_stack.append(node)
                uses_stack.append([])
                modifies_stack.append(node)
                modifies_stack.append([])

            else:
                uses_stack.append(node)
                modifies_stack.append(node)

            if isinstance(node, nodes.VariableNode) and node.parent.variable == node:
                uses_stack.pop()
                modifies_stack[-2].append(modifies_stack[-1].name)
                modifies_stack.pop()

            if (
                isinstance(uses_stack[-1], (nodes.VariableNode, nodes.ConstantNode))
                and node.parent.left != node
            ):
                variable_list = []
                while not isinstance(uses_stack[-1], list):
                    if isinstance(uses_stack[-1], nodes.VariableNode):
                        variable_list.append(uses_stack[-1].name)
                    uses_stack.pop()
                    modifies_stack.pop()
                uses_stack[-1] = variable_list
                if not isinstance(
                    uses_stack[-2], (nodes.StmtWhileNode, nodes.StmtIfNode)
                ):
                    while True:
                        variable_list = []
                        variable_list.extend(uses_stack[-1])
                        if isinstance(uses_stack[-2], nodes.StmtNode):
                            uses[uses_stack[-2].__stmt_id] = list(set(variable_list))
                        if isinstance(uses_stack[-2], nodes.ProcedureNode):
                            uses[uses_stack[-2].name] = list(set(variable_list))
                        if uses_stack[-2].parent.children[-1] != uses_stack[-2]:
                            uses_stack.pop()
                            uses_stack.pop()
                            uses_stack[-1].extend(variable_list)
                            break
                        uses_stack.pop()
                        uses_stack.pop()
                        if isinstance(uses_stack[-1], nodes.ProgramNode):
                            break
                        uses_stack[-1].extend(variable_list)
                    while True:
                        variable_list = []
                        variable_list.extend(modifies_stack[-1])
                        if isinstance(modifies_stack[-2], nodes.StmtNode):
                            modifies[modifies_stack[-2].__stmt_id] = list(
                                set(variable_list)
                            )
                        if isinstance(modifies_stack[-2], nodes.ProcedureNode):
                            modifies[modifies_stack[-2].name] = list(set(variable_list))
                        if modifies_stack[-2].parent.children[-1] != modifies_stack[-2]:
                            modifies_stack.pop()
                            modifies_stack.pop()
                            modifies_stack[-1].extend(variable_list)
                            break
                        modifies_stack.pop()
                        modifies_stack.pop()
                        if isinstance(modifies_stack[-1], nodes.ProgramNode):
                            break
                        modifies_stack[-1].extend(variable_list)

            for child in node.children:
                process_relations(child)

        process_relations(tree)

    uses_stack = []
    modifies_stack = []
    find_all_statements()
    process_all_relations()

    return {
        "statements": statements,
        "variables": variables,
        "follows": follows,
        "parents": parents,
        "uses": uses,
        "modifies": modifies,
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
    a = query["parameters"][0]
    b = query["parameters"][1].strip('"')
    searching_variable_type = query["variables"][query["searching_variable"]]
    uses = context["uses"]
    statements = context["statements"]

    results = []

    try:
        if isinstance(a, str) and isinstance(b, str):
            # case 1 - statement and variable
            if STMT_TYPE_MAP[searching_variable_type] == nodes.StmtNode:
                for key, value in uses.items():
                    if b in value and isinstance(key, int):
                        results.append(key)
            else:
                # case 2 - (assign or if or while) and variable
                if STMT_TYPE_MAP[searching_variable_type]:
                    for key, value in uses.items():
                        if b in value and isinstance(key, int):
                            if isinstance(
                                statements[key], STMT_TYPE_MAP[query["variables"][a]]
                            ):
                                results.append(key)

        if isinstance(a, int) and isinstance(b, str):
            # case 3 - constant and variable - variable is searched for
            if searching_variable_type == "variable":
                results = uses[a]
            # case 4 - constant and variable - statement is searched for
            else:
                if b in uses[a]:
                    results.append(a)

    except KeyError:
        try:
            # case 5 - procedure and variable - variable is searched for
            if searching_variable_type == "variable":
                a = a.strip('"')
                results = uses[a]
            # case 6 - procedure and variable - procedure is searched for
            if searching_variable_type == "procedure":
                for key, value in uses.items():
                    if b in value and isinstance(key, str):
                        results.append(key)
        except KeyError:
            pass

    results.sort()
    return results


def process_modifies(query, context):
    a = query["parameters"][0]
    b = query["parameters"][1].strip('"')
    searching_variable_type = query["variables"][query["searching_variable"]]
    modifies = context["modifies"]
    statements = context["statements"]

    results = []

    try:
        if isinstance(a, str) and isinstance(b, str):
            # case 1 - statement and variable
            if STMT_TYPE_MAP[searching_variable_type] == nodes.StmtNode:
                for key, value in modifies.items():
                    if b in value and isinstance(key, int):
                        results.append(key)
            else:
                # case 2 - (assign or if or while) and variable
                if STMT_TYPE_MAP[searching_variable_type]:
                    for key, value in modifies.items():
                        if b in value and isinstance(key, int):
                            if isinstance(
                                statements[key], STMT_TYPE_MAP[query["variables"][a]]
                            ):
                                results.append(key)

        if isinstance(a, int) and isinstance(b, str):
            # case 3 - constant and variable - variable is searched for
            if searching_variable_type == "variable":
                results = modifies[a]
            # case 4 - constant and variable - statement is searched for
            else:
                if b in modifies[a]:
                    results.append(a)

    except KeyError:
        try:
            # case 5 - procedure and variable - variable is searched for
            if searching_variable_type == "variable":
                a = a.strip('"')
                results = modifies[a]
            # case 6 - procedure and variable - procedure is searched for
            if searching_variable_type == "procedure":
                for key, value in modifies.items():
                    if b in value and isinstance(key, str):
                        results.append(key)
        except KeyError:
            pass

    results.sort()
    return results


def evaluate_query(node: nodes.ASTNode, query):
    context = preprocess_query(node)
    if query["relations"][0]["relation"] == "Follows":
        return process_follows(query, context)
    if query["relations"][0]["relation"] == "Parent":
        return process_parent(query, context)
    if query["relation"] == "Uses":
        return process_uses(query, context)
    if query["relation"] == "Modifies":
        return process_modifies(query, context)
