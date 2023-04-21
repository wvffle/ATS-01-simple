from ats.ast import nodes


def process_follows(query, statements):
    import json

    print(json.dumps(query, indent=2))

    return []


def create_follows_dictionary(tree: nodes.ProgramNode):
    parent_childrens_list = []
    follows_dictionary = {}

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
                    follows_dictionary[str(parent_childrens_list[i][j])] = str(
                        parent_childrens_list[i][j + 1]
                    )
    return follows_dictionary


def evaluate_query(query, follows_dictionary):
    if query["relation"] == "Follows":
        if query["searching_variable"] == query["parameters"][0]:
            return [
                i
                for i in follows_dictionary
                if follows_dictionary[i].startswith(
                    query["variables"][query["searching_variable"]] + ":"
                )
            ]
        elif query["searching_variable"] == query["parameters"][1]:
            return [
                i
                for j, i in follows_dictionary.items()
                if j.startswith(query["variables"][query["searching_variable"]] + ":")
            ]
        else:
            return "Wrong query!"
