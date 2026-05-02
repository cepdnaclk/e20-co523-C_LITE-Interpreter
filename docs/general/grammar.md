# C-Lite Grammar Reference

This document specifies the complete formal grammar for the C-Lite language, expressed in Extended Backus-Naur Form (EBNF).

## Notation

| Notation | Meaning |
|---|---|
| `{ X }` | Zero or more repetitions of X |
| `[ X ]` | Zero or one occurrence of X (optional) |
| `( X \| Y )` | X or Y (choice) |
| `'keyword'` | Terminal literal |

---

## Grammar

### Top-Level

```ebnf
program = { statement } EOF
```

### Statements

```ebnf
statement   = var_decl
            | assignment
            | if_stmt
            | printf_stmt

var_decl    = type IDENT ';'
type        = 'int' | 'float'

assignment  = IDENT '=' expr ';'

if_stmt     = 'if' '(' expr ')' block [ 'else' block ]
block       = '{' { statement } '}'

printf_stmt = 'printf' '(' arg_list ')' ';'
arg_list    = expr { ',' expr }
```

### Expressions

The expression grammar encodes operator precedence through rule stratification. Each level may only call downward into a higher-precedence level.

```ebnf
expr           = comparison

comparison     = addition { ( '==' | '<' | '>' ) addition }

addition       = multiplication { ( '+' | '-' ) multiplication }

multiplication = unary { ( '*' | '/' ) unary }

unary          = '-' unary
               | primary

primary        = INT_LIT
               | FLOAT_LIT
               | IDENT
               | '(' expr ')'
```

### Lexical Tokens

```ebnf
INT_LIT   = digit { digit }
FLOAT_LIT = digit { digit } '.' digit { digit }
IDENT     = letter { letter | digit | '_' }

digit     = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'
letter    = 'a' | ... | 'z' | 'A' | ... | 'Z'
```

---

## Operator Precedence Table

From lowest to highest:

| Level | Operators | Associativity |
|---|---|---|
| 1 (lowest) | `==` `<` `>` | Left |
| 2 | `+` `-` | Left |
| 3 | `*` `/` | Left |
| 4 (highest) | unary `-` | Right |

Parentheses `( expr )` may be used at any level to override precedence.

---

## Notes

- The grammar is **LL(1)** compatible — the correct production can always be selected with a single token of lookahead, enabling a clean recursive descent parser without backtracking.
- **Integer division:** When both operands are `int`, `/` performs floor division (consistent with C semantics).
- **Type coercion:** Assigning a `float` to an `int` variable silently truncates; assigning an `int` to a `float` variable widens it.
- **Block scoping:** Variables declared inside an `if` or `else` block are destroyed when execution leaves that block. Inner scopes can read and modify variables from outer scopes.
