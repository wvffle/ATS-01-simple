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
    uses = {}
    modifies = {}

    def find_all_statements():
        i = 1

        def find_statements_and_procedures(node: nodes.ASTNode):
            if isinstance(node, nodes.StmtNode):
                nonlocal i
                statements[i] = node
                node.__stmt_id = i
                i += 1
                modifies[node.__stmt_id] = []
                uses[node.__stmt_id] = []

            if isinstance(node, nodes.ProcedureNode):
                modifies[node.name] = []
                uses[node.name] = []

            for n in node.children:
                find_statements_and_procedures(n)

        find_statements_and_procedures(tree)

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
                nodes_with_call[node.__stmt_id] = []

            if isinstance(node, nodes.ProcedureNode):
                nodes_with_call[node.name] = []

            for child in node.children:
                nonlocal variable_list
                nonlocal current_procedure
                nodes_stack.append(child)
                if isinstance(child, nodes.ProcedureNode):
                    current_procedure = child.name
                process_relations(child)

                if isinstance(nodes_stack[-1], nodes.VariableNode):
                    if nodes_stack[-1].parent.condition == nodes_stack[-1]:
                        uses[nodes_stack[-1].parent.__stmt_id] = [nodes_stack[-1].name]
                    else:
                        variable_list.append(nodes_stack[-1].name)

                if isinstance(nodes_stack[-1].parent, nodes.StmtAssignNode):
                    if nodes_stack[-1].parent.variable == nodes_stack[-1]:
                        modifies[nodes_stack[-1].parent.__stmt_id] = [
                            nodes_stack[-1].name
                        ]
                    else:
                        uses[nodes_stack[-1].parent.__stmt_id] = variable_list
                    variable_list = []

                if isinstance(nodes_stack[-1], nodes.StmtCallNode):
                    if nodes_stack[-1].name == current_procedure:
                        raise RuntimeError("SIMPLE does not support recursion")
                    if nodes_stack[-1].name not in modifies:
                        raise RuntimeError(
                            'Procedure: "' + nodes_stack[-1].name + '" is not declared'
                        )
                    nodes_with_call[nodes_stack[-1].__stmt_id].append(
                        nodes_stack[-1].name
                    )

                if isinstance(nodes_stack[-1].parent, nodes.StmtLstNode):
                    parent_node = nodes_stack[-1].parent
                    if isinstance(parent_node.parent, nodes.StmtNode):
                        modifies[parent_node.parent.__stmt_id].extend(
                            modifies[nodes_stack[-1].__stmt_id]
                        )
                        uses[parent_node.parent.__stmt_id].extend(
                            uses[nodes_stack[-1].__stmt_id]
                        )
                        nodes_with_call[parent_node.parent.__stmt_id].extend(
                            nodes_with_call[nodes_stack[-1].__stmt_id]
                        )
                    if isinstance(parent_node.parent, nodes.ProcedureNode):
                        modifies[parent_node.parent.name].extend(
                            modifies[nodes_stack[-1].__stmt_id]
                        )
                        uses[parent_node.parent.name].extend(
                            uses[nodes_stack[-1].__stmt_id]
                        )
                        nodes_with_call[parent_node.parent.name].extend(
                            nodes_with_call[nodes_stack[-1].__stmt_id]
                        )

                nodes_stack.pop()

        variable_list = []
        current_procedure = ""
        nodes_stack.append(tree)
        process_relations(tree)

    nodes_with_call = {}
    nodes_stack = []
    find_all_statements()
    process_all_relations()

    for key, value in nodes_with_call.items():
        for v in value:
            modifies[key].extend(modifies[v])
            uses[key].extend(uses[v])
        modifies[key] = list(set(modifies[key]))
        uses[key] = list(set(uses[key]))

    return {
        "statements": statements,
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
        # case 5 - procedure and variable - procedure is searched for
        if searching_variable_type == "procedure":
            for key, value in uses.items():
                if b in value and isinstance(key, str):
                    results.append(key)

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
        # case 5 - procedure and variable - procedure is searched for
        if searching_variable_type == "procedure":
            for key, value in modifies.items():
                if b in value and isinstance(key, str):
                    results.append(key)

    results.sort()
    return results


def evaluate_query(node: nodes.ASTNode, query):
    context = preprocess_query(node)
    if query["relations"][0]["relation"] == "Follows":
        return process_follows(query, context)
    if query["relations"][0]["relation"] == "Parent":
        return process_parent(query, context)
    if query["relations"][0]["relation"] == "Uses":
        return process_uses(query, context)
    if query["relations"][0]["relation"] == "Modifies":
        return process_modifies(query, context)
