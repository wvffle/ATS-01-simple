from ats.ast import nodes

follow_dictionary = {}


def process_follows(query, statements):
    import json

    print(json.dumps(query, indent=2))

    return []


def crecreate_follow_dictionary(tree: nodes.ProgramNode):
    parent_childrens_list = []

    def create_parent_childrens_list(node: nodes.ASTNode):
        childrens = []
        for i in range(len(node.children)):
            create_parent_childrens_list(node.children[i])
            childrens.append(node.children[i])
        if len(node.children) > 0:
            parent_childrens_list.insert(0, childrens)

    create_parent_childrens_list(tree)

    for i in range(len(parent_childrens_list)):
        if len(parent_childrens_list[i]) > 1:
            for j in range(len(parent_childrens_list[i]) - 1):
                if (
                    str(parent_childrens_list[i][j]).split(": ")[0] == "stmt"
                    and str(parent_childrens_list[i][j]).split(": ")[0]
                    == str(parent_childrens_list[i][j + 1]).split(": ")[0]
                ):
                    follow_dictionary[str(parent_childrens_list[i][j])] = str(
                        parent_childrens_list[i][j + 1]
                    )


def evaluate_query(query):
    print(follow_dictionary)

    print(query)
    """
    if query["relation"] == "Follows":
        type = str(query["variables"][query["searching_variable"]])




    statements = {}
    i = 1
    def find_statements(node: nodes.ASTNode):
        if isinstance(node, nodes.StmtNode):
            nonlocal i
            statements[i] = node
            i += 1

        for n in node.children:
            find_statements(n)

    find_statements(tree)
    print(statements)

    if query["relation"] == "Follows":
        return process_follows(query, statements)"""
