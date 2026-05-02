"""
CO523 - C-Lite Interpreter
Semantic Evaluator (Tree-Walking Interpreter) + Symbol Table
"""

from .ast_nodes import (
    Program, VarDecl, Assignment, IfStatement, PrintfStatement,
    IntLiteral, FloatLiteral, Identifier, BinaryOp
)


class RuntimeError_(Exception):
    pass


# ── Symbol Table ─────────────────────────────────────────────────────────────

class SymbolTable:
    """
    A scoped symbol table that maps variable names to (type, value) pairs.
    Supports nested scopes via a parent-pointer chain.
    """

    def __init__(self, parent=None):
        self._table  = {}   # name -> {'type': str, 'value': int|float|None}
        self.parent  = parent

    def declare(self, name: str, dtype: str):
        if name in self._table:
            raise RuntimeError_(f"Variable '{name}' already declared in this scope.")
        self._table[name] = {'type': dtype, 'value': None}

    def assign(self, name: str, value):
        scope = self._lookup_scope(name)
        if scope is None:
            raise RuntimeError_(f"Variable '{name}' not declared.")
        entry = scope._table[name]
        # Type coercion / checking
        if entry['type'] == 'int':
            if not isinstance(value, (int, float)):
                raise RuntimeError_(f"Type error: cannot assign {type(value)} to int '{name}'.")
            value = int(value)
        elif entry['type'] == 'float':
            if not isinstance(value, (int, float)):
                raise RuntimeError_(f"Type error: cannot assign {type(value)} to float '{name}'.")
            value = float(value)
        scope._table[name]['value'] = value

    def get(self, name: str):
        scope = self._lookup_scope(name)
        if scope is None:
            raise RuntimeError_(f"Variable '{name}' not declared.")
        entry = scope._table[name]
        if entry['value'] is None:
            raise RuntimeError_(f"Variable '{name}' used before assignment.")
        return entry['value']

    def _lookup_scope(self, name: str):
        if name in self._table:
            return self
        if self.parent:
            return self.parent._lookup_scope(name)
        return None

    def snapshot(self):
        """Return a dict of all visible bindings (for debugging/display)."""
        result = {}
        if self.parent:
            result.update(self.parent.snapshot())
        for name, entry in self._table.items():
            result[name] = entry
        return result


# ── Interpreter ───────────────────────────────────────────────────────────────

class Interpreter:
    def __init__(self, output_callback=None):
        """
        output_callback: callable(str) for printf output.
        Defaults to print().
        """
        self.global_scope  = SymbolTable()
        self._output       = output_callback if output_callback else print

    # ── Public entry point ────────────────────────────────────────────────────

    def execute(self, program: Program):
        self._exec_stmts(program.statements, self.global_scope)

    # ── Statement dispatch ────────────────────────────────────────────────────

    def _exec_stmts(self, stmts, scope: SymbolTable):
        for stmt in stmts:
            self._exec_stmt(stmt, scope)

    def _exec_stmt(self, stmt, scope: SymbolTable):
        if isinstance(stmt, VarDecl):
            scope.declare(stmt.name, stmt.dtype)

        elif isinstance(stmt, Assignment):
            val = self._eval_expr(stmt.expr, scope)
            scope.assign(stmt.name, val)

        elif isinstance(stmt, IfStatement):
            cond = self._eval_expr(stmt.condition, scope)
            child_scope = SymbolTable(parent=scope)
            if cond:
                self._exec_stmts(stmt.then_block, child_scope)
            elif stmt.else_block is not None:
                else_scope = SymbolTable(parent=scope)
                self._exec_stmts(stmt.else_block, else_scope)

        elif isinstance(stmt, PrintfStatement):
            parts = []
            for arg in stmt.args:
                val = self._eval_expr(arg, scope)
                # Format: int prints without decimal, float keeps decimals
                if isinstance(val, float) and val == int(val):
                    parts.append(str(val))
                else:
                    parts.append(str(val))
            self._output(" ".join(parts))

        else:
            raise RuntimeError_(f"Unknown statement type: {type(stmt)}")

    # ── Expression evaluation ─────────────────────────────────────────────────

    def _eval_expr(self, expr, scope: SymbolTable):
        if isinstance(expr, IntLiteral):
            return expr.value

        elif isinstance(expr, FloatLiteral):
            return expr.value

        elif isinstance(expr, Identifier):
            return scope.get(expr.name)

        elif isinstance(expr, BinaryOp):
            left  = self._eval_expr(expr.left,  scope)
            right = self._eval_expr(expr.right, scope)
            op    = expr.op

            if op == '+':  return left + right
            if op == '-':  return left - right
            if op == '*':  return left * right
            if op == '/':
                if right == 0:
                    raise RuntimeError_("Division by zero.")
                # If both int, do integer division
                if isinstance(left, int) and isinstance(right, int):
                    return left // right
                return left / right
            if op == '==': return int(left == right)
            if op == '<':  return int(left <  right)
            if op == '>':  return int(left >  right)
            raise RuntimeError_(f"Unknown operator: {op}")

        raise RuntimeError_(f"Unknown expression type: {type(expr)}")
