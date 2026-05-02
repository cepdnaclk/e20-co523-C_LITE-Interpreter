"""
tests/test_interpreter.py
Integration tests for the C-Lite Semantic Evaluator.
Each test runs a full lex → parse → evaluate pipeline.
"""

import pytest
from src.lexer import Lexer, LexerError
from src.parser import Parser, ParseError
from src.interpreter import Interpreter, RuntimeError_


def run(source: str) -> list[str]:
    """Full pipeline helper. Returns list of printf output lines."""
    output = []
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    Interpreter(output_callback=lambda s: output.append(s)).execute(program)
    return output


def run_one(source: str) -> str:
    """Run and return the single output line."""
    lines = run(source)
    assert len(lines) == 1, f"Expected 1 output line, got {lines}"
    return lines[0]


# ── T1–T2: Types ──────────────────────────────────────────────────────────────

class TestTypes:
    def test_int_declaration_and_assignment(self):
        assert run_one("int x; x = 10; printf(x);") == "10"

    def test_float_declaration_and_assignment(self):
        assert run_one("float pi; pi = 3.14; printf(pi);") == "3.14"

    def test_float_assigned_int_widens(self):
        # T15: float variable receives int value -> widened to float
        assert run_one("float f; f = 2; printf(f);") == "2.0"

    def test_int_assigned_float_truncates(self):
        # C-style: float stored into int is truncated
        assert run_one("int x; x = 3.9; printf(x);") == "3"


# ── T3–T5: Arithmetic ────────────────────────────────────────────────────────

class TestArithmetic:
    def test_addition(self):
        assert run_one("int x; x = 3 + 4; printf(x);") == "7"

    def test_subtraction(self):
        assert run_one("int x; x = 10 - 3; printf(x);") == "7"

    def test_multiplication(self):
        assert run_one("int x; x = 3 * 4; printf(x);") == "12"

    def test_operator_precedence(self):
        # T3: 6 + 4 * 2 = 14, not 20
        assert run_one("int c; int a; int b; a = 6; b = 4; c = a + b * 2; printf(c);") == "14"

    def test_parentheses(self):
        # T11: (2 + 3) * 4 = 20
        assert run_one("int r; r = (2 + 3) * 4; printf(r);") == "20"

    def test_integer_division(self):
        # T4: 7 / 2 = 3 (floor)
        assert run_one("int x; x = 7 / 2; printf(x);") == "3"

    def test_float_division(self):
        # T5: 7.0 / 2.0 = 3.5
        assert run_one("float x; x = 7.0 / 2.0; printf(x);") == "3.5"

    def test_unary_minus(self):
        # T12
        assert run_one("int x; x = -5; printf(x);") == "-5"

    def test_float_int_mixed(self):
        # T15: 1.5 + 2 = 3.5
        assert run_one("float r; r = 1.5 + 2; printf(r);") == "3.5"

    def test_division_by_zero(self):
        with pytest.raises(RuntimeError_):
            run("int x; x = 1 / 0; printf(x);")


# ── T6–T9: Control flow ───────────────────────────────────────────────────────

class TestControlFlow:
    def test_if_true_branch(self):
        # T6
        assert run_one("int x; x = 5; if (x > 3) { printf(x); }") == "5"

    def test_if_false_branch_skipped(self):
        assert run("int x; x = 1; if (x > 3) { printf(99); }") == []

    def test_if_else_false(self):
        # T7
        src = "int x; x = 2; if (x > 3) { printf(1); } else { printf(0); }"
        assert run_one(src) == "0"

    def test_if_else_true(self):
        src = "int x; x = 5; if (x > 3) { printf(1); } else { printf(0); }"
        assert run_one(src) == "1"

    def test_equality_true(self):
        # T8
        src = "int x; int y; x = 4; y = 4; if (x == y) { printf(1); } else { printf(0); }"
        assert run_one(src) == "1"

    def test_equality_false(self):
        src = "int x; int y; x = 4; y = 5; if (x == y) { printf(1); } else { printf(0); }"
        assert run_one(src) == "0"

    def test_nested_if_else(self):
        # T9
        src = """
            int score;
            score = 75;
            if (score > 90) { printf(1); }
            else { if (score > 50) { printf(2); } else { printf(3); } }
        """
        assert run_one(src) == "2"

    def test_less_than(self):
        src = "int x; x = 2; if (x < 5) { printf(1); } else { printf(0); }"
        assert run_one(src) == "1"


# ── T10: printf ───────────────────────────────────────────────────────────────

class TestPrintf:
    def test_multiple_args(self):
        # T10: printf(a, b) produces "3 7" on one line
        src = "int a; int b; a = 3; b = 7; printf(a, b);"
        assert run_one(src) == "3 7"

    def test_expression_in_printf(self):
        assert run_one("int x; x = 2; printf(x + 3);") == "5"

    def test_multiple_printf_calls(self):
        lines = run("int x; x = 1; printf(x); x = 2; printf(x);")
        assert lines == ["1", "2"]


# ── T13–T14: Semantic errors ──────────────────────────────────────────────────

class TestSemanticErrors:
    def test_undeclared_variable(self):
        # T13
        with pytest.raises(RuntimeError_):
            run("x = 10;")

    def test_use_before_assignment(self):
        # T14
        with pytest.raises(RuntimeError_):
            run("int x; printf(x);")

    def test_redeclaration_in_same_scope(self):
        with pytest.raises(RuntimeError_):
            run("int x; int x;")


# ── Scoping ───────────────────────────────────────────────────────────────────

class TestScoping:
    def test_outer_var_visible_in_block(self):
        src = "int x; x = 42; if (1 > 0) { printf(x); }"
        assert run_one(src) == "42"

    def test_outer_var_modified_in_block(self):
        src = "int x; x = 1; if (1 > 0) { x = 99; } printf(x);"
        assert run_one(src) == "99"

    def test_block_var_does_not_leak(self):
        # Variable declared inside block must not be visible after block
        src = """
            int result;
            result = 0;
            if (1 > 0) {
                int inner;
                inner = 5;
                result = inner;
            }
            printf(result);
        """
        assert run_one(src) == "5"
