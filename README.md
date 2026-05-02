# C-Lite Interpreter

A Python-based interpreter for **C-Lite** — a simplified subset of the C programming language — developed as part of **CO523 – Programming Languages** at the University of Peradeniya.

The interpreter demonstrates the three classical phases of language processing: **lexical analysis**, **syntax analysis**, and **semantic evaluation**.

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

## Architecture

The interpreter is composed of four Python modules, each with a single well-defined responsibility:

| Module           | File             | Responsibility                                                      |
| ---------------- | ---------------- | ------------------------------------------------------------------- |
| Lexical Analyzer | `lexer.py`       | Converts source text into a flat token stream                       |
| AST Nodes        | `ast_nodes.py`   | Defines dataclasses for every node in the Abstract Syntax Tree      |
| Parser           | `parser.py`      | Validates the token stream and builds the AST via recursive descent |
| Interpreter      | `interpreter.py` | Tree-walks the AST, maintains the symbol table, and produces output |
| Entry Point      | `main.py`        | CLI runner, REPL, and built-in test suite                           |

### Lexical Analyzer (`lexer.py`)

A hand-written scanner that processes source text character by character, emitting tokens for keywords, identifiers, integer/float literals, operators, and symbols. Whitespace and comments are silently skipped. A `LexerError` is raised on any unrecognised character.

### Parser (`parser.py`)

A hand-written **recursive descent parser** where each non-terminal in the EBNF grammar corresponds directly to a method in the `Parser` class. Uses LL(1) lookahead to select the correct production rule. Operator precedence is encoded structurally in the grammar hierarchy:

```
comparison > addition > multiplication > unary > primary
```

### Semantic Evaluator (`interpreter.py`)

Tree-walks the AST recursively. A **scoped, linked-chain symbol table** (`SymbolTable`) manages variable state, with each `if`/`else` block creating a new child scope pointing at the enclosing scope.

**Semantic rules enforced:**

- Variables must be declared before assignment or use
- Redeclaration in the same scope is a runtime error
- Reading a declared but unassigned variable is a runtime error
- `int` variables silently truncate float values (C-style semantics)
- Block-scoped variables do not leak into the enclosing scope

---

## Grammar (EBNF)

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

INT_LIT        = digit { digit }
FLOAT_LIT      = digit { digit } '.' digit { digit }
IDENT          = letter { letter | digit | '_' }
```

---

## Usage

### Run a Source File

```bash
python main.py program.c
```

### Interactive REPL

```bash
python main.py
```

Enter C-Lite code line by line. Press **Enter** on a blank line to execute the current buffer. Press **Ctrl-C** to exit.

### Run the Test Suite

```bash
python main.py --test
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

## Test Suite

All **15 built-in test cases** pass, covering:

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

- **`LexerError`** — raised when an unrecognised character is encountered (includes source line number)
- **`ParseError`** — raised when the token stream violates the grammar (includes source line number)
- **`RuntimeError_`** — raised when a semantic rule is violated during execution (includes descriptive message)

---

## Project Info

|                 |                                                  |
| --------------- | ------------------------------------------------ |
| **Course**      | CO523 – Programming Languages                    |
| **Institution** | University of Peradeniya, Faculty of Engineering |
| **Department**  | Computer Engineering                             |
| **Author**      | Janakantha S.M.B.G. (E/20/157)                   |
| **Language**    | Python                                           |
| **License**     | MIT License                                      |
