"""
CO523 - C-Lite Interpreter
Main Entry Point

Usage:
    python main.py <source_file.c>     # run a C-Lite source file
    python main.py                      # interactive REPL
    python main.py --test               # run built-in test suite
"""

import sys
from src.lexer       import Lexer,       LexerError
from src.parser      import Parser,      ParseError
from src.interpreter import Interpreter, RuntimeError_


def run_source(source: str, show_tokens=False, show_ast=False) -> list[str]:
    """
    Lex → Parse → Evaluate a C-Lite source string.
    Returns list of output lines produced by printf.
    """
    output_lines = []

    # 1. Lexical analysis
    lexer  = Lexer(source)
    tokens = lexer.tokenize()
    if show_tokens:
        print("\n── Tokens ──────────────────────────────────")
        for tok in tokens:
            print(f"  {tok}")

    # 2. Syntax analysis
    parser  = Parser(tokens)
    program = parser.parse()
    if show_ast:
        print("\n── AST ─────────────────────────────────────")
        for stmt in program.statements:
            print(f"  {stmt}")

    # 3. Semantic evaluation
    interp = Interpreter(output_callback=lambda s: output_lines.append(s))
    interp.execute(program)

    return output_lines


def run_file(path: str):
    try:
        with open(path) as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {path}")
        sys.exit(1)

    try:
        lines = run_source(source)
        for line in lines:
            print(line)
    except (LexerError, ParseError, RuntimeError_) as e:
        print(e)
        sys.exit(1)


def repl():
    print("C-Lite Interpreter  (CO523 - University of Peradeniya)")
    print("Type C-Lite code. Enter a blank line to execute. Ctrl-C to quit.\n")
    while True:
        try:
            lines = []
            while True:
                line = input(">>> " if not lines else "... ")
                if line == "" and lines:
                    break
                lines.append(line)
            source = "\n".join(lines)
            if not source.strip():
                continue
            output = run_source(source)
            for o in output:
                print(o)
        except (LexerError, ParseError, RuntimeError_) as e:
            print(e)
        except KeyboardInterrupt:
            print("\nBye.")
            break
        except EOFError:
            print()
            break


# ── Built-in Test Suite ───────────────────────────────────────────────────────

TESTS = [
    {
        "name": "T1 – Integer declaration and assignment",
        "source": """
            int x;
            x = 10;
            printf(x);
        """,
        "expected": ["10"],
    },
    {
        "name": "T2 – Float declaration and assignment",
        "source": """
            float pi;
            pi = 3.14;
            printf(pi);
        """,
        "expected": ["3.14"],
    },
    {
        "name": "T3 – Arithmetic operations",
        "source": """
            int a;
            int b;
            int c;
            a = 6;
            b = 4;
            c = a + b * 2;
            printf(c);
        """,
        "expected": ["14"],
    },
    {
        "name": "T4 – Integer division",
        "source": """
            int x;
            x = 7 / 2;
            printf(x);
        """,
        "expected": ["3"],
    },
    {
        "name": "T5 – Float division",
        "source": """
            float x;
            x = 7.0 / 2.0;
            printf(x);
        """,
        "expected": ["3.5"],
    },
    {
        "name": "T6 – if (true branch)",
        "source": """
            int x;
            x = 5;
            if (x > 3) {
                printf(x);
            }
        """,
        "expected": ["5"],
    },
    {
        "name": "T7 – if-else (false branch)",
        "source": """
            int x;
            x = 2;
            if (x > 3) {
                printf(1);
            } else {
                printf(0);
            }
        """,
        "expected": ["0"],
    },
    {
        "name": "T8 – Equality comparison",
        "source": """
            int x;
            int y;
            x = 4;
            y = 4;
            if (x == y) {
                printf(1);
            } else {
                printf(0);
            }
        """,
        "expected": ["1"],
    },
    {
        "name": "T9 – Nested if-else",
        "source": """
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
        """,
        "expected": ["2"],
    },
    {
        "name": "T10 – Multiple printf args",
        "source": """
            int a;
            int b;
            a = 3;
            b = 7;
            printf(a, b);
        """,
        "expected": ["3 7"],
    },
    {
        "name": "T11 – Parenthesised expression",
        "source": """
            int result;
            result = (2 + 3) * 4;
            printf(result);
        """,
        "expected": ["20"],
    },
    {
        "name": "T12 – Unary minus",
        "source": """
            int x;
            x = -5;
            printf(x);
        """,
        "expected": ["-5"],
    },
    {
        "name": "T13 – Undeclared variable (error)",
        "source": """
            x = 10;
        """,
        "expected_error": True,
    },
    {
        "name": "T14 – Use before assignment (error)",
        "source": """
            int x;
            printf(x);
        """,
        "expected_error": True,
    },
    {
        "name": "T15 – Float + int expression (type widening)",
        "source": """
            float result;
            result = 1.5 + 2;
            printf(result);
        """,
        "expected": ["3.5"],
    },
]


def run_tests():
    passed = failed = 0
    print("=" * 60)
    print("C-Lite Interpreter – Test Suite")
    print("=" * 60)
    for t in TESTS:
        name       = t["name"]
        source     = t["source"]
        expect_err = t.get("expected_error", False)
        expected   = t.get("expected", [])
        try:
            output = run_source(source)
            if expect_err:
                print(f"  FAIL  {name}")
                print(f"        Expected an error but got: {output}")
                failed += 1
            elif output == expected:
                print(f"  PASS  {name}")
                passed += 1
            else:
                print(f"  FAIL  {name}")
                print(f"        Expected: {expected}")
                print(f"        Got:      {output}")
                failed += 1
        except (LexerError, ParseError, RuntimeError_) as e:
            if expect_err:
                print(f"  PASS  {name}  (error: {e})")
                passed += 1
            else:
                print(f"  FAIL  {name}")
                print(f"        Unexpected error: {e}")
                failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(TESTS)} tests")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--test":
        ok = run_tests()
        sys.exit(0 if ok else 1)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        repl()
