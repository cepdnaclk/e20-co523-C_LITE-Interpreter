# C-Lite Interpreter — Design Notes

This document explains the key architectural and design decisions made in the C-Lite interpreter.

---

## Module Overview

```
clite-interpreter/
├── src/
│   ├── lexer.py        Lexical Analyzer (Scanner)
│   ├── ast_nodes.py    AST Node Dataclasses
│   ├── parser.py       Recursive Descent Parser
│   └── interpreter.py  Tree-Walking Interpreter + Symbol Table
├── tests/              pytest test suite
├── examples/           Sample C-Lite programs
└── main.py             CLI entry point
```

Each module has a single well-defined responsibility and communicates with the next through a clean interface: `Lexer` produces a token list, `Parser` consumes it and produces a `Program` AST, `Interpreter` consumes the AST and produces output.

---

## Lexical Analyzer (`lexer.py`)

The lexer is a hand-written character-by-character scanner. Design decisions:

- **Single-pass:** The entire source string is scanned in one linear pass, with no backtracking beyond one character of lookahead (`peek(1)`), needed only to distinguish `=` from `==` and `//` from `/`.
- **Line tracking:** A `line` counter is incremented on every `\n`, enabling precise error messages for both the lexer and parser.
- **Comment handling:** Single-line (`//`) and multi-line (`/* */`) comments are silently consumed during whitespace skipping, before any token is emitted.
- **Keyword disambiguation:** Identifiers are read greedily first, then checked against a `KEYWORDS` dict. This ensures that `integer` is classified as `IDENT`, not `INT` + `EGER`.

---

## Abstract Syntax Tree (`ast_nodes.py`)

AST nodes are Python `dataclasses`, chosen for:

- **Immutability by default** — nodes are pure data containers with no methods, keeping the tree structure separate from the execution logic.
- **Readable `repr`** — dataclasses auto-generate `__repr__`, which is useful for the `--ast` debug flag in `main.py`.
- **Type aliases** — `Expr` and `Stmt` are `Union` type aliases that document which node kinds are valid in each position.

---

## Parser (`parser.py`)

The parser is a hand-written **recursive descent parser**. Each non-terminal in the EBNF grammar maps directly to a method:

| Grammar Rule | Method |
|---|---|
| `program` | `parse()` |
| `statement` | `statement()` |
| `var_decl` | `var_decl()` |
| `assignment` | `assignment()` |
| `if_stmt` | `if_stmt()` |
| `block` | `block()` |
| `printf_stmt` | `printf_stmt()` |
| `expr` / `comparison` / ... | `expr()`, `comparison()`, ... |

### Operator Precedence via Grammar Stratification

Precedence is encoded structurally rather than through an explicit precedence table. The expression grammar forms a chain of rules where each level calls downward into the next higher-precedence level:

```
comparison → addition → multiplication → unary → primary
```

This guarantees that `*` and `/` bind more tightly than `+` and `-`, which bind more tightly than comparison operators — matching standard C semantics — with no disambiguation logic needed at runtime.

### LL(1) Compatibility

Every production rule can be selected with a single token of lookahead (`peek_type()`). The `statement()` dispatcher uses this lookahead:

- `INT` or `FLOAT` → `var_decl()`
- `IF` → `if_stmt()`
- `PRINTF` → `printf_stmt()`
- `IDENT` → `assignment()`

---

## Symbol Table (`interpreter.py — SymbolTable`)

The `SymbolTable` is a **scoped, parent-pointer chain**:

```
global_scope
    └── if_scope (child of global)
            └── nested_if_scope (child of if_scope)
```

Each `SymbolTable` instance holds a dict of `name → {type, value}` records and a reference to its `parent`. Variable lookup (`_lookup_scope`) walks the chain upward until the name is found or the chain is exhausted.

This design:
- Correctly models C's **block scoping** — inner scopes see outer variables but outer scopes don't see inner ones.
- Scales to **arbitrary nesting depth** without global state.
- Makes scope **creation and destruction** trivial — a new child scope is created on entering a block and simply goes out of reference when the block finishes.

---

## Type System

C-Lite enforces a simple type system **at the point of assignment**:

| Variable type | Value being stored | Result |
|---|---|---|
| `int` | `int` | stored as-is |
| `int` | `float` | truncated to `int` (C-style) |
| `float` | `float` | stored as-is |
| `float` | `int` | widened to `float` |

Type coercion happens in `SymbolTable.assign()`. Binary operations between `int` and `float` naturally produce a Python `float` via Python's numeric tower, which is then subject to coercion when stored.

---

## Integer vs Float Division

The `/` operator mirrors C semantics:

- Both operands are Python `int` → **floor division** (`//`)
- Either operand is Python `float` → **true division** (`/`)

This is implemented in `Interpreter._eval_expr()` with an `isinstance` check on the evaluated operand values.

---

## Error Handling

Three distinct exception classes provide clean separation of concerns:

| Exception | Raised by | Carries |
|---|---|---|
| `LexerError` | `lexer.py` | Source line number |
| `ParseError` | `parser.py` | Source line number + expected token |
| `RuntimeError_` | `interpreter.py` | Descriptive message |

`RuntimeError_` uses a trailing underscore to avoid shadowing Python's built-in `RuntimeError`.
