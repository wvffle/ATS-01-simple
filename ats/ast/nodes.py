from dotmap import DotMap
from pptree import print_tree


class ASTNode:
    def __init__(self):
        self.nodes = DotMap()
        self.children = []

    def add_node(self, field: str, node):
        self.nodes[field] = node

        if not isinstance(node, list):
            node = [node]

        for n in node:
            if isinstance(n, ASTNode):
                self.children.append(n)

    def print_tree(self):  # pragma: no cover
        print_tree(self, "children", horizontal=False)

    def __str__(self):  # pragma: no cover
        name = self.__class__.__name__[0:-4]
        name = name[0].lower() + name[1:]

        if hasattr(self, "name"):
            name += f": {self.name}"

        return name

    def __repr__(self):  # pragma: no cover
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
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __str__(self):  # pragma: no cover
        return "expr: " + self.name


class ExprPlusNode(ExprNode):
    def __init__(self, left_node, right_node):
        super().__init__("plus")
        self.add_node("left", left_node)
        self.add_node("right", right_node)


class StmtLstNode(ASTNode):
    def __init__(self, statements: list):
        super().__init__()
        self.add_node("statements", statements)


class ProcedureNode(ASTNode):
    def __init__(self, name: str, stmt_lst_node: StmtLstNode):
        super().__init__()
        self.name = name
        self.add_node("stmt_lst", stmt_lst_node)


class ProgramNode(ASTNode):
    def __init__(self, procedure_node: ProcedureNode):
        super().__init__()
        self.add_node("procedure", procedure_node)


class StmtNode(ASTNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __str__(self):  # pragma: no cover
        return "stmt: " + self.name


class StmtWhileNode(StmtNode):
    def __init__(self, condition_node: VariableNode, stmt_lst_node: StmtLstNode):
        super().__init__("while")
        self.add_node("condition", condition_node)
        self.add_node("stmt_lst", stmt_lst_node)


class StmtAssignNode(StmtNode):
    def __init__(self, variable_node: VariableNode, expr_node: ExprNode):
        super().__init__("assign")
        self.add_node("variable", variable_node)
        self.add_node("expression", expr_node)
