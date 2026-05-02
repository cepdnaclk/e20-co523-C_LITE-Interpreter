"""
CO523 - C-Lite Interpreter
Syntax Analyzer (Recursive Descent Parser)

Grammar (EBNF):
    program       = { statement } EOF
    statement     = var_decl | assignment | if_stmt | printf_stmt
    var_decl      = type IDENT ';'
    type          = 'int' | 'float'
    assignment    = IDENT '=' expr ';'
    if_stmt       = 'if' '(' expr ')' block [ 'else' block ]
    block         = '{' { statement } '}'
    printf_stmt   = 'printf' '(' arg_list ')' ';'
    arg_list      = expr { ',' expr }
    expr          = comparison
    comparison    = addition { ( '==' | '<' | '>' ) addition }
    addition      = multiplication { ( '+' | '-' ) multiplication }
    multiplication= unary { ( '*' | '/' ) unary }
    unary         = ( '-' unary ) | primary
    primary       = INT_LIT | FLOAT_LIT | IDENT | '(' expr ')'
"""

from .lexer import TokenType, Token
from .ast_nodes import (
    Program, VarDecl, Assignment, IfStatement, PrintfStatement, Block,
    IntLiteral, FloatLiteral, Identifier, BinaryOp
)


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    # ── Helpers ───────────────────────────────────────────────────────────────

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek_type(self) -> TokenType:
        return self.current().ttype

    def match(self, *ttypes) -> bool:
        return self.peek_type() in ttypes

    def expect(self, ttype: TokenType) -> Token:
        tok = self.current()
        if tok.ttype != ttype:
            raise ParseError(
                f"[Parser] Line {tok.line}: Expected {ttype.name}, "
                f"got {tok.ttype.name} ({tok.value!r})"
            )
        self.pos += 1
        return tok

    def advance(self) -> Token:
        tok = self.current()
        self.pos += 1
        return tok

    # ── Grammar rules ─────────────────────────────────────────────────────────

    def parse(self) -> Program:
        stmts = []
        while not self.match(TokenType.EOF):
            stmts.append(self.statement())
        return Program(stmts)

    def statement(self):
        if self.match(TokenType.INT, TokenType.FLOAT):
            return self.var_decl()
        elif self.match(TokenType.IF):
            return self.if_stmt()
        elif self.match(TokenType.PRINTF):
            return self.printf_stmt()
        elif self.match(TokenType.IDENT):
            return self.assignment()
        else:
            tok = self.current()
            raise ParseError(
                f"[Parser] Line {tok.line}: Unexpected token "
                f"{tok.ttype.name} ({tok.value!r})"
            )

    def var_decl(self) -> VarDecl:
        dtype_tok = self.advance()           # int | float
        dtype = dtype_tok.value
        name_tok = self.expect(TokenType.IDENT)
        self.expect(TokenType.SEMI)
        return VarDecl(dtype=dtype, name=name_tok.value)

    def assignment(self) -> Assignment:
        name_tok = self.expect(TokenType.IDENT)
        self.expect(TokenType.ASSIGN)
        expr = self.expr()
        self.expect(TokenType.SEMI)
        return Assignment(name=name_tok.value, expr=expr)

    def if_stmt(self) -> IfStatement:
        self.expect(TokenType.IF)
        self.expect(TokenType.LPAREN)
        cond = self.expr()
        self.expect(TokenType.RPAREN)
        then_block = self.block()
        else_block = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_block = self.block()
        return IfStatement(condition=cond, then_block=then_block, else_block=else_block)

    def block(self):
        self.expect(TokenType.LBRACE)
        stmts = []
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            stmts.append(self.statement())
        self.expect(TokenType.RBRACE)
        return stmts

    def printf_stmt(self) -> PrintfStatement:
        self.expect(TokenType.PRINTF)
        self.expect(TokenType.LPAREN)
        args = [self.expr()]
        while self.match(TokenType.COMMA):
            self.advance()
            args.append(self.expr())
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMI)
        return PrintfStatement(args=args)

    # ── Expression parsing (operator precedence) ──────────────────────────────

    def expr(self):
        return self.comparison()

    def comparison(self):
        left = self.addition()
        while self.match(TokenType.EQ, TokenType.LT, TokenType.GT):
            op_tok = self.advance()
            right  = self.addition()
            left   = BinaryOp(op=op_tok.value, left=left, right=right)
        return left

    def addition(self):
        left = self.multiplication()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self.advance()
            right  = self.multiplication()
            left   = BinaryOp(op=op_tok.value, left=left, right=right)
        return left

    def multiplication(self):
        left = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            op_tok = self.advance()
            right  = self.unary()
            left   = BinaryOp(op=op_tok.value, left=left, right=right)
        return left

    def unary(self):
        if self.match(TokenType.MINUS):
            op_tok = self.advance()
            operand = self.unary()
            # Represent as (0 - operand)
            return BinaryOp(op='-', left=IntLiteral(0), right=operand)
        return self.primary()

    def primary(self):
        tok = self.current()
        if tok.ttype == TokenType.INT_LIT:
            self.advance()
            return IntLiteral(tok.value)
        elif tok.ttype == TokenType.FLOAT_LIT:
            self.advance()
            return FloatLiteral(tok.value)
        elif tok.ttype == TokenType.IDENT:
            self.advance()
            return Identifier(tok.value)
        elif tok.ttype == TokenType.LPAREN:
            self.advance()
            e = self.expr()
            self.expect(TokenType.RPAREN)
            return e
        else:
            raise ParseError(
                f"[Parser] Line {tok.line}: Expected expression, "
                f"got {tok.ttype.name} ({tok.value!r})"
            )
