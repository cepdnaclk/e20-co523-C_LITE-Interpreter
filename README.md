# C-Lite Interpreter

A Python-based interpreter for **C-Lite** — a simplified subset of the C programming language — developed as part of **CO523 – Programming Languages** at the University of Peradeniya.

The interpreter demonstrates the three classical phases of language processing: **lexical analysis**, **syntax analysis**, and **semantic evaluation**.

---

## Repository Structure

```
clite-interpreter/
├── src/                    # Interpreter source modules
│   ├── __init__.py         # Package exports
│   ├── lexer.py            # Lexical Analyzer (Scanner)
│   ├── ast_nodes.py        # AST Node dataclasses
│   ├── parser.py           # Recursive Descent Parser
│   └── interpreter.py      # Tree-Walking Interpreter + Symbol Table
├── docs/                   # Documentation
│   ├── grammar.md          # Full EBNF grammar reference
│   └── design.md           # Architecture & design decisions
├── tests/                  # pytest test suite
│   ├── __init__.py
│   ├── test_lexer.py       # 27 lexer unit tests
│   ├── test_parser.py      # 34 parser unit tests
│   └── test_interpreter.py # 31 interpreter integration tests
├── examples/               # Sample C-Lite programs
│   └── sample.c
├── main.py                 # CLI entry point (file runner, REPL, test suite)
├── requirements.txt
└── .gitignore
```

---

## Features

C-Lite supports the following language constructs:

- **Data Types:** `int` (32-bit integer) and `float` (double-precision floating-point)
- **Variable Declarations:** Variables must be declared before use (e.g., `int x;`)
- **Assignment:** Single assignment operator `=`
- **Arithmetic Operators:** `+`, `-`, `*`, `/` with correct operator precedence
- **Comparison Operators:** `>`, `<`, `==`
- **Control Structures:** Sequential execution and `if`/`else` conditional branching
- **Standard I/O:** Built-in `printf()` for outputting values to the console
- **Comments:** Single-line (`//`) and multi-line (`/* */`)

---

## Getting Started

### Prerequisites

- Python 3.10+
- pytest (for running the test suite)

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run a source file

```bash
python main.py examples/sample.c
```

### Interactive REPL

```bash
python main.py
```

Enter C-Lite code line by line. Press **Enter** on a blank line to execute the current buffer. Press **Ctrl-C** to exit.

### Built-in test suite

```bash
python main.py --test
```

### pytest test suite

```bash
pytest tests/
```

---

## Architecture

The interpreter is a pipeline of four modules inside `src/`. Each module has a single responsibility and communicates with the next through a clean interface.

| Module           | File                 | Responsibility                                                      |
| ---------------- | -------------------- | ------------------------------------------------------------------- |
| Lexical Analyzer | `src/lexer.py`       | Converts source text into a flat token stream                       |
| AST Nodes        | `src/ast_nodes.py`   | Defines dataclasses for every node in the Abstract Syntax Tree      |
| Parser           | `src/parser.py`      | Validates the token stream and builds the AST via recursive descent |
| Interpreter      | `src/interpreter.py` | Tree-walks the AST, maintains the symbol table, and produces output |
| Entry Point      | `main.py`            | CLI runner, REPL, and built-in test suite                           |

### Lexical Analyzer (`src/lexer.py`)

A hand-written scanner that processes source text character by character, emitting tokens for keywords, identifiers, integer/float literals, operators, and symbols. Whitespace and comments are silently skipped. A `LexerError` is raised on any unrecognised character.

### Parser (`src/parser.py`)

A hand-written **recursive descent parser** where each non-terminal in the EBNF grammar corresponds directly to a method in the `Parser` class. Uses LL(1) lookahead to select the correct production rule. Operator precedence is encoded structurally in the grammar hierarchy:

```
comparison > addition > multiplication > unary > primary
```

### Semantic Evaluator (`src/interpreter.py`)

Tree-walks the AST recursively. A **scoped, linked-chain symbol table** (`SymbolTable`) manages variable state, with each `if`/`else` block creating a new child scope pointing at the enclosing scope.

**Semantic rules enforced:**

- Variables must be declared before assignment or use
- Redeclaration in the same scope is a runtime error
- Reading a declared but unassigned variable is a runtime error
- `int` variables silently truncate float values (C-style semantics)
- Block-scoped variables do not leak into the enclosing scope

---

## Grammar (EBNF)

See [`docs/grammar.md`](docs/grammar.md) for the full reference with precedence table. A summary:

```ebnf
program        = { statement } EOF

statement      = var_decl | assignment | if_stmt | printf_stmt

var_decl       = type IDENT ';'
type           = 'int' | 'float'
assignment     = IDENT '=' expr ';'
if_stmt        = 'if' '(' expr ')' block [ 'else' block ]
block          = '{' { statement } '}'
printf_stmt    = 'printf' '(' arg_list ')' ';'
arg_list       = expr { ',' expr }

expr           = comparison
comparison     = addition { ( '==' | '<' | '>' ) addition }
addition       = multiplication { ( '+' | '-' ) multiplication }
multiplication = unary { ( '*' | '/' ) unary }
unary          = '-' unary | primary
primary        = INT_LIT | FLOAT_LIT | IDENT | '(' expr ')'
```

---

## Sample Programs

### Simple Arithmetic

```c
int a;
int b;
int c;
a = 10;
b = 3;
c = a * b + 1;
printf(c);
```

**Output:** `31`

### Conditional Logic

```c
int score;
score = 75;
if (score > 90) {
    printf(1);
} else {
    if (score > 50) {
        printf(2);
    } else {
        printf(3);
    }
}
```

**Output:** `2`

### Float Computation

```c
float radius;
float area;
radius = 5.0;
area = 3.14 * radius * radius;
printf(area);
```

**Output:** `78.5`

---

## Tests

The project has two test layers:

**Built-in suite** (`python main.py --test`) — 15 hand-written cases covering the core language features, run without any external dependencies.

**pytest suite** (`pytest tests/`) — 92 unit and integration tests organized by module:

| File                        | Tests | Coverage                                                                    |
| --------------------------- | ----- | --------------------------------------------------------------------------- |
| `tests/test_lexer.py`       | 27    | Keywords, literals, identifiers, operators, comments, line tracking, errors |
| `tests/test_parser.py`      | 34    | AST shape, operator precedence, all statement types, error cases            |
| `tests/test_interpreter.py` | 31    | Types, arithmetic, control flow, scoping, semantic errors                   |

| ID  | Feature Tested                                    |
| --- | ------------------------------------------------- |
| T1  | `int` type, declaration, assignment               |
| T2  | `float` type, float literals                      |
| T3  | Operator precedence (`*` before `+`)              |
| T4  | Integer division (`int / int` = floor division)   |
| T5  | Float division (`float / float` = true division)  |
| T6  | `if` with true condition                          |
| T7  | `if-else` with false condition                    |
| T8  | Equality comparison (`==`)                        |
| T9  | Nested `if-else`                                  |
| T10 | `printf` with multiple comma-separated arguments  |
| T11 | Grouping with parentheses                         |
| T12 | Unary minus                                       |
| T13 | Semantic error: undeclared variable               |
| T14 | Semantic error: use before assignment             |
| T15 | Mixed-type arithmetic (float + int type widening) |

---

## Error Handling

Three distinct exception classes provide clean separation of concerns:

| Exception       | Raised in            | Carries                             |
| --------------- | -------------------- | ----------------------------------- |
| `LexerError`    | `src/lexer.py`       | Source line number                  |
| `ParseError`    | `src/parser.py`      | Source line number + expected token |
| `RuntimeError_` | `src/interpreter.py` | Descriptive message                 |

---

## Documentation

| Document                                                                             | Description                                                                                                          |
| ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| [`general/grammar.md`](general/grammar.md)                                           | Full EBNF grammar with operator precedence table and scoping notes                                                   |
| [`general/design.md`](general/design.md)                                             | Architecture overview, module responsibilities, and key design decisions                                             |
| [`general/CO523_CLite_Report.pdf`](general/CO523_CLite_Report.pdf)                   | Comprehensive report covering all aspects of the project, including design, implementation, testing, and reflections |
| [`general/CO523_Project_Specification.pdf`](general/CO523_Project_Specification.pdf) | Original project specification provided by the course instructors                                                    |

---

## Project Info

|                 |                                                  |
| --------------- | ------------------------------------------------ |
| **Course**      | CO523 – Programming Languages                    |
| **Institution** | University of Peradeniya, Faculty of Engineering |
| **Department**  | Computer Engineering                             |
| **Author**      | Janakantha S.M.B.G. (E/20/157)                   |
| **Language**    | Python 3.10+                                     |
| **License**     | MIT License                                      |
