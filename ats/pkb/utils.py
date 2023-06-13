from ats.ast import nodes
from ats.pql.pql import Any

NODE_TYPE_MAP = {
    "stmt": nodes.StmtNode,
    "assign": nodes.StmtAssignNode,
    "while": nodes.StmtWhileNode,
    "if": nodes.StmtIfNode,
    "procedure": nodes.ProcedureNode,
    "prog_line": nodes.StmtNode,
}


def is_valid_type(query, parameter, node):
    return isinstance(node, NODE_TYPE_MAP[query["variables"][parameter]])


def assert_variable_type(query, parameter, node):
    if not is_valid_type(query, parameter, node):
        raise TypeError("Invalid variable type")


def is_variable(query, parameter, node=None):
    if parameter is Any:
        return True

    if parameter not in query["variables"]:
        return False

    if node is not None:
        assert_variable_type(query, parameter, node)

    return True


def _get_stmt_type(query, parameter, default="stmt"):
    if parameter in query["variables"]:
        return query["variables"][parameter]
    else:
        return default


def map_result(node):
    if isinstance(node, nodes.StmtNode):
        return node.__stmt_id
    if isinstance(node, nodes.ProcedureNode):
        return node.name
    return node


def process_relation(
    query,
    context,
    relation,
    relation_cb,
    resolve_node,
    map_result=map_result,
    any_type="stmt",
):
    results = set()

    if is_variable(query, relation["parameters"][0]) and is_variable(
        query, relation["parameters"][1]
    ):
        if relation["parameters"][0] == relation["parameters"][1]:
            return results

    class Break(Exception):
        pass

    def get_needle(stmt_a, stmt_b):
        # Whem we explicitly ask for the second parameter
        if query["searching_variable"] == b:
            return stmt_b
        # Whem we explicitly ask for the first parameter, we ask for a BOOLEAN response or we ask for an unrelated variable
        return stmt_a

    def check_relation(stmt_a, stmt_b):
        nonlocal results

        try:
            if relation_cb(stmt_a, stmt_b):
                needle = query["searching_variable"]
                if needle == a or needle == b or needle == "BOOLEAN":
                    results.add(map_result(get_needle(stmt_a, stmt_b)))

                # NOTE: Edge case: We are querying some unrelated statement
                # PERF: We add entire set of statements of the given type to the results
                else:
                    results |= set(
                        map(
                            map_result,
                            context["statements_by_type"][
                                _get_stmt_type(
                                    query, query["searching_variable"], any_type
                                )
                            ],
                        )
                    )
                    raise Break()
        except KeyError:
            pass

    a, b = relation["parameters"]
    try:
        # NOTE: Best case scenario, we do not have to iterate at all, just static lookup
        if not is_variable(query, a) and not is_variable(query, b):
            stmt_a = resolve_node(a)
            stmt_b = resolve_node(b)
            check_relation(stmt_a, stmt_b)

        # NOTE: Worst case scenario, we have to iterate over all statements in O(n^2)
        #       We try to optimize it by iterating only over the statements
        #       of the specific type
        elif is_variable(query, a) and is_variable(query, b):
            for stmt_a in context["statements_by_type"][
                _get_stmt_type(query, a, any_type)
            ]:
                for stmt_b in context["statements_by_type"][
                    _get_stmt_type(query, b, any_type)
                ]:
                    check_relation(stmt_a, stmt_b)

        # NOTE: We have to iterate over all statements of only one type
        #       This is a case where we have a variable and a statement
        elif is_variable(query, a):
            stmt_b = resolve_node(b)
            for stmt_a in context["statements_by_type"][
                _get_stmt_type(query, a, any_type)
            ]:
                check_relation(stmt_a, stmt_b)

        # NOTE: We have to iterate over all statements of only one type
        #       This is a case where we have a statement and a variable
        elif is_variable(query, b):
            stmt_a = resolve_node(a)
            for stmt_b in context["statements_by_type"][
                _get_stmt_type(query, b, any_type)
            ]:
                check_relation(stmt_a, stmt_b)

    except Break:
        pass

    return results
