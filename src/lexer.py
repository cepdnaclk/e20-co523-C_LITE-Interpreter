"""
CO523 - C-Lite Interpreter
Lexical Analyzer (Scanner)
"""

import re
from enum import Enum, auto


class TokenType(Enum):
    # Data types
    INT     = auto()
    FLOAT   = auto()

    # Control flow keywords
    IF      = auto()
    ELSE    = auto()

    # Built-in I/O
    PRINTF  = auto()

    # Literals
    INT_LIT   = auto()
    FLOAT_LIT = auto()

    # Identifier
    IDENT   = auto()

    # Operators
    PLUS    = auto()
    MINUS   = auto()
    STAR    = auto()
    SLASH   = auto()
    ASSIGN  = auto()
    EQ      = auto()   # ==
    LT      = auto()   # <
    GT      = auto()   # >

    # Symbols
    LPAREN  = auto()
    RPAREN  = auto()
    LBRACE  = auto()
    RBRACE  = auto()
    SEMI    = auto()
    COMMA   = auto()

    # End of file
    EOF     = auto()


KEYWORDS = {
    'int':    TokenType.INT,
    'float':  TokenType.FLOAT,
    'if':     TokenType.IF,
    'else':   TokenType.ELSE,
    'printf': TokenType.PRINTF,
}


class Token:
    def __init__(self, ttype: TokenType, value, line: int):
        self.ttype = ttype
        self.value = value
        self.line  = line

    def __repr__(self):
        return f"Token({self.ttype.name}, {self.value!r}, line={self.line})"


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1
        self.tokens = []

    def error(self, msg):
        raise LexerError(f"[Lexer] Line {self.line}: {msg}")

    def peek(self, offset=0):
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else '\0'

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def skip_whitespace_and_comments(self):
        while self.pos < len(self.source):
            ch = self.peek()
            if ch in (' ', '\t', '\r', '\n'):
                self.advance()
            elif ch == '/' and self.peek(1) == '/':
                # single-line comment
                while self.pos < len(self.source) and self.peek() != '\n':
                    self.advance()
            elif ch == '/' and self.peek(1) == '*':
                # multi-line comment
                self.advance(); self.advance()
                while self.pos < len(self.source):
                    if self.peek() == '*' and self.peek(1) == '/':
                        self.advance(); self.advance()
                        break
                    self.advance()
            else:
                break

    def read_number(self):
        start = self.pos
        is_float = False
        while self.pos < len(self.source) and self.peek().isdigit():
            self.advance()
        if self.peek() == '.' and self.peek(1).isdigit():
            is_float = True
            self.advance()
            while self.pos < len(self.source) and self.peek().isdigit():
                self.advance()
        lexeme = self.source[start:self.pos]
        if is_float:
            return Token(TokenType.FLOAT_LIT, float(lexeme), self.line)
        else:
            return Token(TokenType.INT_LIT, int(lexeme), self.line)

    def read_ident_or_keyword(self):
        start = self.pos
        while self.pos < len(self.source) and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()
        lexeme = self.source[start:self.pos]
        ttype  = KEYWORDS.get(lexeme, TokenType.IDENT)
        return Token(ttype, lexeme, self.line)

    def tokenize(self):
        single = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ';': TokenType.SEMI,
            ',': TokenType.COMMA,
            '<': TokenType.LT,
            '>': TokenType.GT,
        }

        while True:
            self.skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                self.tokens.append(Token(TokenType.EOF, None, self.line))
                break

            ch = self.peek()

            if ch.isdigit():
                self.tokens.append(self.read_number())

            elif ch.isalpha() or ch == '_':
                self.tokens.append(self.read_ident_or_keyword())

            elif ch == '=' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.tokens.append(Token(TokenType.EQ, '==', self.line))

            elif ch == '=':
                self.advance()
                self.tokens.append(Token(TokenType.ASSIGN, '=', self.line))

            elif ch in single:
                self.advance()
                self.tokens.append(Token(single[ch], ch, self.line))

            else:
                self.error(f"Unexpected character: {ch!r}")

        return self.tokens
