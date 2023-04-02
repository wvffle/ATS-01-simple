# from ats.ast import nodes


def follows(list):
    all_children = set(list.children)
    pool = all_children.copy()
    while pool:
        child = pool.pop()
        all_children.add(child)
        pool.update(child.children)
        for i, ch in enumerate(child.children):
            if "stmt:" in ch.__str__():
                if i + 1 < len(child.children):
                    if "stmt:" in child.children[i + 1].__str__():
                        return True

                        # print(child.children[i:i+2])
                        # return child.children[i:i+2]
