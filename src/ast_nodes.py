"""
CO523 - C-Lite Interpreter
Abstract Syntax Tree (AST) Node Definitions
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union


# ── Expressions ──────────────────────────────────────────────────────────────

@dataclass
class IntLiteral:
    value: int

@dataclass
class FloatLiteral:
    value: float

@dataclass
class Identifier:
    name: str

@dataclass
class BinaryOp:
    op: str          # '+' '-' '*' '/' '==' '<' '>'
    left:  "Expr"
    right: "Expr"

Expr = Union[IntLiteral, FloatLiteral, Identifier, BinaryOp]


# ── Statements ────────────────────────────────────────────────────────────────

@dataclass
class VarDecl:
    dtype: str       # 'int' or 'float'
    name:  str

@dataclass
class Assignment:
    name:  str
    expr:  Expr

@dataclass
class IfStatement:
    condition:   Expr
    then_block:  List["Stmt"]
    else_block:  Optional[List["Stmt"]] = field(default=None)

@dataclass
class PrintfStatement:
    args: List[Expr]   # simplified: list of expressions to print

@dataclass
class Block:
    statements: List["Stmt"]

Stmt = Union[VarDecl, Assignment, IfStatement, PrintfStatement, Block]


# ── Program ───────────────────────────────────────────────────────────────────

@dataclass
class Program:
    statements: List[Stmt]
