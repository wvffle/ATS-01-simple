from ats.ast import nodes
from ats.ast.nodes import ProcedureNode
from ats.pkb.design_extractor import extract
from ats.pkb.utils import process_relation


def process_follows(query, context, relation):
    return process_relation(
        query,
        context,
        relation,
        lambda node_a, node_b: context["follows"][node_b] == node_a,
        lambda id: context["statements"][id] if id in context["statements"] else None,
    )


def process_follows_deep(query, context, relation):
    return process_relation(
        query,
        context,
        relation,
        lambda node_a, node_b: node_a.parent == node_b.parent
        and node_a.__stmt_index < node_b.__stmt_index,
        lambda id: context["statements"][id],
    )


def process_parent(query, context, relation):
    return process_relation(
        query,
        context,
        relation,
        lambda node_a, node_b: node_b.parent.parent == node_a,
        lambda id: context["statements"][id] if id in context["statements"] else None,
    )


def process_parent_deep(query, context, relation):
    def relation_cb(node_a, node_b):
        node = node_b.parent.parent
        while not isinstance(node, ProcedureNode):
            if node == node_a:
                return True
            node = node.parent.parent
        return False

    return process_relation(
        query,
        context,
        relation,
        relation_cb,
        lambda id: context["statements"][id],
    )


def process_calls(query, context, relation):
    def resolve_node(param):
        if param[1:-1] not in context["procedures"]:
            return None

        return context["procedures"][param[1:-1]]

    return process_relation(
        query,
        context,
        relation,
        lambda node_a, node_b: node_b in context["calls"]
        and node_a in context["calls"][node_b],
        resolve_node,
        any_type="procedure",
    )


def process_calls_deep(query, context, relation):
    def resolve_node(param):
        return context["procedures"][param[1:-1]]

    def relation_cb(node_a, node_b):
        if node_b in context["calls"]:
            if node_a in context["calls"][node_b]:
                return True

            for call in context["calls"][node_b]:
                if relation_cb(node_a, call):
                    return True
        return False

    return process_relation(
        query,
        context,
        relation,
        relation_cb,
        resolve_node,
        any_type="procedure",
    )


def process_uses(query, context, relation):
    def resolve_node(param):
        if isinstance(param, int):
            return context["statements"][param]
        else:
            return param[1:-1]

    return process_relation(
        query,
        context,
        relation,
        lambda node_a, node_b: node_b in context["uses"]
        and node_a in context["uses"][node_b],
        resolve_node,
    )


def process_modifies(query, context, relation):
    def resolve_node(param):
        if isinstance(param, int):
            return context["statements"][param]
        else:
            return param[1:-1]

    return process_relation(
        query,
        context,
        relation,
        lambda node_a, node_b: node_b in context["modifies"]
        and node_a in context["modifies"][node_b],
        resolve_node,
    )


def process_next(query, context, relation):
    return process_relation(
        query,
        context,
        relation,
        lambda node_a, node_b: node_a in context["next"]
        and node_b in context["next"][node_a],
        lambda id: context["statements"][id],
    )


def process_next_deep(query, context):
    checked_node_pairs = []

    def relation(node_a, node_b):
        if (node_a, node_b) not in checked_node_pairs:
            checked_node_pairs.append((node_a, node_b))
            if node_a in context["next"]:
                if node_b in context["next"][node_a]:
                    checked_node_pairs.clear()
                    return True

                for next in context["next"][node_a]:
                    if relation(next, node_b):
                        checked_node_pairs.clear()
                        return True
            return False

    return process_relation(
        query,
        context,
        relation,
        lambda id: context["statements"][id],
    )


def evaluate_query(node: nodes.ProgramNode, query):
    context = extract(node)
    all_results = set()
    for relation in query["conditions"]["relations"]:
        results = all_results if len(all_results) == 0 else set()
        if relation["relation"] == "Follows":
            results |= process_follows(query, context, relation)

        if relation["relation"] == "Follows*":
            results |= process_follows_deep(query, context, relation)

        if relation["relation"] == "Parent":
            results |= process_parent(query, context, relation)

        if relation["relation"] == "Parent*":
            results |= process_parent_deep(query, context, relation)

        if relation["relation"] == "Calls":
            results |= process_calls(query, context, relation)

        if relation["relation"] == "Calls*":
            results |= process_calls_deep(query, context, relation)

        if relation["relation"] == "Modifies":
            results |= process_modifies(query, context, relation)

        if relation["relation"] == "Uses":
            results |= process_uses(query, context, relation)

        if relation["relation"] == "Next":
            results |= process_next(query, context, relation)

        if relation["relation"] == "Next*":
            return process_next_deep(query, context)

        if results != all_results:
            all_results = all_results.intersection(results)

    for relation in query["conditions"]["attributes"]:
        results = all_results if len(all_results) == 0 else set()

        # TODO: Implement attribute processing

        if results != all_results:
            all_results = all_results.intersection(results)

    for relation in query["conditions"]["patterns"]:
        results = all_results if len(all_results) == 0 else set()

        # TODO: Implement pattern processing

        if results != all_results:
            all_results = all_results.intersection(results)

    if query["searching_variable"] == "BOOLEAN":
        return len(all_results) > 0

    return list(all_results)
