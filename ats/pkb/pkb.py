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
    modifies = {}
    uses = {}

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
                uses[node.__stmt_id] = []

            """ FOR FIX
            if isinstance(node, nodes.ProcedureNode):
                nonlocal procedure_name
                procedure_name = node.name
                modifies[procedure_name] = []

            if isinstance(node, (nodes.StmtWhileNode, nodes.StmtIfNode)):
                modifies[node.__stmt_id] = []

            if isinstance(node, nodes.StmtAssignNode):
                variable = node.nodes.variable.name
                modifies[node.__stmt_id] = variable
                if variable not in modifies[procedure_name]:
                    modifies[procedure_name].append(variable)
                current_node = node
                while not isinstance(current_node, nodes.ProcedureNode):
                    if isinstance(current_node, (nodes.StmtWhileNode, nodes.StmtIfNode)):
                        if variable not in modifies[current_node.__stmt_id]:
                            modifies[current_node.__stmt_id].append(variable)
                    current_node = current_node.parent
                """
            for child in node.children:
                process_relations(child)

        """
        procedure_name = ""
        """
        process_relations(tree)

        for key in variables:
            current_node = key
            while not isinstance(current_node, nodes.ProcedureNode):
                if isinstance(current_node.parent, nodes.StmtNode):
                    if isinstance(current_node.parent, nodes.StmtAssignNode):
                        if current_node.parent.expression == current_node:
                            for stmt_key, stmt_value in statements.items():
                                if current_node.parent == stmt_value:
                                    uses[stmt_key].append(variables[key])
                        else:
                            break
                    else:
                        for stmt_key, stmt_value in statements.items():
                            if current_node.parent == stmt_value:
                                if variables[key] not in uses[stmt_key]:
                                    uses[stmt_key].append(variables[key])
                current_node = current_node.parent

    find_all_statements()
    process_all_relations()

    return {
        "statements": statements,
        "variables": variables,
        "follows": follows,
        "parents": parents,
        "modifies": modifies,
        "uses": uses,
    }


def process_follows(query, context):
    a = query["parameters"][0]
    b = query["parameters"][1]
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
    a = query["parameters"][0]
    b = query["parameters"][1]
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


def process_modifies(query, context):
    """NOT FINISHED
    a = query["parameters"][0]
    b = query["parameters"][1]
    searching_variable_type = query["variables"][query["searching_variable"]]
    modifies = context["modifies"]
    statements = context["statements"]
    results = []

    # case 1 - assign and variable
    if STMT_TYPE_MAP[searching_variable_type] == nodes.StmtAssignNode:
        variable = b.strip('\"')
        for key, value in modifies.items():
            if value == variable:
                results.append(key)

    # case 2 - while and variable
    if STMT_TYPE_MAP[searching_variable_type] == nodes.StmtWhileNode:
        variable = b.strip('\"')
        for key, value in modifies.items():
            if not isinstance(key, str):
                if isinstance(statements[key], STMT_TYPE_MAP[query["variables"][a]]):
                    if variable in value:
                        results.append(key)

    # case 3 - if and variable
    if STMT_TYPE_MAP[searching_variable_type] == nodes.StmtIfNode:
        variable = b.strip('\"')


    # case 4 - statement and variable
    if STMT_TYPE_MAP[searching_variable_type] == nodes.StmtNode:
        variable = b.strip('\"')
        for key, value in modifies.items():
            if not isinstance(key, str):
                if variable in value:
                    results.append(key)

    # case 5 - procedure and variable
    if searching_variable_type == "procedure":
        variable = b.strip('\"')
        for key, value in modifies.items():
            if isinstance(key, str):
                if variable in value:
                    results.append(key)

    # case 6 - variable and procedure
    if searching_variable_type == "variable":
        procedure = a.strip('\"')
        for key, value in modifies.items():
            if isinstance(key, str):
                if procedure in value:
                    results.append(key)

    print(query)
    print(statements)
    print(results)
    return results
    """


def process_uses(query, context):
    a = query["parameters"][0]
    b = query["parameters"][1].strip('"')
    searching_variable_type = query["variables"][query["searching_variable"]]
    uses = context["uses"]
    statements = context["statements"]

    results = []

    if isinstance(a, str) and isinstance(b, str):
        # case 1 - (assign or if or while) and variable
        if STMT_TYPE_MAP[searching_variable_type] in [
            nodes.StmtAssignNode,
            nodes.StmtIfNode,
            nodes.StmtWhileNode,
        ]:
            for key, value in uses.items():
                if b in value:
                    if isinstance(
                        statements[key], STMT_TYPE_MAP[query["variables"][a]]
                    ):
                        results.append(key)

        # case 2 - statement and variable
        if STMT_TYPE_MAP[searching_variable_type] == nodes.StmtNode:
            for key, value in uses.items():
                if b in value:
                    results.append(key)

    # case 3 - constant and variable
    if isinstance(a, int) and isinstance(b, str):
        if b in uses[a]:
            results.append(a)

    return results


def evaluate_query(node: nodes.ASTNode, query):
    context = preprocess_query(node)
    if query["relation"] == "Follows":
        return process_follows(query, context)
    if query["relation"] == "Parent":
        return process_parent(query, context)
    if query["relation"] == "Modifies":
        return process_modifies(query, context)
    if query["relation"] == "Uses":
        return process_uses(query, context)
