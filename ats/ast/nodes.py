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


class ExprMinusNode(ExprNode):
    def __init__(self, left_node, right_node):
        super().__init__("minus")
        self.add_node("left", left_node)
        self.add_node("right", right_node)


class ExprTimesNode(ExprNode):
    def __init__(self, left_node, right_node):
        super().__init__("times")
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
    def __init__(self, procedure_nodes):
        super().__init__()

        self.add_node("procedure", procedure_nodes[0])
        self.add_node("procedures", procedure_nodes[1:])


class StmtNode(ASTNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __str__(self):  # pragma: no cover
        return "stmt: " + self.name


class StmtCallNode(StmtNode):
    def __init__(self, procedure_name: str):
        super().__init__("call")
        self.name = procedure_name

    def __str__(self):  # pragma: no cover
        return "call: " + self.name


class StmtWhileNode(StmtNode):
    def __init__(self, condition_node: VariableNode, stmt_lst_node: StmtLstNode):
        super().__init__("while")
        self.add_node("condition", condition_node)
        self.add_node("stmt_lst", stmt_lst_node)


class StmtIfNode(StmtNode):
    def __init__(
        self,
        condition_node: VariableNode,
        then_node: StmtLstNode,
        else_node: StmtLstNode,
    ):
        super().__init__("if")
        self.add_node("condition", condition_node)
        then_node.name = "then"
        else_node.name = "else"
        self.add_node("then_stmt_lst", then_node)
        self.add_node("else_stmt_lst", else_node)


class StmtAssignNode(StmtNode):
    def __init__(self, variable_node: VariableNode, expr_node: ExprNode):
        super().__init__("assign")
        self.add_node("variable", variable_node)
        self.add_node("expression", expr_node)
