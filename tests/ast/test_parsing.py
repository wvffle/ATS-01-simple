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
