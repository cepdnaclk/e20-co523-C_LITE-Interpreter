"""
tests/test_lexer.py
Unit tests for the C-Lite Lexical Analyzer.
"""

import pytest
from src.lexer import Lexer, LexerError, TokenType


def tokenize(source: str):
    return Lexer(source).tokenize()


def types(source: str):
    """Return just the TokenType sequence (excluding EOF)."""
    return [t.ttype for t in tokenize(source) if t.ttype != TokenType.EOF]


def values(source: str):
    """Return just the token values (excluding EOF)."""
    return [t.value for t in tokenize(source) if t.ttype != TokenType.EOF]


# ── Keywords ──────────────────────────────────────────────────────────────────

class TestKeywords:
    def test_int_keyword(self):
        assert types("int") == [TokenType.INT]

    def test_float_keyword(self):
        assert types("float") == [TokenType.FLOAT]

    def test_if_keyword(self):
        assert types("if") == [TokenType.IF]

    def test_else_keyword(self):
        assert types("else") == [TokenType.ELSE]

    def test_printf_keyword(self):
        assert types("printf") == [TokenType.PRINTF]

    def test_keyword_not_prefix_matched(self):
        # 'integer' should be IDENT, not INT + IDENT
        toks = [t for t in tokenize("integer") if t.ttype != TokenType.EOF]
        assert len(toks) == 1
        assert toks[0].ttype == TokenType.IDENT
        assert toks[0].value == "integer"


# ── Literals ──────────────────────────────────────────────────────────────────

class TestLiterals:
    def test_integer_literal(self):
        toks = [t for t in tokenize("42") if t.ttype != TokenType.EOF]
        assert toks[0].ttype == TokenType.INT_LIT
        assert toks[0].value == 42

    def test_float_literal(self):
        toks = [t for t in tokenize("3.14") if t.ttype != TokenType.EOF]
        assert toks[0].ttype == TokenType.FLOAT_LIT
        assert toks[0].value == pytest.approx(3.14)

    def test_zero(self):
        assert types("0") == [TokenType.INT_LIT]

    def test_multi_digit(self):
        toks = [t for t in tokenize("1000") if t.ttype != TokenType.EOF]
        assert toks[0].value == 1000

    def test_float_with_leading_zero(self):
        toks = [t for t in tokenize("0.5") if t.ttype != TokenType.EOF]
        assert toks[0].ttype == TokenType.FLOAT_LIT
        assert toks[0].value == pytest.approx(0.5)


# ── Identifiers ───────────────────────────────────────────────────────────────

class TestIdentifiers:
    def test_simple_ident(self):
        toks = [t for t in tokenize("foo") if t.ttype != TokenType.EOF]
        assert toks[0].ttype == TokenType.IDENT
        assert toks[0].value == "foo"

    def test_ident_with_digits(self):
        toks = [t for t in tokenize("x1") if t.ttype != TokenType.EOF]
        assert toks[0].ttype == TokenType.IDENT

    def test_ident_with_underscore(self):
        toks = [t for t in tokenize("my_var") if t.ttype != TokenType.EOF]
        assert toks[0].ttype == TokenType.IDENT
        assert toks[0].value == "my_var"

    def test_underscore_start(self):
        toks = [t for t in tokenize("_x") if t.ttype != TokenType.EOF]
        assert toks[0].ttype == TokenType.IDENT


# ── Operators & Symbols ───────────────────────────────────────────────────────

class TestOperatorsAndSymbols:
    def test_single_char_operators(self):
        assert types("+ - * /") == [
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH
        ]

    def test_assign(self):
        assert types("=") == [TokenType.ASSIGN]

    def test_double_eq(self):
        assert types("==") == [TokenType.EQ]

    def test_lt_gt(self):
        assert types("< >") == [TokenType.LT, TokenType.GT]

    def test_symbols(self):
        assert types("( ) { } ; ,") == [
            TokenType.LPAREN, TokenType.RPAREN,
            TokenType.LBRACE, TokenType.RBRACE,
            TokenType.SEMI, TokenType.COMMA,
        ]

    def test_assign_not_eq(self):
        # Single '=' must NOT become EQ
        toks = [t for t in tokenize("x = 1") if t.ttype != TokenType.EOF]
        op = toks[1]
        assert op.ttype == TokenType.ASSIGN


# ── Whitespace & Comments ─────────────────────────────────────────────────────

class TestWhitespaceAndComments:
    def test_whitespace_skipped(self):
        assert types("  int   x  ;  ") == [TokenType.INT, TokenType.IDENT, TokenType.SEMI]

    def test_newlines_skipped(self):
        assert types("int\nx\n;") == [TokenType.INT, TokenType.IDENT, TokenType.SEMI]

    def test_single_line_comment(self):
        assert types("int x; // this is a comment") == [
            TokenType.INT, TokenType.IDENT, TokenType.SEMI
        ]

    def test_multi_line_comment(self):
        assert types("int /* hello\nworld */ x;") == [
            TokenType.INT, TokenType.IDENT, TokenType.SEMI
        ]


# ── Line Tracking ─────────────────────────────────────────────────────────────

class TestLineTracking:
    def test_line_number(self):
        toks = tokenize("int x;\nfloat y;")
        # 'float' should be on line 2
        float_tok = next(t for t in toks if t.ttype == TokenType.FLOAT)
        assert float_tok.line == 2


# ── Error Handling ────────────────────────────────────────────────────────────

class TestErrors:
    def test_unrecognised_character(self):
        with pytest.raises(LexerError):
            tokenize("int @x;")

    def test_hash_is_invalid(self):
        with pytest.raises(LexerError):
            tokenize("#include")


# ── EOF ───────────────────────────────────────────────────────────────────────

class TestEOF:
    def test_empty_source_produces_eof(self):
        toks = tokenize("")
        assert toks[-1].ttype == TokenType.EOF

    def test_eof_always_last(self):
        toks = tokenize("int x;")
        assert toks[-1].ttype == TokenType.EOF
