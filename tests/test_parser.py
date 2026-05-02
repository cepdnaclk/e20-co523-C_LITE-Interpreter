"""
tests/test_parser.py
Unit tests for the C-Lite Recursive Descent Parser.
"""

import pytest
from src.lexer import Lexer
from src.parser import Parser, ParseError
from src.ast_nodes import (
    Program, VarDecl, Assignment, IfStatement, PrintfStatement,
    IntLiteral, FloatLiteral, Identifier, BinaryOp,
)


def parse(source: str) -> Program:
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


def first(source: str):
    """Return the first statement in the parsed program."""
    return parse(source).statements[0]


# ── Program structure ─────────────────────────────────────────────────────────

class TestProgramStructure:
    def test_empty_program(self):
        prog = parse("")
        assert prog.statements == []

    def test_single_statement(self):
        prog = parse("int x;")
        assert len(prog.statements) == 1

    def test_multiple_statements(self):
        prog = parse("int x; int y; int z;")
        assert len(prog.statements) == 3


# ── Variable declarations ─────────────────────────────────────────────────────

class TestVarDecl:
    def test_int_decl(self):
        stmt = first("int x;")
        assert isinstance(stmt, VarDecl)
        assert stmt.dtype == "int"
        assert stmt.name == "x"

    def test_float_decl(self):
        stmt = first("float pi;")
        assert isinstance(stmt, VarDecl)
        assert stmt.dtype == "float"
        assert stmt.name == "pi"

    def test_missing_semicolon(self):
        with pytest.raises(ParseError):
            parse("int x")

    def test_missing_name(self):
        with pytest.raises(ParseError):
            parse("int ;")


# ── Assignments ───────────────────────────────────────────────────────────────

class TestAssignment:
    def test_integer_assignment(self):
        stmt = first("x = 10;")
        assert isinstance(stmt, Assignment)
        assert stmt.name == "x"
        assert isinstance(stmt.expr, IntLiteral)
        assert stmt.expr.value == 10

    def test_float_assignment(self):
        stmt = first("pi = 3.14;")
        assert isinstance(stmt, Assignment)
        assert isinstance(stmt.expr, FloatLiteral)
        assert stmt.expr.value == pytest.approx(3.14)

    def test_ident_assignment(self):
        stmt = first("y = x;")
        assert isinstance(stmt.expr, Identifier)
        assert stmt.expr.name == "x"

    def test_expr_assignment(self):
        stmt = first("z = a + b;")
        assert isinstance(stmt.expr, BinaryOp)
        assert stmt.expr.op == "+"

    def test_missing_semicolon(self):
        with pytest.raises(ParseError):
            parse("x = 5")


# ── Expressions & Operator Precedence ────────────────────────────────────────

class TestExpressions:
    def test_addition(self):
        stmt = first("x = 1 + 2;")
        expr = stmt.expr
        assert isinstance(expr, BinaryOp) and expr.op == "+"

    def test_multiplication(self):
        stmt = first("x = 3 * 4;")
        expr = stmt.expr
        assert isinstance(expr, BinaryOp) and expr.op == "*"

    def test_precedence_mul_before_add(self):
        # 1 + 2 * 3 should parse as 1 + (2 * 3)
        stmt = first("x = 1 + 2 * 3;")
        expr = stmt.expr
        assert isinstance(expr, BinaryOp)
        assert expr.op == "+"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.op == "*"

    def test_parentheses_override_precedence(self):
        # (1 + 2) * 3 should parse as (1 + 2) * 3
        stmt = first("x = (1 + 2) * 3;")
        expr = stmt.expr
        assert isinstance(expr, BinaryOp)
        assert expr.op == "*"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.op == "+"

    def test_unary_minus(self):
        stmt = first("x = -5;")
        expr = stmt.expr
        # Represented as BinaryOp(-, IntLiteral(0), IntLiteral(5))
        assert isinstance(expr, BinaryOp)
        assert expr.op == "-"
        assert isinstance(expr.left, IntLiteral)
        assert expr.left.value == 0

    def test_comparison_eq(self):
        stmt = first("x = a == b;")
        assert isinstance(stmt.expr, BinaryOp)
        assert stmt.expr.op == "=="

    def test_comparison_lt(self):
        stmt = first("x = a < b;")
        assert stmt.expr.op == "<"

    def test_comparison_gt(self):
        stmt = first("x = a > b;")
        assert stmt.expr.op == ">"


# ── If statements ─────────────────────────────────────────────────────────────

class TestIfStatement:
    def test_if_no_else(self):
        stmt = first("if (x > 0) { printf(x); }")
        assert isinstance(stmt, IfStatement)
        assert stmt.else_block is None
        assert len(stmt.then_block) == 1

    def test_if_else(self):
        stmt = first("if (x > 0) { printf(1); } else { printf(0); }")
        assert isinstance(stmt, IfStatement)
        assert stmt.else_block is not None
        assert len(stmt.else_block) == 1

    def test_nested_if(self):
        src = "if (a > 0) { if (b > 0) { printf(1); } }"
        outer = first(src)
        assert isinstance(outer, IfStatement)
        inner = outer.then_block[0]
        assert isinstance(inner, IfStatement)

    def test_missing_paren(self):
        with pytest.raises(ParseError):
            parse("if x > 0 { printf(x); }")

    def test_missing_brace(self):
        with pytest.raises(ParseError):
            parse("if (x > 0) printf(x);")


# ── Printf statements ─────────────────────────────────────────────────────────

class TestPrintfStatement:
    def test_single_arg(self):
        stmt = first("printf(x);")
        assert isinstance(stmt, PrintfStatement)
        assert len(stmt.args) == 1

    def test_multiple_args(self):
        stmt = first("printf(a, b, c);")
        assert isinstance(stmt, PrintfStatement)
        assert len(stmt.args) == 3

    def test_expression_arg(self):
        stmt = first("printf(a + b);")
        assert isinstance(stmt.args[0], BinaryOp)

    def test_missing_semicolon(self):
        with pytest.raises(ParseError):
            parse("printf(x)")


# ── Error recovery ────────────────────────────────────────────────────────────

class TestParseErrors:
    def test_unexpected_token(self):
        with pytest.raises(ParseError):
            parse("== x;")

    def test_unclosed_paren(self):
        with pytest.raises(ParseError):
            parse("x = (1 + 2;")
