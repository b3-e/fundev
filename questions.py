"""
questions.py
============
The built-in question bank. Every question is tagged with the syllabus
subtopic it drills (see `subtopic`), grouped under a `category` used for
the sidebar / browse view. Coverage maps onto the WA Computer Science ATAR
Year 12 syllabus, Unit 3 -> "Programming" content area only:

  Control structures, data types, modular coding (functions/scope/parameter
  passing), operators, data structures (arrays/dictionaries), good
  programming practice, structured algorithms (Big O, search, sort),
  testing, error detection & debugging, object-oriented programming, and
  the ethical/legal implications for developers.

Network communications, cyber security and data management (Unit 4) are
deliberately out of scope here.
"""
from __future__ import annotations

from engines import Question, TestCase, OOPCall, OOPScenario, LANG_PYTHON, LANG_PSEUDOCODE

PY = LANG_PYTHON
PC = LANG_PSEUDOCODE
BOTH = (PY, PC)


def _code(id_, title, category, subtopic, prompt, func_name, py_starter, pc_starter,
          test_cases, method_note="", langs=BOTH, difficulty="core"):
    starter = {PY: py_starter}
    if PC in langs:
        starter[PC] = pc_starter
    return Question(
        id=id_, title=title, category=category, subtopic=subtopic, prompt=prompt.strip(),
        qtype="code", langs=langs, func_name=func_name, starter_code=starter,
        test_cases=test_cases, method_note=method_note.strip(), difficulty=difficulty,
    )


def _oop(id_, title, category, subtopic, prompt, class_name, py_starter, scenarios,
         method_note="", difficulty="core"):
    return Question(
        id=id_, title=title, category=category, subtopic=subtopic, prompt=prompt.strip(),
        qtype="oop", langs=(PY,), func_name=class_name, starter_code={PY: py_starter},
        oop_scenarios=scenarios, method_note=method_note.strip(), difficulty=difficulty,
    )


def _quiz(id_, title, category, subtopic, prompt, choices, correct_index, explanation,
          difficulty="core"):
    return Question(
        id=id_, title=title, category=category, subtopic=subtopic, prompt=prompt.strip(),
        qtype="quiz", choices=choices, correct_index=correct_index,
        explanation=explanation.strip(), difficulty=difficulty,
    )


def build_builtin_questions() -> list:
    q = []

    # =========================================================
    # CONTROL STRUCTURES -- sequence / selection / iteration
    # =========================================================
    q.append(_code(
        "cs.rectangle_area", "Rectangle Area", "Control Structures", "Sequence",
        "Write rectangle_area(length, width) that returns the area of a rectangle. "
        "A simple sequence of steps -- no branching or looping needed.",
        "rectangle_area",
        "def rectangle_area(length, width):\n    # A straight sequence: compute and return the area.\n    pass\n",
        "FUNCTION rectangle_area(length, width)\n    # A straight sequence: compute and return the area.\nENDFUNCTION\n",
        [
            TestCase(args=(4, 5), expected=20, label="4 x 5"),
            TestCase(args=(2.5, 4), expected=10.0, label="2.5 x 4 (float)"),
        ],
    ))

    q.append(_code(
        "cs.grade_from_score", "Grade From Score", "Control Structures", "Selection",
        "Write grade_from_score(score) that returns a letter grade using this "
        "boundary table: score >= 80 -> 'A', >= 70 -> 'B', >= 60 -> 'C', >= 50 -> 'D', "
        "otherwise 'E'. Use an IF/ELSEIF/ELSE (or if/elif/else) chain.",
        "grade_from_score",
        "def grade_from_score(score):\n    # if / elif / else chain over the boundaries above.\n    pass\n",
        "FUNCTION grade_from_score(score)\n    # IF / ELSEIF / ELSE chain over the boundaries above.\nENDFUNCTION\n",
        [
            TestCase(args=(95,), expected="A", label="95 -> A"),
            TestCase(args=(75,), expected="B", label="75 -> B"),
            TestCase(args=(65,), expected="C", label="65 -> C"),
            TestCase(args=(55,), expected="D", label="55 -> D"),
            TestCase(args=(30,), expected="E", label="30 -> E"),
            TestCase(args=(80,), expected="A", label="boundary: exactly 80"),
        ],
    ))

    q.append(_code(
        "cs.is_leap_year", "Leap Year Checker", "Control Structures", "Selection",
        "Write is_leap_year(year) returning True if it's a leap year: divisible by 4, "
        "except centuries (divisible by 100) which must also be divisible by 400. "
        "This needs a compound logical expression (AND / OR / NOT).",
        "is_leap_year",
        "def is_leap_year(year):\n    # divisible by 4 AND (NOT divisible by 100 OR divisible by 400)\n    pass\n",
        "FUNCTION is_leap_year(year)\n    # divisible by 4 AND (NOT divisible by 100 OR divisible by 400)\nENDFUNCTION\n",
        [
            TestCase(args=(2024,), expected=True, label="2024 (div by 4)"),
            TestCase(args=(1900,), expected=False, label="1900 (century, not div 400)"),
            TestCase(args=(2000,), expected=True, label="2000 (century, div 400)"),
            TestCase(args=(2023,), expected=False, label="2023 (not div by 4)"),
        ],
    ))

    q.append(_code(
        "cs.sum_first_n", "Sum of First N Numbers", "Control Structures", "Fixed Iteration",
        "Write sum_first_n(n) that returns 1 + 2 + ... + n using a FIXED iteration "
        "(a FOR loop that counts a known number of times) -- not a formula.",
        "sum_first_n",
        "def sum_first_n(n):\n    # Use a for-loop that runs a fixed, known number of times.\n    pass\n",
        "FUNCTION sum_first_n(n)\n    # Use a FOR loop that runs a fixed, known number of times.\nENDFUNCTION\n",
        [
            TestCase(args=(5,), expected=15, label="n=5"),
            TestCase(args=(1,), expected=1, label="n=1"),
            TestCase(
                args=(200,), expected=20100, label="n=200 -- must actually loop",
                min_steps_expr="n*1.2",
            ),
        ],
        method_note="Method check: a closed-form formula (n*(n+1)/2) finishes in ~1 step "
                    "regardless of n and will be rejected on the n=200 case -- this question "
                    "wants a real fixed-count loop.",
    ))

    q.append(_code(
        "cs.collatz_steps", "Collatz Steps", "Control Structures", "Pre-test Iteration",
        "Write collatz_steps(n) using a PRE-TEST loop (condition checked before each "
        "pass, e.g. WHILE): repeatedly apply n = n/2 if n is even, else n = 3*n + 1, "
        "counting steps until n reaches 1. Return the step count.",
        "collatz_steps",
        "def collatz_steps(n):\n    # WHILE n != 1: apply the Collatz rule, counting steps.\n    pass\n",
        "FUNCTION collatz_steps(n)\n    # WHILE n != 1: apply the Collatz rule, counting steps.\nENDFUNCTION\n",
        [
            TestCase(args=(1,), expected=0, label="n=1 -- already done, loop body never runs"),
            TestCase(args=(6,), expected=8, label="n=6"),
            TestCase(args=(27,), expected=111, label="n=27 (long chain)"),
        ],
        method_note="A pre-test (WHILE) loop checks its condition first, so n=1 must "
                    "return 0 without entering the loop body at all.",
    ))

    # =========================================================
    # DATA TYPES
    # =========================================================
    q.append(_code(
        "dt.parse_and_add", "Parse and Add", "Data Types", "Type Casting",
        "Write parse_and_add(a_str, b_str) that takes two strings holding whole "
        "numbers, converts each to an integer, and returns their sum as an integer.",
        "parse_and_add",
        "def parse_and_add(a_str, b_str):\n    # Convert both strings to int, then add.\n    pass\n",
        "FUNCTION parse_and_add(a_str, b_str)\n    # Convert both strings to int using INT(), then add.\nENDFUNCTION\n",
        [
            TestCase(args=("4", "5"), expected=9, label='"4" + "5"'),
            TestCase(args=("120", "-20"), expected=100, label='"120" + "-20"'),
        ],
    ))

    q.append(_code(
        "dt.fahrenheit_to_celsius", "Fahrenheit to Celsius", "Data Types", "Float",
        "Write fahrenheit_to_celsius(f) that converts a Fahrenheit float temperature "
        "to Celsius: (f - 32) * 5 / 9. Return a float.",
        "fahrenheit_to_celsius",
        "def fahrenheit_to_celsius(f):\n    pass\n",
        "FUNCTION fahrenheit_to_celsius(f)\nENDFUNCTION\n",
        [
            TestCase(args=(32,), expected=0.0, label="32F -> 0C"),
            TestCase(args=(212,), expected=100.0, label="212F -> 100C"),
            TestCase(args=(98.6,), expected=37.0, label="98.6F -> 37C"),
        ],
    ))

    # =========================================================
    # FUNCTIONS, PARAMETERS & SCOPE
    # =========================================================
    q.append(_code(
        "fn.increment_copy", "Increment Copy", "Functions & Scope", "Parameter Passing (value)",
        "Write increment_copy(x) that returns x + 1. Simple values like integers are "
        "passed BY VALUE: the function gets its own copy, so this can never change the "
        "caller's original variable -- only what's returned matters.",
        "increment_copy",
        "def increment_copy(x):\n    pass\n",
        "FUNCTION increment_copy(x)\nENDFUNCTION\n",
        [
            TestCase(args=(5,), expected=6, label="5 -> 6"),
            TestCase(args=(-1,), expected=0, label="-1 -> 0"),
        ],
    ))

    q.append(_code(
        "fn.append_bonus", "Append Bonus", "Functions & Scope", "Parameter Passing (reference)",
        "Write append_bonus(scores) that appends the value 99 to the scores array/list "
        "and returns it. Arrays are passed BY REFERENCE: the function is working on the "
        "SAME underlying array the caller has, not a private copy.",
        "append_bonus",
        "def append_bonus(scores):\n    pass\n",
        "FUNCTION append_bonus(scores)\nENDFUNCTION\n",
        [
            TestCase(args=([1, 2, 3],), expected=[1, 2, 3, 99], label="[1,2,3]"),
            TestCase(args=([],), expected=[99], label="empty list"),
        ],
    ))

    q.append(_code(
        "fn.running_total_with_default", "Running Total With Bonus", "Functions & Scope",
        "Parameters & Arguments",
        "Write add_with_bonus(a, b, bonus) that returns a + b + bonus, where bonus is a "
        "normal third parameter (not a default). Call it to see how arguments map onto "
        "parameters in order.",
        "add_with_bonus",
        "def add_with_bonus(a, b, bonus):\n    pass\n",
        "FUNCTION add_with_bonus(a, b, bonus)\nENDFUNCTION\n",
        [
            TestCase(args=(2, 3, 10), expected=15, label="2+3+10"),
            TestCase(args=(0, 0, 0), expected=0, label="all zero"),
        ],
    ))

    # =========================================================
    # OPERATORS & EXPRESSIONS
    # =========================================================
    q.append(_code(
        "op.is_valid_triangle", "Valid Triangle", "Operators & Expressions",
        "Relational + Logical Operators",
        "Write is_valid_triangle(a, b, c) returning True if three side lengths can "
        "form a triangle: all sides positive AND the sum of any two sides is greater "
        "than the third. Combine relational operators with AND/OR.",
        "is_valid_triangle",
        "def is_valid_triangle(a, b, c):\n    pass\n",
        "FUNCTION is_valid_triangle(a, b, c)\nENDFUNCTION\n",
        [
            TestCase(args=(3, 4, 5), expected=True, label="3-4-5 valid"),
            TestCase(args=(1, 1, 3), expected=False, label="1-1-3 invalid (too short)"),
            TestCase(args=(-1, 4, 5), expected=False, label="negative side invalid"),
            TestCase(args=(5, 5, 5), expected=True, label="equilateral valid"),
        ],
    ))

    q.append(_code(
        "op.final_price", "Final Price Calculator", "Operators & Expressions",
        "Arithmetic + Relational + Logical",
        "Write final_price(price, is_member, coupon_percent) that applies a flat 10% "
        "member discount IF is_member is True OR coupon_percent >= 20, otherwise no "
        "discount. Return the resulting price rounded to 2 decimal places.",
        "final_price",
        "def final_price(price, is_member, coupon_percent):\n    pass\n",
        "FUNCTION final_price(price, is_member, coupon_percent)\nENDFUNCTION\n",
        [
            TestCase(args=(100, True, 0), expected=90.0, label="member, no coupon"),
            TestCase(args=(100, False, 25), expected=90.0, label="big coupon, not member"),
            TestCase(args=(100, False, 5), expected=100.0, label="neither -> no discount"),
        ],
    ))

    # =========================================================
    # DATA STRUCTURES -- 1D / 2D arrays, dictionaries
    # =========================================================
    q.append(_code(
        "ds.find_max", "Find the Maximum", "Data Structures", "1D Arrays",
        "Write find_max(arr) that returns the largest value in a non-empty 1D array, "
        "scanning the array yourself (don't rely on a built-in max()).",
        "find_max",
        "def find_max(arr):\n    pass\n",
        "FUNCTION find_max(arr)\nENDFUNCTION\n",
        [
            TestCase(args=([3, 7, 2, 9, 4],), expected=9, label="mixed"),
            TestCase(args=([-5, -1, -9],), expected=-1, label="all negative"),
            TestCase(args=([42],), expected=42, label="single element"),
        ],
    ))

    q.append(_code(
        "ds.reverse_array", "Reverse an Array", "Data Structures", "1D Arrays",
        "Write reverse_array(arr) that returns a NEW array with the elements in "
        "reverse order, built by manually stepping through arr (no slicing or a "
        "built-in reverse shortcut).",
        "reverse_array",
        "def reverse_array(arr):\n    # Build the reversed array yourself -- no arr[::-1], no .reverse()\n    pass\n",
        "FUNCTION reverse_array(arr)\n    # Build the reversed array yourself, element by element.\nENDFUNCTION\n",
        [
            TestCase(args=([1, 2, 3],), expected=[3, 2, 1], label="small sanity check"),
            TestCase(
                args=(list(range(30)),), expected=list(range(29, -1, -1)),
                label="30 items -- must actually iterate",
                min_steps_expr="n*0.8",
            ),
        ],
        method_note="Method check: slicing (arr[::-1]) or a built-in reverse executes in "
                    "roughly one step no matter how big arr is, and is rejected on the "
                    "30-item case -- this question wants a manual, element-by-element build.",
    ))

    q.append(_code(
        "ds.array_average", "Array Average", "Data Structures", "1D Arrays",
        "Write array_average(arr) that returns the average (mean) of a non-empty "
        "array of numbers, as a float.",
        "array_average",
        "def array_average(arr):\n    pass\n",
        "FUNCTION array_average(arr)\nENDFUNCTION\n",
        [
            TestCase(args=([1, 2, 3, 4],), expected=2.5, label="1..4"),
            TestCase(args=([10],), expected=10.0, label="single element"),
        ],
    ))

    q.append(_code(
        "ds.matrix_transpose", "Matrix Transpose", "Data Structures", "2D Arrays",
        "Write matrix_transpose(grid) that returns the transpose of a 2D array "
        "(rows become columns). Assume grid is rectangular.",
        "matrix_transpose",
        "def matrix_transpose(grid):\n    pass\n",
        "FUNCTION matrix_transpose(grid)\nENDFUNCTION\n",
        [
            TestCase(args=([[1, 2, 3], [4, 5, 6]],), expected=[[1, 4], [2, 5], [3, 6]],
                     label="2x3 -> 3x2"),
            TestCase(args=([[1]],), expected=[[1]], label="1x1"),
        ],
    ))

    q.append(_code(
        "ds.matrix_diagonal_sum", "Matrix Diagonal Sum", "Data Structures", "2D Arrays",
        "Write matrix_diagonal_sum(grid) that returns the sum of the main diagonal "
        "(top-left to bottom-right) of a square 2D array.",
        "matrix_diagonal_sum",
        "def matrix_diagonal_sum(grid):\n    pass\n",
        "FUNCTION matrix_diagonal_sum(grid)\nENDFUNCTION\n",
        [
            TestCase(args=([[1, 2], [3, 4]],), expected=5, label="2x2 -> 1+4"),
            TestCase(args=([[5, 1, 2], [1, 6, 3], [4, 9, 7]],), expected=18, label="3x3 -> 5+6+7"),
        ],
    ))

    q.append(_code(
        "ds.word_frequency", "Word Frequency Counter", "Data Structures", "Dictionaries",
        "Write word_frequency(words) that returns a dictionary mapping each word in "
        "the words array to how many times it appears.",
        "word_frequency",
        "def word_frequency(words):\n    pass\n",
        "FUNCTION word_frequency(words)\nENDFUNCTION\n",
        [
            TestCase(args=(["cat", "dog", "cat", "cat", "dog"],),
                     expected={"cat": 3, "dog": 2}, label="cats and dogs"),
            TestCase(args=([],), expected={}, label="empty"),
        ],
    ))

    q.append(_code(
        "ds.invert_dictionary", "Invert a Dictionary", "Data Structures", "Dictionaries",
        "Write invert_dictionary(d) that returns a new dictionary with the keys and "
        "values of d swapped (assume all original values are unique).",
        "invert_dictionary",
        "def invert_dictionary(d):\n    pass\n",
        "FUNCTION invert_dictionary(d)\nENDFUNCTION\n",
        [
            TestCase(args=({"a": 1, "b": 2},), expected={1: "a", 2: "b"}, label="simple swap"),
        ],
    ))

    # =========================================================
    # SEARCHING & SORTING (structured algorithms)
    # =========================================================
    arr_small = [5, 3, 8, 1, 9, 2]
    arr_big = list(range(0, 400, 2))
    q.append(_code(
        "algo.linear_search", "Linear Search", "Searching & Sorting", "Linear Search",
        "Write linear_search(arr, target). Scan the array left to right, one element "
        "at a time, and return the index of the first match, or -1 if target never "
        "appears. arr is NOT assumed to be sorted.",
        "linear_search",
        "def linear_search(arr, target):\n    pass\n",
        "FUNCTION linear_search(arr, target)\nENDFUNCTION\n",
        [
            TestCase(args=(arr_small, 5), expected=0, label="target at index 0"),
            TestCase(args=(arr_small, 9), expected=4, label="target in the middle"),
            TestCase(args=(arr_small, 42), expected=-1, label="target absent (small)"),
            TestCase(args=(arr_big, 999), expected=-1, label="200 items, absent -- worst case",
                     min_steps_expr="n*1.2"),
        ],
        method_note="Method check: on a 200-item 'not found' case, a real left-to-right "
                    "scan takes roughly n steps. Finishing suspiciously fast (e.g. a hidden "
                    "binary search, or Python's `in`) is rejected even if the answer is right.",
    ))

    sorted_small = [1, 3, 5, 7, 9, 11]
    sorted_big = list(range(0, 2000, 2))
    q.append(_code(
        "algo.binary_search", "Binary Search", "Searching & Sorting", "Binary Search",
        "Write binary_search(arr, target). arr is sorted ascending. Repeatedly look at "
        "the middle of the remaining range and eliminate half the search space each "
        "step, until you find target or run out of range. Return the index, or -1.",
        "binary_search",
        "def binary_search(arr, target):\n    pass\n",
        "FUNCTION binary_search(arr, target)\nENDFUNCTION\n",
        [
            TestCase(args=(sorted_small, 7), expected=3, label="small sanity check"),
            TestCase(args=(sorted_big, 1000), expected=500, label="1000 items, present -- O(log n)",
                     max_steps_expr="8*math.log2(n)+20"),
            TestCase(args=(sorted_big, 1), expected=-1, label="1000 items, absent -- O(log n)",
                     max_steps_expr="8*math.log2(n)+20"),
        ],
        method_note="Method check: real binary search on 1000 items takes roughly "
                    "log2(1000) ~ 10 steps. Anywhere near 1000 steps means it's secretly "
                    "a linear scan wearing a binary-search name.",
    ))

    q.append(_code(
        "algo.bubble_sort", "Bubble Sort", "Searching & Sorting", "Bubble Sort",
        "Write bubble_sort(arr) returning a NEW list sorted ascending. Repeatedly "
        "sweep through the list comparing neighbouring pairs and swapping if out of "
        "order, until a full sweep makes no swaps. No sorted()/.sort() shortcuts.",
        "bubble_sort",
        "def bubble_sort(arr):\n    pass\n",
        "FUNCTION bubble_sort(arr)\nENDFUNCTION\n",
        [
            TestCase(args=([3, 1, 2],), expected=[1, 2, 3], label="small sanity check"),
            TestCase(args=(list(range(30, 0, -1)),), expected=list(range(1, 31)),
                     label="30 items, reverse-sorted -- worst case", min_steps_expr="n*n*0.5"),
        ],
        method_note="Method check: on a 30-item reverse-sorted worst case, a real "
                    "compare-and-swap sort does on the order of n^2 work. A sorted() call "
                    "finishes in ~1 step and is rejected -- the output is right, the "
                    "method isn't.",
    ))

    q.append(_code(
        "algo.selection_sort", "Selection Sort", "Searching & Sorting", "Selection Sort",
        "Write selection_sort(arr) returning a NEW list sorted ascending. For each "
        "position, scan the remaining unsorted part for the minimum, then swap it "
        "into place. No sorted()/.sort() shortcuts.",
        "selection_sort",
        "def selection_sort(arr):\n    pass\n",
        "FUNCTION selection_sort(arr)\nENDFUNCTION\n",
        [
            TestCase(args=([4, 1, 3],), expected=[1, 3, 4], label="small sanity check"),
            TestCase(args=(list(range(25, 0, -1)),), expected=list(range(1, 26)),
                     label="25 items, reverse-sorted -- worst case", min_steps_expr="n*n*0.5"),
        ],
        method_note="Method check: same idea as bubble sort -- real selection sort does "
                    "O(n^2) work on a 25-item worst case; sorted()/.sort() shortcuts finish "
                    "almost instantly and are rejected.",
    ))

    q.append(_code(
        "algo.insertion_sort", "Insertion Sort", "Searching & Sorting", "Insertion Sort",
        "Write insertion_sort(arr) returning a NEW list sorted ascending. Build up the "
        "sorted section one element at a time: take the next element and shift it "
        "backwards through the sorted section until it's in the right place. No "
        "sorted()/.sort() shortcuts.",
        "insertion_sort",
        "def insertion_sort(arr):\n    pass\n",
        "FUNCTION insertion_sort(arr)\nENDFUNCTION\n",
        [
            TestCase(args=([4, 1, 3],), expected=[1, 3, 4], label="small sanity check"),
            TestCase(args=(list(range(25, 0, -1)),), expected=list(range(1, 26)),
                     label="25 items, reverse-sorted -- worst case", min_steps_expr="n*n*0.3"),
        ],
        method_note="Method check: reverse-sorted input is insertion sort's worst case -- "
                    "every new element has to shift all the way to the front, so a real "
                    "implementation does on the order of n^2 work. sorted()/.sort() "
                    "shortcuts finish almost instantly and are rejected.",
    ))

    q.append(_quiz(
        "quiz.bigo_purpose", "Purpose of Big O", "Searching & Sorting", "Big O Notation",
        "What does Big O notation describe about an algorithm?",
        ["The exact number of seconds it takes to run",
         "How its worst-case running time/work grows as the input size grows",
         "How many lines of code it has",
         "The programming language it was written in"],
        1,
        "Big O describes the growth rate of an algorithm's time (or space) requirement "
        "as the input size n increases -- not a literal stopwatch time.",
    ))
    q.append(_quiz(
        "quiz.bigo_binary", "Big O of Binary Search", "Searching & Sorting", "Big O Notation",
        "What is the worst-case Big O time complexity of binary search on a sorted array?",
        ["O(1)", "O(n)", "O(log n)", "O(n^2)"], 2,
        "Binary search halves the remaining search space every step, so the number of "
        "steps grows logarithmically with n.",
    ))
    q.append(_quiz(
        "quiz.bigo_bubble", "Big O of Bubble Sort", "Searching & Sorting", "Big O Notation",
        "What is the worst-case Big O time complexity of bubble sort?",
        ["O(log n)", "O(n)", "O(n log n)", "O(n^2)"], 3,
        "Bubble sort compares/swaps neighbouring pairs across repeated full passes, "
        "giving roughly n^2 comparisons in the worst case (reverse-sorted input).",
    ))
    q.append(_quiz(
        "quiz.bigo_linear", "Big O of Linear Search", "Searching & Sorting", "Big O Notation",
        "What is the worst-case Big O time complexity of linear search?",
        ["O(1)", "O(log n)", "O(n)", "O(n^2)"], 2,
        "In the worst case (target absent, or at the very end) a linear search has to "
        "check every one of the n elements.",
    ))

    # =========================================================
    # RECURSION
    # =========================================================
    q.append(_code(
        "rec.factorial", "Recursive Factorial", "Recursion", "Recursion",
        "Write factorial_recursive(n) using RECURSION -- the function must call "
        "itself, not use a loop. Return n! with factorial(0) == 1.",
        "factorial_recursive",
        "def factorial_recursive(n):\n    pass\n",
        "FUNCTION factorial_recursive(n)\nENDFUNCTION\n",
        [
            TestCase(args=(5,), expected=120, label="n=5 -- must recurse", n_hint=5, min_calls_expr="n"),
            TestCase(args=(10,), expected=3628800, label="n=10 -- must recurse", n_hint=10, min_calls_expr="n"),
        ],
        method_note="Method check: this counts self-calls. A correct recursive solution "
                    "calls itself about n times; a for/while-loop version calls itself "
                    "once and is rejected, even with the right return value.",
    ))

    q.append(_code(
        "rec.fibonacci", "Recursive Fibonacci", "Recursion", "Recursion",
        "Write fibonacci_recursive(n) using plain RECURSION (no loops, no "
        "memoisation/caching): fib(0)=0, fib(1)=1, fib(n) = fib(n-1) + fib(n-2).",
        "fibonacci_recursive",
        "def fibonacci_recursive(n):\n    pass\n",
        "FUNCTION fibonacci_recursive(n)\nENDFUNCTION\n",
        [
            TestCase(args=(10,), expected=55, label="n=10 -- must recurse (no memo)", n_hint=10, min_calls_expr="2*n"),
            TestCase(args=(15,), expected=610, label="n=15 -- must recurse (no memo)", n_hint=15, min_calls_expr="2*n"),
        ],
        method_note="Method check: naive recursive Fibonacci makes a LOT of self-calls "
                    "(recomputing the same values repeatedly). A loop or a memoised "
                    "version makes far fewer calls and is rejected -- this question "
                    "specifically wants the naive, exponential-time recursion.",
    ))

    q.append(_code(
        "rec.sum_digits", "Recursive Digit Sum", "Recursion", "Recursion",
        "Write sum_digits_recursive(n) using RECURSION to return the sum of the "
        "decimal digits of a non-negative integer n (e.g. 1234 -> 1+2+3+4 = 10).",
        "sum_digits_recursive",
        "def sum_digits_recursive(n):\n    pass\n",
        "FUNCTION sum_digits_recursive(n)\nENDFUNCTION\n",
        [
            TestCase(args=(1234,), expected=10, label="1234 -> 10"),
            TestCase(args=(7,), expected=7, label="single digit"),
            TestCase(args=(0,), expected=0, label="zero"),
        ],
    ))

    q.append(_code(
        "rec.power", "Recursive Power", "Recursion", "Recursion",
        "Write power_recursive(base, exp) using RECURSION to compute base ** exp for "
        "a non-negative integer exponent, without using ** or pow().",
        "power_recursive",
        "def power_recursive(base, exp):\n    pass\n",
        "FUNCTION power_recursive(base, exp)\nENDFUNCTION\n",
        [
            TestCase(args=(2, 10), expected=1024, label="2^10"),
            TestCase(args=(5, 0), expected=1, label="anything^0 = 1"),
            TestCase(args=(3, 1), expected=3, label="3^1"),
        ],
    ))

    # =========================================================
    # GOOD PROGRAMMING PRACTICE -- exception handling & validation
    # =========================================================
    q.append(_code(
        "gpp.safe_divide", "Safe Divide", "Good Programming Practice", "Exception Handling",
        "Write safe_divide(a, b) that returns a / b, but if b is 0, catch the error "
        "and return None instead of letting the program crash. This is the exception "
        "handling skill called for by good programming practice.",
        "safe_divide",
        "def safe_divide(a, b):\n    # Use a try/except to handle division by zero gracefully.\n    pass\n",
        "FUNCTION safe_divide(a, b)\n    # There's no try/except in this pseudocode dialect --\n    # check b before dividing instead, and return a suitable value.\nENDFUNCTION\n",
        [
            TestCase(args=(10, 2), expected=5.0, label="normal division"),
            TestCase(args=(5, 0), expected=None, label="divide by zero -- must not crash"),
        ],
    ))

    q.append(_code(
        "gpp.validate_and_square", "Validate Then Square", "Good Programming Practice",
        "Input Validation",
        "Write validate_and_square(x) that validates its input BEFORE processing: if x "
        "is negative, return None (it's invalid for this problem); otherwise return "
        "x squared.",
        "validate_and_square",
        "def validate_and_square(x):\n    # Validate input before processing.\n    pass\n",
        "FUNCTION validate_and_square(x)\n    # Validate input before processing.\nENDFUNCTION\n",
        [
            TestCase(args=(4,), expected=16, label="valid positive"),
            TestCase(args=(0,), expected=0, label="zero is valid"),
            TestCase(args=(-3,), expected=None, label="negative -- invalid"),
        ],
    ))

    q.append(_quiz(
        "quiz.gantt_purpose", "Gantt Charts", "Good Programming Practice", "Framework for Development",
        "In the 'investigate' phase of the development framework, what is a Gantt "
        "chart used for?",
        ["Testing the final solution against user requirements",
         "Scheduling tasks over time to plan and track a development project",
         "Storing data in a relational structure",
         "Highlighting syntax errors in code"], 1,
        "A Gantt chart is a project-scheduling tool that lays out tasks and their "
        "timeframes, used when planning a development schedule.",
    ))
    q.append(_quiz(
        "quiz.linear_vs_iterative", "Linear vs Iterative Development", "Good Programming Practice",
        "Development Process",
        "What's the key difference between a linear and an iterative development process?",
        ["Linear repeats every phase in cycles; iterative only runs once",
         "Linear moves through phases once in sequence; iterative repeats/refines phases "
         "based on feedback",
         "Linear is only for databases; iterative is only for networks",
         "There is no real difference"], 1,
        "A linear process moves straight through investigate -> design -> develop -> "
        "evaluate once. An iterative process cycles back through earlier phases as the "
        "solution is refined.",
    ))
    q.append(_quiz(
        "quiz.stub_purpose", "Purpose of a Stub", "Good Programming Practice", "Modular Coding",
        "Why would a programmer write a 'stub' function while developing a larger "
        "program?",
        ["To permanently replace a function that isn't needed",
         "To act as a placeholder for an unfinished module so the rest of the program "
         "can be built and tested around it",
         "To automatically generate test data",
         "To encrypt sensitive source code"], 1,
        "A stub is a minimal, temporary placeholder implementation (e.g. returning a "
        "fixed value) that lets the rest of the program be structured, run and tested "
        "before every module is finished.",
    ))
    q.append(_quiz(
        "quiz.mainline_clarity", "Clear Mainline", "Good Programming Practice", "Good Practice",
        "Why is 'a clear, uncluttered mainline with one logical task per subroutine' "
        "considered good practice?",
        ["It makes the program run faster on any hardware",
         "It makes the overall program easier to read, test and maintain by breaking it "
         "into understandable, focused pieces",
         "It is required by every programming language's syntax",
         "It removes the need for any comments"], 1,
        "Splitting a program into small, single-purpose subroutines with a clean "
        "top-level mainline improves readability, testability and long-term "
        "maintainability -- it isn't about raw speed.",
    ))
    q.append(_quiz(
        "quiz.version_control_purpose", "Version Control", "Good Programming Practice", "Good Practice",
        "What problem does version control (e.g. Git) primarily solve during "
        "software development?",
        ["It prevents all runtime errors automatically",
         "It tracks changes to code over time, letting developers collaborate and "
         "revert to earlier versions if something breaks",
         "It compiles code faster",
         "It replaces the need for testing"], 1,
        "Version control systems track the history of changes to a codebase, support "
        "collaboration between developers, and allow reverting to a previous working "
        "version.",
    ))
    q.append(_quiz(
        "quiz.backup_purpose", "Regular Backups", "Good Programming Practice", "Good Practice",
        "Why does good programming practice recommend regular backups of code and data?",
        ["To make the program run faster",
         "To protect against loss from hardware failure, accidental deletion or "
         "corruption",
         "To automatically fix logic errors",
         "Backups are only needed for network communications, not programming"], 1,
        "Regular backups protect the project against data loss from things like disk "
        "failure, accidental deletion, or corrupted files.",
    ))

    # =========================================================
    # TESTING
    # =========================================================
    q.append(_quiz(
        "quiz.unit_testing", "Purpose of Unit Testing", "Testing", "Unit Testing",
        "What is the main purpose of unit testing?",
        ["Checking that the whole finished system meets user requirements",
         "Checking that an individual function/module performs correctly in isolation",
         "Measuring how many users the system can support",
         "Reviewing the ethical implications of a system"], 1,
        "Unit tests target one small piece of code (a function or module) in isolation "
        "to confirm it behaves correctly before it's combined with everything else.",
    ))
    q.append(_quiz(
        "quiz.acceptance_vs_unit", "Acceptance vs Unit Testing", "Testing", "Acceptance Testing",
        "How does acceptance testing differ from unit testing?",
        ["Acceptance testing checks individual functions; unit testing checks the whole "
         "system",
         "Acceptance testing checks whether the finished solution meets the user's "
         "functional requirements; unit testing checks individual pieces of code",
         "They are two names for the same process",
         "Acceptance testing is only done by the original developer"], 1,
        "Acceptance testing is a user-focused check that the overall solution does what "
        "was asked for, while unit testing verifies individual code units work "
        "correctly.",
    ))
    q.append(_quiz(
        "quiz.live_test_data", "Live Test Data", "Testing", "Live Test Data",
        "Why would a tester use 'live' test data (large file sizes, a realistic mix "
        "of transaction types, real response times, high data volumes) instead of "
        "just a couple of made-up examples?",
        ["Live data is easier to type in manually",
         "It makes sure testing reflects how the system will actually behave under "
         "real operating conditions, including performance under load",
         "It removes the need for any other kind of testing",
         "Live data guarantees there will be no bugs"], 1,
        "Live/realistic test data (volume, mixed transaction types, timing) helps "
        "reveal problems -- like performance or load issues -- that small, tidy sample "
        "data would never expose.",
    ))
    q.append(_quiz(
        "quiz.actual_vs_expected", "Actual vs Expected Output", "Testing", "Test Comparison",
        "During testing, what does 'comparing actual output with expected output' "
        "mean?",
        ["Running the program twice and comparing the running time",
         "Checking whether the result the program produced for a test case matches "
         "the result you calculated it SHOULD produce",
         "Comparing your code style with another programmer's",
         "Checking whether the code compiles without errors"], 1,
        "For each test case you predict/calculate the expected result ahead of time, "
        "then compare it against what the program actually returns -- a mismatch flags "
        "a bug.",
    ))
    q.append(_quiz(
        "quiz.load_testing", "Load Testing", "Testing", "Live Test Data",
        "What does 'load testing' (testing with a high volume of data) specifically "
        "check?",
        ["Whether the program's variable names follow conventions",
         "How the system performs -- speed, stability, resource use -- when handling a "
         "large volume of data or many transactions at once",
         "Whether the program has any syntax errors",
         "Whether the developer documented their code"], 1,
        "Load testing pushes a system with a realistic (large) volume of data or "
        "traffic to see whether performance holds up, rather than just checking "
        "correctness on small inputs.",
    ))

    # =========================================================
    # ERROR DETECTION & DEBUGGING
    # =========================================================
    q.append(_code(
        "dbg.fix_off_by_one", "Fix: Count Negatives", "Error Detection & Debugging",
        "Logic Errors",
        "This starter has a LOGIC ERROR in its comparison. count_negatives(nums) "
        "should count how many numbers in nums are STRICTLY less than zero -- but the "
        "buggy version also counts zero. Fix the comparison operator.",
        "count_negatives",
        "def count_negatives(nums):\n    count = 0\n    for x in nums:\n        if x <= 0:  # BUG: this also counts zero\n            count += 1\n    return count\n",
        "FUNCTION count_negatives(nums)\n    count = 0\n    FOR i = 0 TO LENGTH(nums) - 1\n        IF nums[i] <= 0 THEN  // BUG: this also counts zero\n            count = count + 1\n        ENDIF\n    ENDFOR\n    RETURN count\nENDFUNCTION\n",
        [
            TestCase(args=([-3, -1, 0, 2, 5],), expected=2, label="two negatives, one zero"),
            TestCase(args=([0, 0, 0],), expected=0, label="all zero -- none negative"),
            TestCase(args=([-1, -2, -3],), expected=3, label="all negative"),
        ],
    ))

    q.append(_code(
        "dbg.fix_safe_average", "Fix: Safe Average", "Error Detection & Debugging",
        "Runtime Errors (division by zero)",
        "This starter has a RUNTIME ERROR: safe_average(nums) crashes with a "
        "division-by-zero error on an empty list. Fix it so an empty list returns "
        "None instead of crashing, while still averaging normally otherwise.",
        "safe_average",
        "def safe_average(nums):\n    total = 0\n    for x in nums:\n        total += x\n    return total / len(nums)  # BUG: crashes when nums is empty\n",
        "FUNCTION safe_average(nums)\n    total = 0\n    FOR i = 0 TO LENGTH(nums) - 1\n        total = total + nums[i]\n    ENDFOR\n    RETURN total / LENGTH(nums)  // BUG: crashes when nums is empty\nENDFUNCTION\n",
        [
            TestCase(args=([2, 4, 6],), expected=4.0, label="normal case"),
            TestCase(args=([],), expected=None, label="empty list -- must not crash"),
        ],
    ))

    q.append(_code(
        "dbg.fix_last_element", "Fix: Get Last Element", "Error Detection & Debugging",
        "Runtime Errors (index out of range)",
        "This starter has a RUNTIME ERROR: get_last(arr) crashes with an "
        "index-out-of-range error. Fix the index so it correctly returns the last "
        "element of a non-empty array.",
        "get_last",
        "def get_last(arr):\n    return arr[len(arr)]  # BUG: valid indices only go up to len(arr) - 1\n",
        "FUNCTION get_last(arr)\n    RETURN arr[LENGTH(arr)]  // BUG: valid indices only go up to LENGTH(arr) - 1\nENDFUNCTION\n",
        [
            TestCase(args=([1, 2, 3],), expected=3, label="[1,2,3] -> 3"),
            TestCase(args=([42],), expected=42, label="single element"),
        ],
    ))

    q.append(_quiz(
        "quiz.error_types", "Types of Errors", "Error Detection & Debugging", "Error Types",
        "A program crashes partway through execution because it tries to divide a "
        "number by zero. What TYPE of error is this?",
        ["Syntax error", "Logic error", "Runtime error", "Compilation warning"], 2,
        "A runtime error only shows up while the program is actually running (e.g. "
        "division by zero, index out of range) -- the code is syntactically valid and "
        "will happily compile.",
    ))
    q.append(_quiz(
        "quiz.syntax_vs_logic", "Syntax vs Logic Errors", "Error Detection & Debugging",
        "Error Types",
        "A program runs without crashing but consistently produces the wrong answer "
        "(e.g. it used '<' where it should have used '<='). What TYPE of error is "
        "this?",
        ["Syntax error", "Logic error", "Runtime error", "Hardware error"], 1,
        "A logic error is code that's valid and runs fine, but doesn't do what the "
        "programmer intended -- the program logic itself is flawed.",
    ))
    q.append(_quiz(
        "quiz.breakpoint_purpose", "Breakpoints", "Error Detection & Debugging",
        "Debugging Techniques",
        "What does setting a breakpoint while debugging let a programmer do?",
        ["Permanently delete a line of code",
         "Pause execution at that line so the current variable values can be inspected",
         "Automatically fix any errors found",
         "Speed up the program's execution"], 1,
        "A breakpoint pauses execution at a chosen line so the developer can inspect "
        "variable values and step through the program to find where behaviour goes "
        "wrong.",
    ))
    q.append(_quiz(
        "quiz.desk_check", "Desk Checking", "Error Detection & Debugging",
        "Debugging Techniques",
        "What is 'desk checking' (using a trace table)?",
        ["Automated testing performed by the compiler",
         "Manually walking through code line by line on paper, tracking variable "
         "values, to find where the logic goes wrong",
         "Checking the physical desk setup of a workstation",
         "A way to measure a network's bandwidth"], 1,
        "Desk checking means tracing through the code by hand (often with a trace "
        "table of variable values) to find logic errors without running the program.",
    ))
    q.append(_quiz(
        "quiz.index_out_of_range", "Index Out of Range", "Error Detection & Debugging",
        "Error Types",
        "An array has 5 elements (valid indices 0 to 4). Which of these causes an "
        "'index out of range' runtime error?",
        ["Accessing index 0", "Accessing index 4", "Accessing index 5", "Accessing index 2"],
        2,
        "Valid indices for a 5-element array run from 0 to 4 -- index 5 is one past "
        "the end and triggers an index-out-of-range error.",
    ))

    # =========================================================
    # OBJECT-ORIENTED PROGRAMMING (Python only)
    # =========================================================
    q.append(_oop(
        "oop.rectangle", "Rectangle Class", "Object-Oriented Programming",
        "Classes, Objects & Methods",
        "Create a class Rectangle. Its __init__(self, width, height) should store "
        "both as attributes. Add methods area(self) and perimeter(self) returning "
        "the rectangle's area and perimeter.",
        "Rectangle",
        "class Rectangle:\n    def __init__(self, width, height):\n        pass\n\n    def area(self):\n        pass\n\n    def perimeter(self):\n        pass\n",
        [
            OOPScenario("area of 4x5", (4, 5), [OOPCall("area", ())], 20),
            OOPScenario("perimeter of 4x5", (4, 5), [OOPCall("perimeter", ())], 18),
            OOPScenario("area of 3x3", (3, 3), [OOPCall("area", ())], 9),
        ],
    ))

    q.append(_oop(
        "oop.bank_account", "Bank Account Class", "Object-Oriented Programming",
        "Classes, Objects & Methods",
        "Create a class BankAccount. __init__(self, balance) stores the starting "
        "balance. deposit(self, amount) adds to the balance. withdraw(self, amount) "
        "subtracts from the balance but must NOT let it go below 0 -- if the "
        "withdrawal would overdraw the account, leave the balance unchanged. "
        "get_balance(self) returns the current balance.",
        "BankAccount",
        "class BankAccount:\n    def __init__(self, balance):\n        pass\n\n    def deposit(self, amount):\n        pass\n\n    def withdraw(self, amount):\n        # Must not allow the balance to go below 0.\n        pass\n\n    def get_balance(self):\n        pass\n",
        [
            OOPScenario("deposit then balance", (100,), [OOPCall("deposit", (50,)), OOPCall("get_balance", ())], 150),
            OOPScenario("withdraw within funds", (100,), [OOPCall("withdraw", (40,)), OOPCall("get_balance", ())], 60),
            OOPScenario("withdraw over funds is blocked", (50,), [OOPCall("withdraw", (100,)), OOPCall("get_balance", ())], 50),
        ],
    ))

    q.append(_oop(
        "oop.inheritance_animal", "Animal Inheritance", "Object-Oriented Programming",
        "Inheritance",
        "Create a base class Animal with __init__(self, name) storing name, and a "
        "method speak(self) that returns '...'. Create a subclass Dog(Animal) that "
        "OVERRIDES speak(self) to return 'Woof!' instead, demonstrating inheritance "
        "(Dog reuses Animal's __init__ without rewriting it).",
        "Dog",
        "class Animal:\n    def __init__(self, name):\n        self.name = name\n\n    def speak(self):\n        return '...'\n\n\nclass Dog(Animal):\n    def speak(self):\n        # Override to return 'Woof!'\n        pass\n",
        [
            OOPScenario("dog speaks", ("Rex",), [OOPCall("speak", ())], "Woof!"),
        ],
    ))

    q.append(_oop(
        "oop.counter", "Counter Class", "Object-Oriented Programming",
        "State & Instantiation",
        "Create a class Counter. __init__(self) starts count at 0. increment(self) "
        "adds 1 to count. reset(self) sets count back to 0. get_count(self) returns "
        "the current count.",
        "Counter",
        "class Counter:\n    def __init__(self):\n        pass\n\n    def increment(self):\n        pass\n\n    def reset(self):\n        pass\n\n    def get_count(self):\n        pass\n",
        [
            OOPScenario("increment 3 times", (), [OOPCall("increment", ()), OOPCall("increment", ()),
                        OOPCall("increment", ()), OOPCall("get_count", ())], 3),
            OOPScenario("increment then reset", (), [OOPCall("increment", ()), OOPCall("increment", ()),
                        OOPCall("reset", ()), OOPCall("get_count", ())], 0),
        ],
    ))

    q.append(_oop(
        "oop.student", "Student Class", "Object-Oriented Programming",
        "Combining OOP with Control Structures",
        "Create a class Student. __init__(self, name) stores name and starts an "
        "empty marks list. add_mark(self, mark) appends a mark to the list. "
        "average(self) returns the mean of all marks so far (use a loop inside the "
        "method), or 0 if there are no marks yet.",
        "Student",
        "class Student:\n    def __init__(self, name):\n        pass\n\n    def add_mark(self, mark):\n        pass\n\n    def average(self):\n        pass\n",
        [
            OOPScenario("average of two marks", ("Amara",),
                        [OOPCall("add_mark", (80,)), OOPCall("add_mark", (90,)), OOPCall("average", ())], 85.0),
            OOPScenario("average with no marks", ("Beau",), [OOPCall("average", ())], 0),
        ],
    ))

    q.append(_oop(
        "oop.circle", "Circle Class", "Object-Oriented Programming",
        "Classes, Objects & Methods",
        "Create a class Circle. __init__(self, radius) stores the radius. "
        "area(self) returns pi * radius^2. circumference(self) returns "
        "2 * pi * radius. Import math for pi.",
        "Circle",
        "import math\n\n\nclass Circle:\n    def __init__(self, radius):\n        pass\n\n    def area(self):\n        pass\n\n    def circumference(self):\n        pass\n",
        [
            OOPScenario("area of radius 2", (2,), [OOPCall("area", ())], 12.566370614359172),
            OOPScenario("circumference of radius 3", (3,), [OOPCall("circumference", ())], 18.84955592153876),
        ],
    ))

    q.append(_quiz(
        "quiz.encapsulation", "Encapsulation", "Object-Oriented Programming", "OOP Concepts",
        "What does 'encapsulation' mean in object-oriented programming?",
        ["A class having many unrelated responsibilities",
         "Bundling data (attributes) and the behaviour (methods) that operates on it "
         "together inside one object, controlling access to its internals",
         "Making one class inherit from many other classes at once",
         "Converting a program into pseudocode"], 1,
        "Encapsulation bundles an object's data and the methods that work on it "
        "together, typically hiding/protecting internal details from the outside.",
    ))
    q.append(_quiz(
        "quiz.abstraction", "Abstraction", "Object-Oriented Programming", "OOP Concepts",
        "What does 'abstraction' mean in object-oriented programming?",
        ["Exposing every internal implementation detail of a class",
         "Hiding complex implementation details behind a simple, well-defined "
         "interface the user of the class interacts with",
         "Making a class impossible to instantiate",
         "Writing code without any comments"], 1,
        "Abstraction means presenting a simple interface (e.g. deposit()/withdraw()) "
        "while hiding the complicated details of how it's implemented underneath.",
    ))
    q.append(_quiz(
        "quiz.polymorphism", "Polymorphism", "Object-Oriented Programming", "OOP Concepts",
        "In the Animal/Dog example, calling .speak() gives a different result "
        "depending on whether the object is an Animal or a Dog. What OOP concept "
        "does this demonstrate?",
        ["Encapsulation", "Polymorphism", "Normalisation", "Recursion"], 1,
        "Polymorphism lets objects of different (related) classes respond to the same "
        "method call in their own way -- here, speak() behaves differently for Animal "
        "vs Dog.",
    ))
    q.append(_quiz(
        "quiz.inheritance_purpose", "Why Use Inheritance", "Object-Oriented Programming",
        "OOP Concepts",
        "What is the main benefit of using inheritance (e.g. Dog extends Animal) "
        "instead of writing Dog as a completely separate, unrelated class?",
        ["It makes the program run in less memory automatically",
         "It lets Dog reuse Animal's existing attributes/methods and only add or "
         "override what's different, avoiding duplicated code",
         "It is required by Python syntax for every class",
         "It prevents the class from ever being instantiated"], 1,
        "Inheritance lets a subclass reuse a parent class's code and only define what's "
        "new or different, reducing duplication and modelling an 'is-a' relationship.",
    ))

    # =========================================================
    # ETHICAL & LEGAL IMPLICATIONS FOR DEVELOPERS
    # =========================================================
    q.append(_quiz(
        "quiz.ip_acknowledgement", "Acknowledging Intellectual Property", "Ethical & Legal Implications",
        "Developer Rights & Responsibilities",
        "A developer reuses a chunk of open-source code written by someone else "
        "inside their own project. What is their ethical/legal responsibility?",
        ["Nothing -- once code is on the internet it belongs to whoever uses it",
         "To acknowledge the original author's intellectual property rather than "
         "presenting it as their own work",
         "To rewrite Python's entire standard library from scratch",
         "To keep the reused code a secret from their employer"], 1,
        "Developers are expected to acknowledge the intellectual property of others "
        "they build on, rather than claiming someone else's work as their own.",
    ))
    q.append(_quiz(
        "quiz.code_of_conduct", "Code of Conduct", "Ethical & Legal Implications",
        "Developer Rights & Responsibilities",
        "Why do many software organisations expect developers to adhere to a "
        "professional 'code of conduct'?",
        ["It's a legal requirement in every country with no exceptions",
         "It sets shared expectations for ethical, responsible behaviour -- e.g. "
         "honesty, respecting users, not causing harm -- across the profession",
         "It specifies which programming language must be used",
         "It replaces the need for testing"], 1,
        "A code of conduct sets out expected professional and ethical standards of "
        "behaviour for developers, covering things like honesty and responsible "
        "treatment of users and data.",
    ))
    q.append(_quiz(
        "quiz.ergonomics", "Ergonomic Issues", "Ethical & Legal Implications",
        "Developer Rights & Responsibilities",
        "A developer designs a data-entry interface with tiny, cramped controls that "
        "cause user strain and errors over long use. Which responsibility have they "
        "neglected?",
        ["Addressing ergonomic issues in software design",
         "Ensuring referential integrity",
         "Subnetting the network correctly",
         "Normalising the database to 3NF"], 0,
        "Ergonomics is about designing software that is comfortable and safe to use "
        "over extended periods -- layout, sizing, and interaction design all matter.",
    ))
    q.append(_quiz(
        "quiz.inclusivity", "Inclusivity in Software Design", "Ethical & Legal Implications",
        "Developer Rights & Responsibilities",
        "Why is it considered a developer responsibility to address inclusivity "
        "issues (e.g. accessibility for users with disabilities) in software design?",
        ["It's optional and only matters for government software",
         "Software should be usable by as broad a range of people as reasonably "
         "possible, not just one narrow group of users",
         "It makes the code run faster",
         "It is unrelated to ethics, only to marketing"], 1,
        "Inclusive design aims to make software usable by people with a wide range of "
        "abilities and needs, rather than assuming every user is the same.",
    ))
    q.append(_quiz(
        "quiz.privacy_dev", "Ensuring Privacy", "Ethical & Legal Implications",
        "Developer Rights & Responsibilities",
        "What does it mean for a developer to ensure 'individuals' privacy is not "
        "compromised' when building software?",
        ["Publishing all collected user data openly for transparency",
         "Handling and storing personal data responsibly, only using/sharing it "
         "appropriately and protecting it from unauthorised access",
         "Never collecting any data at all, under any circumstances",
         "Encrypting the source code so nobody can read it"], 1,
        "Protecting privacy means responsibly collecting, storing and using personal "
        "data, and safeguarding it from being exposed or misused.",
    ))
    q.append(_quiz(
        "quiz.malware_responsibility", "Malware & Developer Responsibility", "Ethical & Legal Implications",
        "Impacts of Software in Society",
        "What is a software developer's ethical/legal responsibility regarding "
        "malware such as viruses?",
        ["To create malware only for 'educational' purposes",
         "To neither generate nor transmit malware -- deliberately writing or "
         "spreading malicious software is both unethical and illegal",
         "Malware is acceptable if the source code is kept private",
         "Only large companies need to worry about malware"], 1,
        "Developers are expected to neither create nor distribute malware -- doing so "
        "is both an ethical breach and, in most jurisdictions, illegal.",
    ))
    q.append(_quiz(
        "quiz.reliance_on_software", "Reliance on Software", "Ethical & Legal Implications",
        "Impacts of Software in Society",
        "Society becoming heavily reliant on software (e.g. for banking, "
        "navigation, healthcare records) raises what kind of concern?",
        ["None -- more reliance is always purely beneficial with no downsides",
         "If that software fails, is unavailable, or is flawed, the impact on "
         "people's lives can be significant, which raises the stakes on software "
         "quality and reliability",
         "It only matters for entertainment software",
         "It removes the need for any testing"], 1,
        "As more of daily life depends on software working correctly, failures or "
        "flaws can have serious, wide-reaching real-world consequences.",
    ))
    q.append(_quiz(
        "quiz.cyber_safety", "Cyber Safety & Social Networking", "Ethical & Legal Implications",
        "Impacts of Software in Society",
        "Which of these is a cyber-safety concern developers should consider when "
        "building social-networking style software?",
        ["Making sure fonts are consistent across screens",
         "Risks like harassment, oversharing of personal information, or exposure to "
         "harmful content between users of the platform",
         "Whether the app uses a relational or non-relational database",
         "The programming language's release date"], 1,
        "Cyber safety concerns for social platforms include things like harassment, "
        "privacy risks from oversharing, and exposure to harmful content -- design "
        "choices can help mitigate these.",
    ))
    q.append(_quiz(
        "quiz.unreliable_info", "Unverifiable Information Online", "Ethical & Legal Implications",
        "Impacts of Software in Society",
        "The internet makes huge volumes of information available, some of it "
        "unsupported, unverifiable, misleading or simply incorrect. Why is this "
        "relevant to software developers?",
        ["It isn't relevant to developers at all, only to journalists",
         "Software that surfaces or relies on such information (e.g. search results, "
         "feeds, data imports) can spread misinformation, so this needs to be "
         "considered in how systems are designed",
         "It means developers should stop using the internet completely",
         "It only matters for government websites"], 1,
        "Because software often surfaces or processes information from the internet, "
        "developers need to consider the risk of spreading unreliable or misleading "
        "content through their systems.",
    ))

    return q