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
    assert ast.nodes.procedures[0].__class__ == nodes.ProcedureNode
    assert ast.nodes.procedures[0].name == "proc"


def test_ast_procedure_multiple():
    ast = parse(
        """
        procedure proc {
            a = 1;
        }
        procedure proc2 {
            a = 8;
        }
    """
    )

    assert ast.__class__ == nodes.ProgramNode
    assert ast.nodes.procedures[0].__class__ == nodes.ProcedureNode
    assert ast.nodes.procedures[0].name == "proc"

    assert ast.nodes.procedures[1].__class__ == nodes.ProcedureNode
    assert ast.nodes.procedures[1].name == "proc2"


def test_ast_procedure_multiple_more():
    ast = parse(
        """
        procedure proc {
            a = 1;
        }
        procedure proc2 {
            a = 8;
        }
        procedure proc3 {
            a = 10;
        }
    """
    )

    assert ast.__class__ == nodes.ProgramNode
    assert ast.nodes.procedures[0].__class__ == nodes.ProcedureNode
    assert ast.nodes.procedures[0].name == "proc"

    assert ast.nodes.procedures[1].__class__ == nodes.ProcedureNode
    assert ast.nodes.procedures[1].name == "proc2"

    assert ast.nodes.procedures[2].__class__ == nodes.ProcedureNode
    assert ast.nodes.procedures[2].name == "proc3"


def test_ast_stmt_lst():
    ast = parse(
        """
        procedure proc {
            a = 1;
        }
    """
    )

    proc = ast.nodes.procedures[0]

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

    stmt_lst = ast.nodes.procedures[0].nodes.stmt_lst

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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprPlusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.ExprMinusNode
    deep = expr.nodes.right

    assert deep.nodes.left.__class__ == nodes.ConstantNode
    assert deep.nodes.left.value == "2"

    assert deep.nodes.right.__class__ == nodes.VariableNode
    assert deep.nodes.right.name == "d"


def test_ast_expr_minus_plus_odd():
    ast = parse(
        """
        procedure proc {
            a = c - 2 + d;
        }
    """
    )

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprMinusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.ExprPlusNode
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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprTimesNode
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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprTimesNode
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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprPlusNode
    assert expr.nodes.left.__class__ == nodes.VariableNode
    assert expr.nodes.left.name == "c"

    assert expr.nodes.right.__class__ == nodes.ExprTimesNode
    deep = expr.nodes.right

    assert deep.nodes.left.__class__ == nodes.ConstantNode
    assert deep.nodes.left.value == "2"

    assert deep.nodes.right.__class__ == nodes.VariableNode
    assert deep.nodes.right.name == "d"


def test_ast_expr_times_minus_long_odd():
    ast = parse(
        """
        procedure proc {
            a = c * 2 - d;
        }
    """
    )

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprMinusNode
    assert expr.nodes.left.__class__ == nodes.ExprTimesNode
    deep = expr.nodes.left

    assert deep.nodes.left.__class__ == nodes.VariableNode
    assert deep.nodes.left.name == "c"

    assert deep.nodes.right.__class__ == nodes.ConstantNode
    assert deep.nodes.right.value == "2"

    assert expr.nodes.right.__class__ == nodes.VariableNode
    assert expr.nodes.right.name == "d"


def test_ast_bracket_expr_minus_variables():
    ast = parse(
        """
        procedure proc {
            a = (c - d);
        }
    """
    )

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

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

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprTimesNode
    assert expr.nodes.left.__class__ == nodes.ConstantNode
    assert expr.nodes.left.value == "2"

    assert expr.nodes.right.__class__ == nodes.ExprMinusNode
    deep = expr.nodes.right

    assert deep.nodes.left.__class__ == nodes.VariableNode
    assert deep.nodes.left.name == "c"

    assert deep.nodes.right.__class__ == nodes.VariableNode
    assert deep.nodes.right.name == "d"


def test_ast_bracket_expr_plus_times_odd():
    ast = parse(
        """
        procedure proc {
            a = (c + 2) * b;
        }
    """
    )

    expr = ast.nodes.procedures[0].nodes.stmt_lst.nodes.statements[0].nodes.expression

    assert expr.__class__ == nodes.ExprTimesNode
    assert expr.nodes.left.__class__ == nodes.ExprPlusNode
    deep = expr.nodes.left

    assert deep.nodes.left.__class__ == nodes.VariableNode
    assert deep.nodes.left.name == "c"

    assert deep.nodes.right.__class__ == nodes.ConstantNode
    assert deep.nodes.right.value == "2"

    assert expr.nodes.right.__class__ == nodes.VariableNode
    assert expr.nodes.right.name == "b"


def test_ast_call():
    ast = parse(
        """
        procedure proc {
            call test;
        }
    """
    )

    stmt_lst = ast.nodes.procedures[0].nodes.stmt_lst

    assert len(stmt_lst.nodes.statements) == 1
    assert stmt_lst.nodes.statements[0].__class__ == nodes.StmtCallNode
    assert stmt_lst.nodes.statements[0].name == "test"


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

    stmt_lst = ast.nodes.procedures[0].nodes.stmt_lst

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

    stmt_lst = ast.nodes.procedures[0].nodes.stmt_lst

    assert len(stmt_lst.nodes.statements) == 1
    assert stmt_lst.nodes.statements[0].__class__ == nodes.StmtIfNode

    if_node = stmt_lst.nodes.statements[0]
    assert if_node.nodes.condition.__class__ == nodes.VariableNode
    assert if_node.nodes.condition.name == "a"

    assert if_node.nodes.then_stmt_lst.__class__ == nodes.StmtLstNode
    assert len(if_node.nodes.then_stmt_lst.nodes.statements) == 1

    assert if_node.nodes.else_stmt_lst.__class__ == nodes.StmtLstNode
    assert len(if_node.nodes.else_stmt_lst.nodes.statements) == 1
