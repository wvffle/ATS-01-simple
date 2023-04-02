def parent(list):
    all_children = set(list.children)
    pool = all_children.copy()
    while pool:
        child = pool.pop()
        all_children.add(child)
        pool.update(child.children)
        if "stmtLst" in child.__str__():
            if len(child.children) > 0:
                print(child.children)
                return True
            else:
                print(child.children)
                return False
