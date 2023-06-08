from collections.abc import Callable
from typing import Union

from dotmap import DotMap
from pptree import print_tree

printer_filter = None


class ASTNode:
    parent: Union["ASTNode", None]

    def __init__(self):
        self.name = ""
        self.nodes = DotMap()
        self.children = []
        self.parent = None

    def add_node(self, field: str, node):
        self.nodes[field] = node

        if isinstance(node, list):
            for n in node:
                n.parent = self
        else:
            node.parent = self

        if not isinstance(node, list):
            node = [node]

        for n in node:
            if isinstance(n, ASTNode):
                self.children.append(n)

    # NOTE: this is a hack to filter the tree while pretty printing it or to shorten the access to the nodes
    def __getattr__(self, name: str):  # pragma: no cover
        if name not in self.__dict__:
            if name == "filtered_children":
                return self._get_filtered_children()
            if name == "_name":
                raise AttributeError()
            return self.nodes[name]

        return self.__dict__[name]

    def _get_filtered_children(self):  # pragma: no cover
        if printer_filter is None:
            return self.children
        else:
            return [c for c in self.children if printer_filter(c)]

    def print_tree(
        self, filter: Callable[["ASTNode"], bool] | None = None
    ):  # pragma: no cover
        global printer_filter
        printer_filter = filter

        print_tree(self, "filtered_children", horizontal=False, nameattr="_name")

    def __str__(self):  # pragma: no cover
        name = self.__class__.__name__[0:-4]
        name = name[0].lower() + name[1:]

        if self.name != "":
            return f"{name}: {self.name}"

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
    parent: "StmtAssignNode"

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
    parent: "ProgramNode"

    def __init__(self, name: str, stmt_lst_node: StmtLstNode):
        super().__init__()
        self.name = name
        self.add_node("stmt_lst", stmt_lst_node)


class ProgramNode(ASTNode):
    parent: None

    def __init__(self, procedure_nodes):
        super().__init__()
        self.add_node("procedures", procedure_nodes)


class StmtNode(ASTNode):
    parent: "StmtLstNode"

    __stmt_index: int
    __stmt_id: int

    def __init__(self, name: str):
        super().__init__()
        self.__stmt_index = -1
        self.__stmt_id = -1

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
