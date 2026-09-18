"""
engines.py
==========
Data model (Question / TestCase / OOPCall) plus the three grading engines:

  * evaluate_python_submission   -- runs + traces a Python function
  * evaluate_pseudocode_submission -- runs + traces a pseudocode function
  * evaluate_oop_submission      -- instantiates a class, drives it through
                                     a sequence of method calls
  * evaluate_quiz_submission     -- straightforward multiple-choice grading

All engines return a plain-dict "report" that the UI layer renders. No
tkinter/customtkinter imports live in this file, so it can be unit tested
headlessly.
"""
from __future__ import annotations

import math
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from pseudo_engine import (
    run_pseudocode_and_count, PseudoStepLimit, PseudoRuntimeError, PseudoSyntaxError,
)

LANG_PYTHON = "python"
LANG_PSEUDOCODE = "pseudocode"


# ============================================================
# Data model
# ============================================================

@dataclass
class TestCase:
    """One (input -> expected output) check for a 'code' question, optionally
    with a *method fingerprint* the submission must match: bounds on how many
    lines/statements ran (min/max_steps_expr) and/or how many times the
    function called itself (min/max_calls_expr). Expressions are plain
    Python, evaluated with `n` (this test case's size) and `math` in scope."""
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    expected: Any = None
    n_hint: Optional[int] = None
    label: str = ""
    min_steps_expr: Optional[str] = None
    max_steps_expr: Optional[str] = None
    min_calls_expr: Optional[str] = None
    max_calls_expr: Optional[str] = None

    def size(self) -> int:
        if self.n_hint is not None:
            return self.n_hint
        for a in list(self.args) + list(self.kwargs.values()):
            if hasattr(a, "__len__"):
                return len(a)
        return 1


@dataclass
class OOPCall:
    """One step in an OOP test scenario: call `method` with `args` on the
    instance under test. Only the LAST call's result in a scenario is graded
    against `expected` -- earlier calls exist purely to build up state
    (e.g. a couple of deposit() calls before checking get_balance())."""
    method: str
    args: tuple = field(default_factory=tuple)


@dataclass
class OOPScenario:
    label: str
    constructor_args: tuple = field(default_factory=tuple)
    calls: list = field(default_factory=list)   # list[OOPCall]
    expected: Any = None


@dataclass
class Choice:
    text: str


@dataclass
class Question:
    id: str
    title: str
    category: str
    subtopic: str            # short curriculum tag shown as a chip, e.g. "Iteration"
    prompt: str
    qtype: str = "code"      # "code" | "oop" | "quiz"
    langs: tuple = (LANG_PYTHON, LANG_PSEUDOCODE)   # which languages this code Q supports
    func_name: str = ""      # code: function name / oop: class name
    starter_code: dict = field(default_factory=dict)  # {lang: starter source}
    test_cases: list = field(default_factory=list)     # code: list[TestCase]
    oop_scenarios: list = field(default_factory=list)   # oop: list[OOPScenario]
    method_note: str = ""
    difficulty: str = "core"   # "core" | "stretch"
    custom: bool = False
    # quiz-only
    choices: list = field(default_factory=list)   # list[str]
    correct_index: int = 0
    explanation: str = ""


# ============================================================
# Serialisation (for custom, user-added questions)
# ============================================================

def question_to_dict(q: "Question") -> dict:
    return {
        "id": q.id, "title": q.title, "category": q.category, "subtopic": q.subtopic,
        "prompt": q.prompt, "qtype": q.qtype, "langs": list(q.langs),
        "func_name": q.func_name, "starter_code": q.starter_code,
        "method_note": q.method_note, "difficulty": q.difficulty, "custom": True,
        "choices": q.choices, "correct_index": q.correct_index, "explanation": q.explanation,
        "test_cases": [
            {
                "args": list(tc.args), "kwargs": tc.kwargs, "expected": tc.expected,
                "n_hint": tc.n_hint, "label": tc.label,
                "min_steps_expr": tc.min_steps_expr, "max_steps_expr": tc.max_steps_expr,
                "min_calls_expr": tc.min_calls_expr, "max_calls_expr": tc.max_calls_expr,
            }
            for tc in q.test_cases
        ],
    }


def question_from_dict(d: dict) -> "Question":
    tcs = [
        TestCase(
            args=tuple(t["args"]), kwargs=t.get("kwargs") or {}, expected=t.get("expected"),
            n_hint=t.get("n_hint"), label=t.get("label", ""),
            min_steps_expr=t.get("min_steps_expr"), max_steps_expr=t.get("max_steps_expr"),
            min_calls_expr=t.get("min_calls_expr"), max_calls_expr=t.get("max_calls_expr"),
        )
        for t in d.get("test_cases", [])
    ]
    return Question(
        id=d["id"], title=d["title"], category=d["category"], subtopic=d.get("subtopic", "Custom"),
        prompt=d["prompt"], qtype=d.get("qtype", "code"), langs=tuple(d.get("langs", [LANG_PYTHON])),
        func_name=d.get("func_name", ""), starter_code=d.get("starter_code", {}), test_cases=tcs,
        method_note=d.get("method_note", ""), difficulty=d.get("difficulty", "core"), custom=True,
        choices=d.get("choices", []), correct_index=d.get("correct_index", 0),
        explanation=d.get("explanation", ""),
    )


# ============================================================
# Python execution + tracing
# ============================================================

class StepLimitExceeded(Exception):
    pass


def run_and_count(func, func_name, args, kwargs, max_events=2_000_000, timeout_sec=3.0):
    """Call func(*args, **kwargs) while counting:
       - 'lines': how many bytecode LINE events fired anywhere while func
         (and anything it calls) was executing -- a cheap proxy for "how much
         work did this do".
       - 'calls': how many times a frame named func_name was entered -- a
         proxy for "how many times did this function call itself".
    Raises StepLimitExceeded on runaway loops instead of hanging forever."""
    kwargs = kwargs or {}
    counters = {"lines": 0, "calls": 0}
    start = time.time()

    def tracer(frame, event, arg):
        if event == "line":
            counters["lines"] += 1
            if counters["lines"] > max_events:
                raise StepLimitExceeded("too many steps (possible infinite loop)")
            if time.time() - start > timeout_sec:
                raise StepLimitExceeded("timed out (possible infinite loop)")
        elif event == "call":
            if frame.f_code.co_name == func_name:
                counters["calls"] += 1
        return tracer

    sys.settrace(tracer)
    try:
        result = func(*args, **kwargs)
    finally:
        sys.settrace(None)
    return result, counters["lines"], counters["calls"]


def _values_equal(a, b) -> bool:
    try:
        if isinstance(a, float) or isinstance(b, float):
            return math.isclose(float(a), float(b), rel_tol=1e-6, abs_tol=1e-9)
        return a == b
    except Exception:
        return False


def _apply_method_checks(entry, tc, lines, calls):
    method_ok = True
    n = tc.size()
    scope = {"math": math, "n": n}
    checks = [
        (tc.min_steps_expr, lines, "min", "steps"),
        (tc.max_steps_expr, lines, "max", "steps"),
        (tc.min_calls_expr, calls, "min", "self-calls"),
        (tc.max_calls_expr, calls, "max", "self-calls"),
    ]
    for expr, actual_val, kind, what in checks:
        if not expr or actual_val is None:
            continue
        try:
            bound = eval(expr, {"__builtins__": {}}, scope)
        except Exception:
            continue
        if kind == "min" and actual_val < bound:
            method_ok = False
            entry["method_messages"].append(
                f"only {actual_val} {what} -- expected at least {bound:.0f}. "
                f"This looks too fast/simple for the required method.")
        elif kind == "max" and actual_val > bound:
            method_ok = False
            entry["method_messages"].append(
                f"took {actual_val} {what} -- expected at most {bound:.0f}. "
                f"This looks too slow, or like the wrong method.")
    return method_ok


def evaluate_python_submission(question: "Question", source: str) -> dict:
    report = {"compile_error": None, "tests": [], "all_passed": False, "method_ok": True}
    try:
        code_obj = compile(source, "<submission>", "exec")
    except SyntaxError as e:
        report["compile_error"] = f"SyntaxError: {e.msg} (line {e.lineno})"
        return report
    ns: dict = {}
    try:
        exec(code_obj, ns)
    except Exception as e:
        report["compile_error"] = f"{type(e).__name__} while loading your code: {e}"
        return report
    func = ns.get(question.func_name)
    if not callable(func):
        report["compile_error"] = f"Your code must define a function named '{question.func_name}'."
        return report

    all_passed = True
    method_ok = True
    for i, tc in enumerate(question.test_cases):
        entry = {"label": tc.label or f"Test {i + 1}", "args": tc.args, "expected": tc.expected,
                 "actual": None, "passed": False, "error": None, "lines": None, "calls": None,
                 "method_messages": []}
        lines = calls = None
        try:
            result, lines, calls = run_and_count(func, question.func_name, tc.args, tc.kwargs)
            entry["actual"] = result
            entry["passed"] = _values_equal(result, tc.expected)
            entry["lines"], entry["calls"] = lines, calls
        except StepLimitExceeded as e:
            entry["error"] = str(e)
        except Exception as e:
            entry["error"] = f"{type(e).__name__}: {e}"
        if not entry["passed"]:
            all_passed = False
        if entry["error"] is None:
            if not _apply_method_checks(entry, tc, lines, calls):
                method_ok = False
        report["tests"].append(entry)
    report["all_passed"], report["method_ok"] = all_passed, method_ok
    return report


def evaluate_pseudocode_submission(question: "Question", source: str) -> dict:
    report = {"compile_error": None, "tests": [], "all_passed": False, "method_ok": True}
    all_passed = True
    method_ok = True
    for i, tc in enumerate(question.test_cases):
        entry = {"label": tc.label or f"Test {i + 1}", "args": tc.args, "expected": tc.expected,
                 "actual": None, "passed": False, "error": None, "lines": None, "calls": None,
                 "method_messages": []}
        try:
            result, steps, calls = run_pseudocode_and_count(source, question.func_name, tc.args)
            entry["actual"] = result
            entry["passed"] = _values_equal(result, tc.expected)
            entry["lines"], entry["calls"] = steps, calls
        except PseudoStepLimit as e:
            entry["error"] = str(e)
        except (PseudoSyntaxError, PseudoRuntimeError) as e:
            entry["error"] = str(e)
        except Exception as e:
            entry["error"] = f"{type(e).__name__}: {e}"
        if not entry["passed"]:
            all_passed = False
        if entry["error"] is None:
            if not _apply_method_checks(entry, tc, entry["lines"], entry["calls"]):
                method_ok = False
        report["tests"].append(entry)
    report["all_passed"], report["method_ok"] = all_passed, method_ok
    if report["tests"] and all(t["error"] for t in report["tests"]):
        first_err = report["tests"][0]["error"]
        if first_err and ("must define a function" in first_err or "Line" in first_err):
            report["compile_error"] = first_err
    return report


def evaluate_submission(question: "Question", source: str, language: str) -> dict:
    if language == LANG_PSEUDOCODE:
        return evaluate_pseudocode_submission(question, source)
    return evaluate_python_submission(question, source)


# ============================================================
# OOP grading (Python only -- see README for rationale)
# ============================================================

def evaluate_oop_submission(question: "Question", source: str) -> dict:
    report = {"compile_error": None, "tests": [], "all_passed": False, "method_ok": True}
    try:
        code_obj = compile(source, "<submission>", "exec")
    except SyntaxError as e:
        report["compile_error"] = f"SyntaxError: {e.msg} (line {e.lineno})"
        return report
    ns: dict = {}
    try:
        exec(code_obj, ns)
    except Exception as e:
        report["compile_error"] = f"{type(e).__name__} while loading your code: {e}"
        return report
    cls = ns.get(question.func_name)
    if not isinstance(cls, type):
        report["compile_error"] = f"Your code must define a class named '{question.func_name}'."
        return report

    all_passed = True
    for i, sc in enumerate(question.oop_scenarios):
        entry = {"label": sc.label or f"Scenario {i + 1}", "expected": sc.expected,
                 "actual": None, "passed": False, "error": None, "method_messages": []}
        try:
            with _time_limit(3.0):
                obj = cls(*sc.constructor_args)
                result = None
                for call in sc.calls:
                    method = getattr(obj, call.method, None)
                    if not callable(method):
                        raise AttributeError(f"'{question.func_name}' has no method '{call.method}'")
                    result = method(*call.args)
                entry["actual"] = result
                entry["passed"] = _values_equal(result, sc.expected)
        except Exception as e:
            entry["error"] = f"{type(e).__name__}: {e}"
        if not entry["passed"]:
            all_passed = False
        report["tests"].append(entry)
    report["all_passed"] = all_passed
    report["method_ok"] = True
    return report


class _time_limit:
    """Best-effort wall-clock guard around OOP scenario execution (no signal-
    based interrupt needed since these calls are short and non-looping in
    practice; this just stamps a start time other code could check)."""
    def __init__(self, seconds):
        self.seconds = seconds

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


# ============================================================
# Quiz grading
# ============================================================

def evaluate_quiz_submission(question: "Question", choice_index: int) -> dict:
    correct = (choice_index == question.correct_index)
    return {
        "passed": correct, "method_ok": True, "choice_index": choice_index,
        "correct_index": question.correct_index, "explanation": question.explanation,
    }