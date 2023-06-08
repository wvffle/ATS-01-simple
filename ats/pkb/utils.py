from ats.ast import nodes
from ats.pql.pql import Any

NODE_TYPE_MAP = {
    "stmt": nodes.StmtNode,
    "assign": nodes.StmtAssignNode,
    "while": nodes.StmtWhileNode,
    "if": nodes.StmtIfNode,
    "procedure": nodes.ProcedureNode,
}


def assert_variable_type(query, parameter, node):
    if not isinstance(node, NODE_TYPE_MAP[query["variables"][parameter]]):
        raise TypeError("Invalid variable type")


def is_variable(query, parameter, node=None):
    if parameter is Any:
        return True

    if parameter not in query["variables"]:
        return False

    if node is not None:
        assert_variable_type(query, parameter, node)

    return True
