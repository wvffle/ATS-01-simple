from pptree import print_tree


class ASTNode:
    def __init__(self):
        self.nodes = {}
        self.children = []

    def add_node(self, field: str, node):
        self.nodes[field] = node

        if not isinstance(node, list):
            node = [node]

        for n in node:
            if isinstance(n, ASTNode):
                self.children.append(n)

    def print_tree(self):
        print_tree(self, "children", horizontal=False)

    def __str__(self):
        name = self.__class__.__name__[0:-4]
        name = name[0].lower() + name[1:]

        if hasattr(self, "name"):
            name += f": {self.name}"

        return name

    def __repr__(self):
        return self.__str__()


class ConstantNode(ASTNode):
    def __init__(self, value: str):
        super().__init__()
        self.name = value
        self.value = value


class VariableNode(ASTNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name


class ExprNode(ASTNode):
    pass


class StmtLstNode(ASTNode):
    def __init__(self, statements: list):
        super().__init__()
        self.add_node("statements", statements)


class ProcedureNode(ASTNode):
    def __init__(self, name: str, stmt_lst_node: StmtLstNode):
        super().__init__()
        self.name = name
        self.add_node("stmtLst", stmt_lst_node)


class ProgramNode(ASTNode):
    def __init__(self, procedure_node: ProcedureNode):
        super().__init__()
        self.add_node("procedure", procedure_node)


class StmtNode(ASTNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __str__(self):
        return "stmt: " + self.name


class StmtWhileNode(StmtNode):
    def __init__(self, condition_node: VariableNode, stmt_lst_node: StmtLstNode):
        super().__init__("while")
        self.add_node("condition", condition_node)
        self.add_node("stmtLst", stmt_lst_node)


class StmtAssignNode(StmtNode):
    def __init__(self, variable_node: VariableNode, expr_node: ExprNode):
        super().__init__("assign")
        self.add_node("variable", variable_node)
        self.add_node("expression", expr_node)
