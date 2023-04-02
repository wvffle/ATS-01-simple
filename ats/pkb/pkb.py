def follows(list, s1, s2):
    all_children = set(list.children)
    pool = all_children.copy()
    while pool:
        child = pool.pop()
        all_children.add(child)
        pool.update(child.children)
        for i, ch in enumerate(child.children):
            if s1 in child.children.__str__() and s2 in child.children.__str__():
                return True
            else:
                return False


def parent(list, s1, s2):
    all_children = set(list.children)
    pool = all_children.copy()
    while pool:
        child = pool.pop()
        all_children.add(child)
        pool.update(child.children)
        for i, ch in enumerate(child.children):
            if s1 in ch.__str__():
                if "stmtLst" in ch.children.__str__():
                    for x in ch.children:
                        if s2 in x.children.__str__():
                            return True
                        else:
                            return False
                else:
                    return False
            else:
                return False
