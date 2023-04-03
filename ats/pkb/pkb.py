from ats.ast import nodes

mydict = {}


def add(list):
    idx = 0
    all_children = set(list.children)
    pool = all_children.copy()
    while pool:
        child = pool.pop()
        all_children.add(child)
        pool.update(child.children)
        for item in child.children:
            if isinstance(item, nodes.StmtLstNode):
                indexes = mydict.setdefault(idx, [])
                indexes.append(item.children)
                idx = idx + 1


def follows(s1: str, s2: str):
    for i in mydict.keys():
        one_level = mydict.get(i)[0]
        for j, item in enumerate(one_level):
            if j < len(one_level) - 1:
                if s1 in one_level[j].__str__() and s2 in one_level[j + 1].__str__():
                    print(1)
                    return True
