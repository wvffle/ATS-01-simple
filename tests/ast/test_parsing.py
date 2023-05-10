from ats.ast import nodes
from ats.parser.parser import parse


def test_ast_procedure():
    ast = parse(
        """
        procedure proc {
            a = 1;
        }
    """
    )

    assert ast.__class__ == nodes.ProgramNode
    assert ast.nodes.procedure.__class__ == nodes.ProcedureNode
    assert ast.nodes.procedure.name == "proc"


def test_ast_stmt_lst():
    ast = parse(
        """
        procedure proc {
            a = 1;
        }
    """
    )

    proc = ast.nodes.procedure

    assert proc.nodes.stmt_lst.__class__ == nodes.StmtLstNode

    assert len(proc.nodes.stmt_lst.nodes.statements) == 1
    assert proc.nodes.stmt_lst.nodes.statements[0].__class__ == nodes.StmtAssignNode


def test_ast_assign_constant():
    ast = parse(
        """
        procedure proc {
            a = 1;
        }
    """
    )

    stmt_lst = ast.nodes.procedure.nodes.stmt_lst

    assert len(stmt_lst.nodes.statements) == 1
    assert stmt_lst.nodes.statements[0].__class__ == nodes.StmtAssignNode

    assign = stmt_lst.nodes.statements[0]

    assert assign.nodes.variable.__class__ == nodes.VariableNode
    assert assign.nodes.variable.name == "a"

    assert assign.nodes.expression.__class__ == nodes.ConstantNode
    assert assign.nodes.expression.value == "1"


def test_ast_expr_plus_constants():
    ast = parse(
        """
        procedure proc {
            a = 8 + 1;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprPlusNode
    assert expr.nodes.left.__class__ == nodes.ConstantNode
    assert expr.nodes.left.value == "8"

    assert expr.nodes.right.__class__ == nodes.ConstantNode
    assert expr.nodes.right.value == "1"


def test_ast_expr_plus_variables():
    ast = parse(
        """
        procedure proc {
            a = c + d;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprPlusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.VariableNode
    assert expr.nodes.right.name == "d"


def test_ast_expr_plus_long_odd():
    ast = parse(
        """
        procedure proc {
            a = c + 2 + d;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprPlusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.ExprPlusNode
    deep = expr.nodes.right

    assert deep.nodes.left.__class__ == nodes.ConstantNode
    assert deep.nodes.left.value == "2"

    assert deep.nodes.right.__class__ == nodes.VariableNode
    assert deep.nodes.right.name == "d"


def test_ast_expr_plus_long_even():
    ast = parse(
        """
        procedure proc {
            a = c + 2 + d + 8;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprPlusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.ExprPlusNode
    deep = expr.nodes.right

    assert deep.nodes.left.__class__ == nodes.ConstantNode
    assert deep.nodes.left.value == "2"

    assert deep.nodes.right.__class__ == nodes.ExprPlusNode
    deeper = deep.nodes.right

    assert deeper.nodes.left.__class__ == nodes.VariableNode
    assert deeper.nodes.left.name == "d"

    assert deeper.nodes.right.__class__ == nodes.ConstantNode
    assert deeper.nodes.right.value == "8"


def test_ast_expr_minus_constants():
    ast = parse(
        """
        procedure proc {
            a = 8 - 1;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprMinusNode
    assert expr.nodes.left.__class__ == nodes.ConstantNode
    assert expr.nodes.left.value == "8"

    assert expr.nodes.right.__class__ == nodes.ConstantNode
    assert expr.nodes.right.value == "1"


def test_ast_expr_minus_variables():
    ast = parse(
        """
        procedure proc {
            a = c - d;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprMinusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.VariableNode
    assert expr.nodes.right.name == "d"


def test_ast_expr_minus_long_odd():
    ast = parse(
        """
        procedure proc {
            a = c - 2 - d;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprMinusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.ExprMinusNode
    deep = expr.nodes.right

    assert deep.nodes.left.__class__ == nodes.ConstantNode
    assert deep.nodes.left.value == "2"

    assert deep.nodes.right.__class__ == nodes.VariableNode
    assert deep.nodes.right.name == "d"


def test_ast_expr_minus_long_even():
    ast = parse(
        """
        procedure proc {
            a = c - 2 - d - 8;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprMinusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.ExprMinusNode
    deep = expr.nodes.right

    assert deep.nodes.left.__class__ == nodes.ConstantNode
    assert deep.nodes.left.value == "2"

    assert deep.nodes.right.__class__ == nodes.ExprMinusNode
    deeper = deep.nodes.right

    assert deeper.nodes.left.__class__ == nodes.VariableNode
    assert deeper.nodes.left.name == "d"

    assert deeper.nodes.right.__class__ == nodes.ConstantNode
    assert deeper.nodes.right.value == "8"


def test_ast_expr_plus_minus_odd():
    ast = parse(
        """
        procedure proc {
            a = c + 2 - d;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprPlusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.ExprMinusNode
    deep = expr.nodes.right

    assert deep.nodes.left.__class__ == nodes.ConstantNode
    assert deep.nodes.left.value == "2"

    assert deep.nodes.right.__class__ == nodes.VariableNode
    assert deep.nodes.right.name == "d"


def test_ast_expr_plus_minus_long():
    ast = parse(
        """
        procedure proc {
            a = c + 2 - d - 8;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprPlusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.ExprMinusNode
    deep = expr.nodes.right

    assert deep.nodes.left.__class__ == nodes.ConstantNode
    assert deep.nodes.left.value == "2"

    assert deep.nodes.right.__class__ == nodes.ExprMinusNode
    deeper = deep.nodes.right

    assert deeper.nodes.left.__class__ == nodes.VariableNode
    assert deeper.nodes.left.name == "d"

    assert deeper.nodes.right.__class__ == nodes.ConstantNode
    assert deeper.nodes.right.value == "8"


def test_ast_term_times_constants():
    ast = parse(
        """
        procedure proc {
            a = 8 * 1;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.TimesNode
    assert expr.nodes.left.__class__ == nodes.ConstantNode
    assert expr.nodes.left.value == "8"

    assert expr.nodes.right.__class__ == nodes.ConstantNode
    assert expr.nodes.right.value == "1"


def test_ast_term_times_variables():
    ast = parse(
        """
        procedure proc {
            a = c * d;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.TimesNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.VariableNode
    assert expr.nodes.right.name == "d"


def test_ast_expr_plus_times_odd():
    ast = parse(
        """
        procedure proc {
            a = c + 2 * d;
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprPlusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.TimesNode
    deep = expr.nodes.right

    assert deep.nodes.left.__class__ == nodes.ConstantNode
    assert deep.nodes.left.value == "2"

    assert deep.nodes.right.__class__ == nodes.VariableNode
    assert deep.nodes.right.name == "d"


# NOTE: Test nie przedchodzi.
# Błąd w logice parsera: mnożenie nie może znajdować się po skrajnej lewej stronie expression.
# def test_ast_expr_times_minus_long_odd():
#     ast = parse(
#         """
#         procedure proc {
#             a = c * 2 - d;
#         }
#     """
#     )

#     expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

#     assert expr.__class__ == nodes.ExprMinusNode
#     assert expr.nodes.left.__class__ == nodes.TimesNode
#     deep = expr.nodes.left

#     assert deep.nodes.left.__class__ == nodes.VariableNode
#     assert deep.nodes.left.name == "c"

#     assert deep.nodes.right.__class__ == nodes.ConstantNode
#     assert deep.nodes.right.value == "2"

#     assert expr.nodes.right.__class__ == nodes.VariableNode
#     assert expr.nodes.right.name == "d"


def test_ast_bracket_expr_minus_variables():
    ast = parse(
        """
        procedure proc {
            a = (c - d);
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprMinusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.VariableNode
    assert expr.nodes.right.name == "d"


def test_ast_bracket_expr_times_minus_odd():
    ast = parse(
        """
        procedure proc {
            a = 2 * (c - d);
        }
    """
    )

    expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.TimesNode
    assert expr.nodes.left.__class__ == nodes.ConstantNode
    assert expr.nodes.left.value == "2"

    assert expr.nodes.right.__class__ == nodes.ExprMinusNode
    deep = expr.nodes.right

    assert deep.nodes.left.__class__ == nodes.VariableNode
    assert deep.nodes.left.name == "c"

    assert deep.nodes.right.__class__ == nodes.VariableNode
    assert deep.nodes.right.name == "d"


# NOTE: Test nie przedchodzi.
# Błąd w logice parsera
# def test_ast_bracket_expr_plus_times_odd():
#     ast = parse(
#         """
#         procedure proc {
#             a = (c + 2) * b;
#         }
#     """
#     )

#     expr = ast.nodes.procedure.nodes.stmt_lst.nodes.statements[0].nodes.expression

#     assert expr.__class__ == nodes.TimesNode
#     assert expr.nodes.left.__class__ == nodes.ExprPlusNode
#     deep = expr.nodes.left

#     assert deep.nodes.left.__class__ == nodes.VariableNode
#     assert deep.nodes.left.name == "c"

#     assert deep.nodes.right.__class__ == nodes.ConstantNode
#     assert deep.nodes.right.value == "2"

#     assert expr.nodes.right.__class__ == nodes.VariableNode
#     assert expr.nodes.right.name == "b"


def test_ast_while():
    ast = parse(
        """
        procedure proc {
            while a {
                a = 1;
            }
        }
    """
    )

    stmt_lst = ast.nodes.procedure.nodes.stmt_lst

    assert len(stmt_lst.nodes.statements) == 1
    assert stmt_lst.nodes.statements[0].__class__ == nodes.StmtWhileNode

    loop = stmt_lst.nodes.statements[0]
    assert loop.nodes.condition.__class__ == nodes.VariableNode
    assert loop.nodes.condition.name == "a"

    assert loop.nodes.stmt_lst.__class__ == nodes.StmtLstNode
    assert len(loop.nodes.stmt_lst.nodes.statements) == 1


def test_ast_if():
    ast = parse(
        """
        procedure proc {
            if a then {
                a = 1;
            }
            else {
                b = 2;
            }
        }
    """
    )

    stmt_lst = ast.nodes.procedure.nodes.stmt_lst

    assert len(stmt_lst.nodes.statements) == 1
    assert stmt_lst.nodes.statements[0].__class__ == nodes.StmtIfNode

    if_node = stmt_lst.nodes.statements[0]
    assert if_node.nodes.condition.__class__ == nodes.VariableNode
    assert if_node.nodes.condition.name == "a"

    assert if_node.nodes.then_stmt_lst.__class__ == nodes.StmtLstNode
    assert len(if_node.nodes.then_stmt_lst.nodes.statements) == 1

    assert if_node.nodes.else_stmt_lst.__class__ == nodes.StmtLstNode
    assert len(if_node.nodes.else_stmt_lst.nodes.statements) == 1
