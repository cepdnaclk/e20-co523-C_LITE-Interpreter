// CO523 - C-Lite Sample Program
// Demonstrates all supported language features

// --- Integer and Float Declarations ---
int a;
int b;
int result;
float x;
float y;
float avg;

// --- Basic Assignments ---
a = 10;
b = 3;
x = 5.5;
y = 2.5;

// --- Arithmetic Operations ---
result = a + b * 2;
printf(result);

// --- Integer Division (floor) ---
result = a / b;
printf(result);

// --- Float Arithmetic ---
avg = (x + y) / 2.0;
printf(avg);

// --- Comparison: greater than ---
if (a > b) {
    printf(1);
} else {
    printf(0);
}

// --- Comparison: less than ---
if (b < a) {
    printf(1);
} else {
    printf(0);
}

// --- Equality check ---
int p;
int q;
p = 7;
q = 7;
if (p == q) {
    printf(1);
} else {
    printf(0);
}

// --- Nested if-else (grade classifier) ---
int score;
score = 82;

if (score > 90) {
    printf(1);
} else {
    if (score > 75) {
        printf(2);
    } else {
        if (score > 50) {
            printf(3);
        } else {
            printf(4);
        }
    }
}

// --- Multiple printf arguments ---
printf(a, b, result);

// --- Unary minus ---
int neg;
neg = -99;
printf(neg);

// --- Float assigned from int expression ---
float f;
f = 4.0 * 2.0 + 1.5;
printf(f);
