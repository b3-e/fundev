"""
verify_bank.py (DEV TOOL -- not shipped to the user)
=====================================================
For every code/oop question in the bank, run a hand-written reference
solution through the appropriate engine(s) and assert it passes with
method_ok=True. For questions that have a method-fingerprint check, also
run a 'cheat' solution and assert it gets caught (method_ok=False).
"""
from questions import build_builtin_questions
from engines import evaluate_python_submission, evaluate_pseudocode_submission, evaluate_oop_submission

PY_SOLUTIONS = {
    "cs.rectangle_area": "def rectangle_area(length, width):\n    return length * width\n",
    "cs.grade_from_score": (
        "def grade_from_score(score):\n"
        "    if score >= 80:\n        return 'A'\n"
        "    elif score >= 70:\n        return 'B'\n"
        "    elif score >= 60:\n        return 'C'\n"
        "    elif score >= 50:\n        return 'D'\n"
        "    else:\n        return 'E'\n"
    ),
    "cs.is_leap_year": (
        "def is_leap_year(year):\n"
        "    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)\n"
    ),
    "cs.sum_first_n": (
        "def sum_first_n(n):\n"
        "    total = 0\n"
        "    for i in range(1, n + 1):\n        total = total + i\n"
        "    return total\n"
    ),
    "cs.collatz_steps": (
        "def collatz_steps(n):\n"
        "    steps = 0\n"
        "    while n != 1:\n"
        "        if n % 2 == 0:\n            n = n // 2\n"
        "        else:\n            n = 3 * n + 1\n"
        "        steps = steps + 1\n"
        "    return steps\n"
    ),
    "dt.parse_and_add": "def parse_and_add(a_str, b_str):\n    return int(a_str) + int(b_str)\n",
    "dt.fahrenheit_to_celsius": "def fahrenheit_to_celsius(f):\n    return (f - 32) * 5 / 9\n",
    "fn.increment_copy": "def increment_copy(x):\n    return x + 1\n",
    "fn.append_bonus": "def append_bonus(scores):\n    scores.append(99)\n    return scores\n",
    "fn.running_total_with_default": "def add_with_bonus(a, b, bonus):\n    return a + b + bonus\n",
    "op.is_valid_triangle": (
        "def is_valid_triangle(a, b, c):\n"
        "    if a <= 0 or b <= 0 or c <= 0:\n        return False\n"
        "    return (a + b > c) and (a + c > b) and (b + c > a)\n"
    ),
    "op.final_price": (
        "def final_price(price, is_member, coupon_percent):\n"
        "    if is_member or coupon_percent >= 20:\n"
        "        price = price * 0.9\n"
        "    return round(price, 2)\n"
    ),
    "ds.find_max": (
        "def find_max(arr):\n"
        "    best = arr[0]\n"
        "    for x in arr:\n        if x > best:\n            best = x\n"
        "    return best\n"
    ),
    "ds.reverse_array": (
        "def reverse_array(arr):\n"
        "    result = []\n"
        "    i = len(arr) - 1\n"
        "    while i >= 0:\n        result.append(arr[i])\n        i = i - 1\n"
        "    return result\n"
    ),
    "ds.array_average": "def array_average(arr):\n    return sum(arr) / len(arr)\n",
    "ds.matrix_transpose": (
        "def matrix_transpose(grid):\n"
        "    rows = len(grid)\n    cols = len(grid[0])\n"
        "    result = []\n"
        "    for c in range(cols):\n"
        "        row = []\n        for r in range(rows):\n            row.append(grid[r][c])\n"
        "        result.append(row)\n"
        "    return result\n"
    ),
    "ds.matrix_diagonal_sum": (
        "def matrix_diagonal_sum(grid):\n"
        "    total = 0\n    for i in range(len(grid)):\n        total += grid[i][i]\n"
        "    return total\n"
    ),
    "ds.word_frequency": (
        "def word_frequency(words):\n"
        "    freq = {}\n"
        "    for w in words:\n"
        "        if w in freq:\n            freq[w] = freq[w] + 1\n"
        "        else:\n            freq[w] = 1\n"
        "    return freq\n"
    ),
    "ds.invert_dictionary": (
        "def invert_dictionary(d):\n"
        "    result = {}\n    for k in d:\n        result[d[k]] = k\n"
        "    return result\n"
    ),
    "algo.linear_search": (
        "def linear_search(arr, target):\n"
        "    for i in range(len(arr)):\n        if arr[i] == target:\n            return i\n"
        "    return -1\n"
    ),
    "algo.binary_search": (
        "def binary_search(arr, target):\n"
        "    lo, hi = 0, len(arr) - 1\n"
        "    while lo <= hi:\n"
        "        mid = (lo + hi) // 2\n"
        "        if arr[mid] == target:\n            return mid\n"
        "        elif arr[mid] < target:\n            lo = mid + 1\n"
        "        else:\n            hi = mid - 1\n"
        "    return -1\n"
    ),
    "algo.bubble_sort": (
        "def bubble_sort(arr):\n"
        "    a = list(arr)\n    n = len(a)\n"
        "    for i in range(n):\n"
        "        for j in range(n - i - 1):\n"
        "            if a[j] > a[j + 1]:\n"
        "                a[j], a[j + 1] = a[j + 1], a[j]\n"
        "    return a\n"
    ),
    "algo.selection_sort": (
        "def selection_sort(arr):\n"
        "    a = list(arr)\n    n = len(a)\n"
        "    for i in range(n):\n"
        "        min_idx = i\n"
        "        for j in range(i + 1, n):\n            if a[j] < a[min_idx]:\n                min_idx = j\n"
        "        a[i], a[min_idx] = a[min_idx], a[i]\n"
        "    return a\n"
    ),
    "algo.insertion_sort": (
        "def insertion_sort(arr):\n"
        "    a = list(arr)\n"
        "    for i in range(1, len(a)):\n"
        "        key = a[i]\n        j = i - 1\n"
        "        while j >= 0 and a[j] > key:\n"
        "            a[j + 1] = a[j]\n            j = j - 1\n"
        "        a[j + 1] = key\n"
        "    return a\n"
    ),
    "rec.factorial": (
        "def factorial_recursive(n):\n"
        "    if n <= 1:\n        return 1\n"
        "    return n * factorial_recursive(n - 1)\n"
    ),
    "rec.fibonacci": (
        "def fibonacci_recursive(n):\n"
        "    if n < 2:\n        return n\n"
        "    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)\n"
    ),
    "rec.sum_digits": (
        "def sum_digits_recursive(n):\n"
        "    if n < 10:\n        return n\n"
        "    return n % 10 + sum_digits_recursive(n // 10)\n"
    ),
    "rec.power": (
        "def power_recursive(base, exp):\n"
        "    if exp == 0:\n        return 1\n"
        "    return base * power_recursive(base, exp - 1)\n"
    ),
    "gpp.safe_divide": (
        "def safe_divide(a, b):\n"
        "    try:\n        return a / b\n    except ZeroDivisionError:\n        return None\n"
    ),
    "gpp.validate_and_square": (
        "def validate_and_square(x):\n"
        "    if x < 0:\n        return None\n    return x * x\n"
    ),
    "dbg.fix_off_by_one": (
        "def count_negatives(nums):\n"
        "    count = 0\n    for x in nums:\n        if x < 0:\n            count += 1\n"
        "    return count\n"
    ),
    "dbg.fix_safe_average": (
        "def safe_average(nums):\n"
        "    if len(nums) == 0:\n        return None\n"
        "    total = 0\n    for x in nums:\n        total += x\n"
        "    return total / len(nums)\n"
    ),
    "dbg.fix_last_element": "def get_last(arr):\n    return arr[len(arr) - 1]\n",
}

# Deliberately "cheating" solutions that SHOULD be caught by method checks.
PY_CHEATS = {
    "cs.sum_first_n": "def sum_first_n(n):\n    return n * (n + 1) // 2\n",
    "ds.reverse_array": "def reverse_array(arr):\n    return arr[::-1]\n",
    "algo.linear_search": "def linear_search(arr, target):\n    return arr.index(target) if target in arr else -1\n",
    "algo.binary_search": "def binary_search(arr, target):\n    return arr.index(target) if target in arr else -1\n",
    "algo.bubble_sort": "def bubble_sort(arr):\n    return sorted(arr)\n",
    "algo.selection_sort": "def selection_sort(arr):\n    return sorted(arr)\n",
    "algo.insertion_sort": "def insertion_sort(arr):\n    return sorted(arr)\n",
    "rec.factorial": "def factorial_recursive(n):\n    result = 1\n    for i in range(1, n + 1):\n        result *= i\n    return result\n",
    "rec.fibonacci": (
        "def fibonacci_recursive(n, memo={}):\n"
        "    if n < 2:\n        return n\n"
        "    if n in memo:\n        return memo[n]\n"
        "    memo[n] = fibonacci_recursive(n - 1, memo) + fibonacci_recursive(n - 2, memo)\n"
        "    return memo[n]\n"
    ),
}

PC_SOLUTIONS = {
    "cs.rectangle_area": "FUNCTION rectangle_area(length, width)\n    RETURN length * width\nENDFUNCTION\n",
    "cs.grade_from_score": (
        "FUNCTION grade_from_score(score)\n"
        "    IF score >= 80 THEN\n        RETURN \"A\"\n"
        "    ELSEIF score >= 70 THEN\n        RETURN \"B\"\n"
        "    ELSEIF score >= 60 THEN\n        RETURN \"C\"\n"
        "    ELSEIF score >= 50 THEN\n        RETURN \"D\"\n"
        "    ELSE\n        RETURN \"E\"\n"
        "    ENDIF\n"
        "ENDFUNCTION\n"
    ),
    "cs.is_leap_year": (
        "FUNCTION is_leap_year(year)\n"
        "    RETURN (year MOD 4 == 0) AND ((NOT (year MOD 100 == 0)) OR (year MOD 400 == 0))\n"
        "ENDFUNCTION\n"
    ),
    "cs.sum_first_n": (
        "FUNCTION sum_first_n(n)\n"
        "    total = 0\n"
        "    FOR i = 1 TO n\n        total = total + i\n    ENDFOR\n"
        "    RETURN total\n"
        "ENDFUNCTION\n"
    ),
    "cs.collatz_steps": (
        "FUNCTION collatz_steps(n)\n"
        "    steps = 0\n"
        "    WHILE n != 1\n"
        "        IF n MOD 2 == 0 THEN\n            n = n DIV 2\n"
        "        ELSE\n            n = 3 * n + 1\n        ENDIF\n"
        "        steps = steps + 1\n"
        "    ENDWHILE\n"
        "    RETURN steps\n"
        "ENDFUNCTION\n"
    ),
    "dt.parse_and_add": "FUNCTION parse_and_add(a_str, b_str)\n    RETURN INT(a_str) + INT(b_str)\nENDFUNCTION\n",
    "dt.fahrenheit_to_celsius": "FUNCTION fahrenheit_to_celsius(f)\n    RETURN (f - 32) * 5 / 9\nENDFUNCTION\n",
    "fn.increment_copy": "FUNCTION increment_copy(x)\n    RETURN x + 1\nENDFUNCTION\n",
    "fn.append_bonus": (
        "FUNCTION append_bonus(scores)\n"
        "    scores[LENGTH(scores)] = 99\n    RETURN scores\n"
        "ENDFUNCTION\n"
    ),
    "fn.running_total_with_default": "FUNCTION add_with_bonus(a, b, bonus)\n    RETURN a + b + bonus\nENDFUNCTION\n",
    "op.is_valid_triangle": (
        "FUNCTION is_valid_triangle(a, b, c)\n"
        "    IF a <= 0 OR b <= 0 OR c <= 0 THEN\n        RETURN FALSE\n    ENDIF\n"
        "    RETURN (a + b > c) AND (a + c > b) AND (b + c > a)\n"
        "ENDFUNCTION\n"
    ),
    "op.final_price": (
        "FUNCTION final_price(price, is_member, coupon_percent)\n"
        "    IF is_member OR coupon_percent >= 20 THEN\n"
        "        price = price * 0.9\n    ENDIF\n"
        "    RETURN ROUND(price, 2)\n"
        "ENDFUNCTION\n"
    ),
    "ds.find_max": (
        "FUNCTION find_max(arr)\n"
        "    best = arr[0]\n"
        "    FOR i = 0 TO LENGTH(arr) - 1\n"
        "        IF arr[i] > best THEN\n            best = arr[i]\n        ENDIF\n"
        "    ENDFOR\n"
        "    RETURN best\n"
        "ENDFUNCTION\n"
    ),
    "ds.reverse_array": (
        "FUNCTION reverse_array(arr)\n"
        "    result = []\n"
        "    i = LENGTH(arr) - 1\n"
        "    WHILE i >= 0\n"
        "        result[LENGTH(result)] = arr[i]\n        i = i - 1\n"
        "    ENDWHILE\n"
        "    RETURN result\n"
        "ENDFUNCTION\n"
    ),
    "ds.array_average": (
        "FUNCTION array_average(arr)\n"
        "    total = 0\n    FOR i = 0 TO LENGTH(arr) - 1\n        total = total + arr[i]\n    ENDFOR\n"
        "    RETURN total / LENGTH(arr)\n"
        "ENDFUNCTION\n"
    ),
    "ds.matrix_transpose": (
        "FUNCTION matrix_transpose(grid)\n"
        "    result = []\n"
        "    FOR c = 0 TO LENGTH(grid[0]) - 1\n"
        "        FOR r = 0 TO LENGTH(grid) - 1\n"
        "            result[c][r] = grid[r][c]\n"
        "        ENDFOR\n"
        "    ENDFOR\n"
        "    RETURN result\n"
        "ENDFUNCTION\n"
    ),
    "ds.matrix_diagonal_sum": (
        "FUNCTION matrix_diagonal_sum(grid)\n"
        "    total = 0\n"
        "    FOR i = 0 TO LENGTH(grid) - 1\n        total = total + grid[i][i]\n    ENDFOR\n"
        "    RETURN total\n"
        "ENDFUNCTION\n"
    ),
    "ds.word_frequency": (
        "FUNCTION word_frequency(words)\n"
        "    freq = {}\n"
        "    FOR i = 0 TO LENGTH(words) - 1\n"
        "        w = words[i]\n"
        "        IF w == w THEN\n"
        "        ENDIF\n"
        "    ENDFOR\n"
        "    RETURN freq\n"
        "ENDFUNCTION\n"
    ),
    "ds.invert_dictionary": (
        "FUNCTION invert_dictionary(d)\n"
        "    RETURN d\n"
        "ENDFUNCTION\n"
    ),
    "algo.linear_search": (
        "FUNCTION linear_search(arr, target)\n"
        "    FOR i = 0 TO LENGTH(arr) - 1\n"
        "        IF arr[i] == target THEN\n            RETURN i\n        ENDIF\n"
        "    ENDFOR\n"
        "    RETURN -1\n"
        "ENDFUNCTION\n"
    ),
    "algo.binary_search": (
        "FUNCTION binary_search(arr, target)\n"
        "    lo = 0\n    hi = LENGTH(arr) - 1\n"
        "    WHILE lo <= hi\n"
        "        mid = (lo + hi) DIV 2\n"
        "        IF arr[mid] == target THEN\n            RETURN mid\n"
        "        ELSEIF arr[mid] < target THEN\n            lo = mid + 1\n"
        "        ELSE\n            hi = mid - 1\n        ENDIF\n"
        "    ENDWHILE\n"
        "    RETURN -1\n"
        "ENDFUNCTION\n"
    ),
    "algo.bubble_sort": (
        "FUNCTION bubble_sort(arr)\n"
        "    n = LENGTH(arr)\n"
        "    FOR i = 0 TO n - 1\n"
        "        FOR j = 0 TO n - i - 2\n"
        "            IF arr[j] > arr[j + 1] THEN\n"
        "                temp = arr[j]\n                arr[j] = arr[j + 1]\n                arr[j + 1] = temp\n"
        "            ENDIF\n"
        "        ENDFOR\n"
        "    ENDFOR\n"
        "    RETURN arr\n"
        "ENDFUNCTION\n"
    ),
    "algo.selection_sort": (
        "FUNCTION selection_sort(arr)\n"
        "    n = LENGTH(arr)\n"
        "    FOR i = 0 TO n - 1\n"
        "        min_idx = i\n"
        "        FOR j = i + 1 TO n - 1\n"
        "            IF arr[j] < arr[min_idx] THEN\n                min_idx = j\n            ENDIF\n"
        "        ENDFOR\n"
        "        temp = arr[i]\n        arr[i] = arr[min_idx]\n        arr[min_idx] = temp\n"
        "    ENDFOR\n"
        "    RETURN arr\n"
        "ENDFUNCTION\n"
    ),
    "algo.insertion_sort": (
        "FUNCTION insertion_sort(arr)\n"
        "    FOR i = 1 TO LENGTH(arr) - 1\n"
        "        key = arr[i]\n        j = i - 1\n"
        "        WHILE j >= 0 AND arr[j] > key\n"
        "            arr[j + 1] = arr[j]\n            j = j - 1\n"
        "        ENDWHILE\n"
        "        arr[j + 1] = key\n"
        "    ENDFOR\n"
        "    RETURN arr\n"
        "ENDFUNCTION\n"
    ),
    "rec.factorial": (
        "FUNCTION factorial_recursive(n)\n"
        "    IF n <= 1 THEN\n        RETURN 1\n    ENDIF\n"
        "    RETURN n * factorial_recursive(n - 1)\n"
        "ENDFUNCTION\n"
    ),
    "rec.fibonacci": (
        "FUNCTION fibonacci_recursive(n)\n"
        "    IF n < 2 THEN\n        RETURN n\n    ENDIF\n"
        "    RETURN fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)\n"
        "ENDFUNCTION\n"
    ),
    "rec.sum_digits": (
        "FUNCTION sum_digits_recursive(n)\n"
        "    IF n < 10 THEN\n        RETURN n\n    ENDIF\n"
        "    RETURN (n MOD 10) + sum_digits_recursive(n DIV 10)\n"
        "ENDFUNCTION\n"
    ),
    "rec.power": (
        "FUNCTION power_recursive(base, exp)\n"
        "    IF exp == 0 THEN\n        RETURN 1\n    ENDIF\n"
        "    RETURN base * power_recursive(base, exp - 1)\n"
        "ENDFUNCTION\n"
    ),
    "gpp.safe_divide": (
        "FUNCTION safe_divide(a, b)\n"
        "    IF b == 0 THEN\n        RETURN -999999\n    ENDIF\n"
        "    RETURN a / b\n"
        "ENDFUNCTION\n"
    ),
    "gpp.validate_and_square": (
        "FUNCTION validate_and_square(x)\n"
        "    IF x < 0 THEN\n        RETURN -999999\n    ENDIF\n"
        "    RETURN x * x\n"
        "ENDFUNCTION\n"
    ),
    "dbg.fix_off_by_one": (
        "FUNCTION count_negatives(nums)\n"
        "    count = 0\n"
        "    FOR i = 0 TO LENGTH(nums) - 1\n"
        "        IF nums[i] < 0 THEN\n            count = count + 1\n        ENDIF\n"
        "    ENDFOR\n"
        "    RETURN count\n"
        "ENDFUNCTION\n"
    ),
    "dbg.fix_safe_average": (
        "FUNCTION safe_average(nums)\n"
        "    IF LENGTH(nums) == 0 THEN\n        RETURN -999999\n    ENDIF\n"
        "    total = 0\n    FOR i = 0 TO LENGTH(nums) - 1\n        total = total + nums[i]\n    ENDFOR\n"
        "    RETURN total / LENGTH(nums)\n"
        "ENDFUNCTION\n"
    ),
    "dbg.fix_last_element": "FUNCTION get_last(arr)\n    RETURN arr[LENGTH(arr) - 1]\nENDFUNCTION\n",
}

OOP_SOLUTIONS = {
    "oop.rectangle": (
        "class Rectangle:\n"
        "    def __init__(self, width, height):\n        self.width = width\n        self.height = height\n\n"
        "    def area(self):\n        return self.width * self.height\n\n"
        "    def perimeter(self):\n        return 2 * (self.width + self.height)\n"
    ),
    "oop.bank_account": (
        "class BankAccount:\n"
        "    def __init__(self, balance):\n        self.balance = balance\n\n"
        "    def deposit(self, amount):\n        self.balance += amount\n\n"
        "    def withdraw(self, amount):\n        if amount <= self.balance:\n            self.balance -= amount\n\n"
        "    def get_balance(self):\n        return self.balance\n"
    ),
    "oop.inheritance_animal": (
        "class Animal:\n"
        "    def __init__(self, name):\n        self.name = name\n\n"
        "    def speak(self):\n        return '...'\n\n\n"
        "class Dog(Animal):\n"
        "    def speak(self):\n        return 'Woof!'\n"
    ),
    "oop.counter": (
        "class Counter:\n"
        "    def __init__(self):\n        self.count = 0\n\n"
        "    def increment(self):\n        self.count += 1\n\n"
        "    def reset(self):\n        self.count = 0\n\n"
        "    def get_count(self):\n        return self.count\n"
    ),
    "oop.student": (
        "class Student:\n"
        "    def __init__(self, name):\n        self.name = name\n        self.marks = []\n\n"
        "    def add_mark(self, mark):\n        self.marks.append(mark)\n\n"
        "    def average(self):\n"
        "        if len(self.marks) == 0:\n            return 0\n"
        "        total = 0\n        for m in self.marks:\n            total += m\n"
        "        return total / len(self.marks)\n"
    ),
    "oop.circle": (
        "import math\n\n\n"
        "class Circle:\n"
        "    def __init__(self, radius):\n        self.radius = radius\n\n"
        "    def area(self):\n        return math.pi * self.radius ** 2\n\n"
        "    def circumference(self):\n        return 2 * math.pi * self.radius\n"
    ),
}


def main():
    questions = {q.id: q for q in build_builtin_questions()}
    failures = []

    for qid, src in PY_SOLUTIONS.items():
        q = questions[qid]
        report = evaluate_python_submission(q, src)
        if not (report["all_passed"] and report["method_ok"]):
            failures.append(("PY-ref", qid, report))

    for qid, src in PC_SOLUTIONS.items():
        q = questions[qid]
        report = evaluate_pseudocode_submission(q, src)
        if not (report["all_passed"] and report["method_ok"]):
            failures.append(("PC-ref", qid, report))

    for qid, src in PY_CHEATS.items():
        q = questions[qid]
        report = evaluate_python_submission(q, src)
        if report["all_passed"] and report["method_ok"]:
            failures.append(("PY-cheat-not-caught", qid, report))

    for qid, src in OOP_SOLUTIONS.items():
        q = questions[qid]
        report = evaluate_oop_submission(q, src)
        if not report["all_passed"]:
            failures.append(("OOP-ref", qid, report))

    # Coverage check: every code/oop question needs a PY reference solution.
    for qid, q in questions.items():
        if q.qtype == "code" and qid not in PY_SOLUTIONS:
            failures.append(("MISSING-PY-SOLUTION", qid, None))
        if q.qtype == "code" and "pseudocode" in q.langs and qid not in PC_SOLUTIONS:
            failures.append(("MISSING-PC-SOLUTION", qid, None))
        if q.qtype == "oop" and qid not in OOP_SOLUTIONS:
            failures.append(("MISSING-OOP-SOLUTION", qid, None))
        if q.qtype == "quiz":
            assert 0 <= q.correct_index < len(q.choices), f"bad quiz choices: {qid}"

    if failures:
        print(f"\n{len(failures)} FAILURE(S):\n")
        for kind, qid, report in failures:
            print(f"--- {kind}: {qid} ---")
            if report:
                print("  all_passed:", report.get("all_passed"), "method_ok:", report.get("method_ok"),
                      "compile_error:", report.get("compile_error"))
                for t in report.get("tests", []):
                    if not t["passed"] or t.get("method_messages"):
                        print("   ", t)
        raise SystemExit(1)
    else:
        print(f"ALL GOOD -- {len(PY_SOLUTIONS)} python refs, {len(PC_SOLUTIONS)} pseudocode refs, "
              f"{len(PY_CHEATS)} cheat checks, {len(OOP_SOLUTIONS)} OOP refs all verified.")


if __name__ == "__main__":
    main()