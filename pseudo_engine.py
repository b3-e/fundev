"""
pseudo_engine.py
=================
A small tokenizer / recursive-descent parser / tree-walking interpreter for
the pseudocode dialect used throughout the WA Computer Science ATAR syllabus
(IF/THEN/ELSE/ENDIF, WHILE/ENDWHILE, REPEAT/UNTIL, FOR/TO/STEP/ENDFOR,
FUNCTION/ENDFUNCTION, arrays with [..] literals, dictionaries with {k:v}
literals, and the usual arithmetic/relational/logical operators).

No third-party dependencies -- pure stdlib, so it can be unit tested and
imported without a GUI toolkit available.
"""
from __future__ import annotations

import re
import time

# ============================================================
# Tokenizer
# ============================================================

KEYWORDS = {
    'FUNCTION', 'ENDFUNCTION', 'PROCEDURE', 'ENDPROCEDURE', 'RETURN',
    'IF', 'THEN', 'ELSE', 'ELSEIF', 'ENDIF',
    'WHILE', 'DO', 'ENDWHILE', 'REPEAT', 'UNTIL',
    'FOR', 'TO', 'STEP', 'ENDFOR',
    'OUTPUT', 'PRINT',
    'AND', 'OR', 'NOT', 'MOD', 'DIV',
    'TRUE', 'FALSE',
}

_TOKEN_RE = re.compile(r"""
    (?P<NUMBER>\d+\.\d+|\d+)
  | (?P<STRING>"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')
  | (?P<OP2>==|!=|<=|>=|<-)
  | (?P<OP1>[+\-*/=<>])
  | (?P<LBRACKET>\[)
  | (?P<RBRACKET>\])
  | (?P<LBRACE>\{)
  | (?P<RBRACE>\})
  | (?P<LPAREN>\()
  | (?P<RPAREN>\))
  | (?P<COMMA>,)
  | (?P<COLON>:)
  | (?P<NEWLINE>\n)
  | (?P<SKIP>[ \t\r]+)
  | (?P<COMMENT>//[^\n]*|\#[^\n]*)
  | (?P<NAME>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<MISMATCH>.)
""", re.VERBOSE)


class PseudoSyntaxError(Exception):
    pass


def tokenize(source: str):
    tokens = []
    line = 1
    for m in _TOKEN_RE.finditer(source):
        kind = m.lastgroup
        text = m.group()
        if kind == 'SKIP' or kind == 'COMMENT':
            continue
        if kind == 'NEWLINE':
            tokens.append(('NEWLINE', '\n', line))
            line += 1
            continue
        if kind == 'NUMBER':
            val = float(text) if '.' in text else int(text)
            tokens.append(('NUMBER', val, line))
        elif kind == 'STRING':
            tokens.append(('STRING', text[1:-1], line))
        elif kind == 'NAME':
            upper = text.upper()
            if upper in KEYWORDS:
                tokens.append((upper, text, line))
            else:
                tokens.append(('NAME', text, line))
        elif kind == 'MISMATCH':
            raise PseudoSyntaxError(f"Unexpected character {text!r} on line {line}")
        else:
            tokens.append((kind if kind not in ('OP1', 'OP2') else text, text, line))
    tokens.append(('EOF', '', line))
    return tokens


# ============================================================
# Parser (recursive descent) -> tuple-tagged AST nodes
# ============================================================

class Parser:
    def __init__(self, tokens):
        self.toks = tokens
        self.pos = 0

    def peek(self):
        return self.toks[self.pos]

    def at(self, *types):
        return self.toks[self.pos][0] in types

    def advance(self):
        t = self.toks[self.pos]
        self.pos += 1
        return t

    def expect(self, ttype):
        t = self.toks[self.pos]
        if t[0] != ttype:
            raise PseudoSyntaxError(f"Line {t[2]}: expected {ttype}, got {t[0]} ({t[1]!r})")
        self.pos += 1
        return t

    def skip_newlines(self):
        while self.at('NEWLINE'):
            self.pos += 1

    def parse_program(self):
        stmts = []
        self.skip_newlines()
        while not self.at('EOF'):
            stmts.append(self.parse_statement())
            self.skip_newlines()
        return stmts

    def parse_block(self, stop_types):
        stmts = []
        self.skip_newlines()
        while self.peek()[0] not in stop_types:
            stmts.append(self.parse_statement())
            self.skip_newlines()
        return stmts

    def parse_statement(self):
        ttype = self.peek()[0]
        if ttype in ('FUNCTION', 'PROCEDURE'):
            return self.parse_funcdef()
        if ttype == 'IF':
            return self.parse_if()
        if ttype == 'WHILE':
            return self.parse_while()
        if ttype == 'REPEAT':
            return self.parse_repeat()
        if ttype == 'FOR':
            return self.parse_for()
        if ttype == 'RETURN':
            return self.parse_return()
        if ttype in ('OUTPUT', 'PRINT'):
            return self.parse_output()
        return self.parse_assign_or_expr()

    def parse_funcdef(self):
        end_kw = 'ENDFUNCTION' if self.peek()[0] == 'FUNCTION' else 'ENDPROCEDURE'
        self.advance()
        name = self.expect('NAME')[1]
        self.expect('LPAREN')
        params = []
        if not self.at('RPAREN'):
            params.append(self.expect('NAME')[1])
            while self.at('COMMA'):
                self.advance()
                params.append(self.expect('NAME')[1])
        self.expect('RPAREN')
        body = self.parse_block({end_kw, 'EOF'})
        self.expect(end_kw)
        return ('funcdef', name, params, body)

    def parse_if(self):
        self.advance()
        branches = []
        cond = self.parse_expr()
        self.expect('THEN')
        body = self.parse_block({'ELSE', 'ELSEIF', 'ENDIF', 'EOF'})
        branches.append((cond, body))
        while self.at('ELSEIF'):
            self.advance()
            cond2 = self.parse_expr()
            self.expect('THEN')
            body2 = self.parse_block({'ELSE', 'ELSEIF', 'ENDIF', 'EOF'})
            branches.append((cond2, body2))
        else_body = None
        if self.at('ELSE'):
            self.advance()
            else_body = self.parse_block({'ENDIF', 'EOF'})
        self.expect('ENDIF')
        return ('if', branches, else_body)

    def parse_while(self):
        self.advance()
        cond = self.parse_expr()
        if self.at('DO'):
            self.advance()
        body = self.parse_block({'ENDWHILE', 'EOF'})
        self.expect('ENDWHILE')
        return ('while', cond, body)

    def parse_repeat(self):
        self.advance()
        body = self.parse_block({'UNTIL', 'EOF'})
        self.expect('UNTIL')
        cond = self.parse_expr()
        return ('repeat', body, cond)

    def parse_for(self):
        self.advance()
        var = self.expect('NAME')[1]
        if self.at('=') or self.at('<-'):
            self.advance()
        else:
            self.expect('=')
        start_e = self.parse_expr()
        self.expect('TO')
        end_e = self.parse_expr()
        step_e = None
        if self.at('STEP'):
            self.advance()
            step_e = self.parse_expr()
        body = self.parse_block({'ENDFOR', 'EOF'})
        self.expect('ENDFOR')
        return ('for', var, start_e, end_e, step_e, body)

    def parse_return(self):
        self.advance()
        if self.at('NEWLINE', 'EOF') or self.peek()[0] in _BLOCK_ENDERS:
            return ('return', None)
        expr = self.parse_expr()
        return ('return', expr)

    def parse_output(self):
        self.advance()
        exprs = [self.parse_expr()]
        while self.at('COMMA'):
            self.advance()
            exprs.append(self.parse_expr())
        return ('output', exprs)

    def parse_assign_or_expr(self):
        expr = self.parse_expr()
        if self.at('=', '<-'):
            self.advance()
            if expr[0] not in ('var', 'index'):
                raise PseudoSyntaxError("Left-hand side of assignment must be a variable")
            rhs = self.parse_expr()
            return ('assign', expr, rhs)
        return ('exprstmt', expr)

    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        node = self.parse_and()
        while self.at('OR'):
            self.advance()
            rhs = self.parse_and()
            node = ('binop', 'OR', node, rhs)
        return node

    def parse_and(self):
        node = self.parse_not()
        while self.at('AND'):
            self.advance()
            rhs = self.parse_not()
            node = ('binop', 'AND', node, rhs)
        return node

    def parse_not(self):
        if self.at('NOT'):
            self.advance()
            return ('unary', 'NOT', self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self):
        node = self.parse_additive()
        while self.at('==', '!=', '<', '>', '<=', '>='):
            op = self.advance()[0]
            rhs = self.parse_additive()
            node = ('binop', op, node, rhs)
        return node

    def parse_additive(self):
        node = self.parse_multiplicative()
        while self.at('+', '-'):
            op = self.advance()[0]
            rhs = self.parse_multiplicative()
            node = ('binop', op, node, rhs)
        return node

    def parse_multiplicative(self):
        node = self.parse_unary()
        while self.at('*', '/', 'MOD', 'DIV'):
            op = self.advance()[0]
            rhs = self.parse_unary()
            node = ('binop', op, node, rhs)
        return node

    def parse_unary(self):
        if self.at('-'):
            self.advance()
            return ('unary', '-', self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        while self.at('LBRACKET'):
            self.advance()
            idx = self.parse_expr()
            self.expect('RBRACKET')
            node = ('index', node, idx)
        return node

    def parse_primary(self):
        t = self.peek()
        if t[0] == 'NUMBER':
            self.advance()
            return ('num', t[1])
        if t[0] == 'STRING':
            self.advance()
            return ('str', t[1])
        if t[0] == 'TRUE':
            self.advance()
            return ('bool', True)
        if t[0] == 'FALSE':
            self.advance()
            return ('bool', False)
        if t[0] == 'LPAREN':
            self.advance()
            e = self.parse_expr()
            self.expect('RPAREN')
            return e
        if t[0] == 'LBRACKET':
            self.advance()
            elems = []
            if not self.at('RBRACKET'):
                elems.append(self.parse_expr())
                while self.at('COMMA'):
                    self.advance()
                    elems.append(self.parse_expr())
            self.expect('RBRACKET')
            return ('arraylit', elems)
        if t[0] == 'LBRACE':
            self.advance()
            pairs = []
            if not self.at('RBRACE'):
                k = self.parse_expr()
                self.expect('COLON')
                v = self.parse_expr()
                pairs.append((k, v))
                while self.at('COMMA'):
                    self.advance()
                    k2 = self.parse_expr()
                    self.expect('COLON')
                    v2 = self.parse_expr()
                    pairs.append((k2, v2))
            self.expect('RBRACE')
            return ('dictlit', pairs)
        if t[0] == 'NAME':
            self.advance()
            name = t[1]
            if self.at('LPAREN'):
                self.advance()
                args = []
                if not self.at('RPAREN'):
                    args.append(self.parse_expr())
                    while self.at('COMMA'):
                        self.advance()
                        args.append(self.parse_expr())
                self.expect('RPAREN')
                return ('call', name, args)
            return ('var', name)
        raise PseudoSyntaxError(f"Line {t[2]}: unexpected token {t[0]} ({t[1]!r})")


_BLOCK_ENDERS = {'ELSE', 'ELSEIF', 'ENDIF', 'ENDWHILE', 'UNTIL', 'ENDFOR',
                  'ENDFUNCTION', 'ENDPROCEDURE', 'EOF'}


def parse(source: str):
    return Parser(tokenize(source)).parse_program()


# ============================================================
# Interpreter
# ============================================================

class PseudoStepLimit(Exception):
    pass


class PseudoRuntimeError(Exception):
    pass


class _Return(Exception):
    def __init__(self, value):
        self.value = value


def truthy(v):
    return bool(v)


def apply_binop(op, l, r):
    if op == '+':
        return l + r
    if op == '-':
        return l - r
    if op == '*':
        return l * r
    if op == '/':
        return l / r
    if op == 'MOD':
        return l % r
    if op == 'DIV':
        return int(l) // int(r)
    if op == '==':
        return l == r
    if op == '!=':
        return l != r
    if op == '<':
        return l < r
    if op == '>':
        return l > r
    if op == '<=':
        return l <= r
    if op == '>=':
        return l >= r
    raise PseudoRuntimeError(f"Unknown operator {op}")


class PseudoInterp:
    def __init__(self, program_stmts, trace_name=None, max_steps=300_000, timeout_sec=3.0):
        self.funcs = {}
        self.globals = {}
        self.steps = 0
        self.calls = 0
        self.trace_key = (trace_name or '').upper()
        self.max_steps = max_steps
        self.timeout_sec = timeout_sec
        self.start = None
        prelude = []
        for stmt in program_stmts:
            if stmt[0] == 'funcdef':
                _, name, params, body = stmt
                self.funcs[name.upper()] = (params, body)
            else:
                prelude.append(stmt)
        self._prelude = prelude

    def run_prelude(self):
        self.start = time.time()
        self.exec_block(self._prelude, self.globals)

    def call(self, name, args):
        if self.start is None:
            self.start = time.time()
        return self.call_any(name, list(args))

    def tick(self):
        self.steps += 1
        if self.steps > self.max_steps:
            raise PseudoStepLimit("too many steps (possible infinite loop)")
        if time.time() - self.start > self.timeout_sec:
            raise PseudoStepLimit("timed out (possible infinite loop)")

    def exec_block(self, stmts, scope):
        for stmt in stmts:
            self.exec_stmt(stmt, scope)

    def exec_stmt(self, stmt, scope):
        self.tick()
        tag = stmt[0]
        if tag == 'assign':
            _, target, expr = stmt
            val = self.eval(expr, scope)
            self.assign_target(target, val, scope)
        elif tag == 'if':
            _, branches, else_body = stmt
            for cond, body in branches:
                if truthy(self.eval(cond, scope)):
                    self.exec_block(body, scope)
                    return
            if else_body is not None:
                self.exec_block(else_body, scope)
        elif tag == 'while':
            _, cond, body = stmt
            while truthy(self.eval(cond, scope)):
                self.exec_block(body, scope)
                self.tick()
        elif tag == 'repeat':
            _, body, cond = stmt
            while True:
                self.exec_block(body, scope)
                self.tick()
                if truthy(self.eval(cond, scope)):
                    break
        elif tag == 'for':
            _, var, start_e, end_e, step_e, body = stmt
            i = self.eval(start_e, scope)
            end_v = self.eval(end_e, scope)
            step_v = self.eval(step_e, scope) if step_e is not None else 1
            if step_v == 0:
                raise PseudoRuntimeError("FOR step cannot be 0")
            while (step_v > 0 and i <= end_v) or (step_v < 0 and i >= end_v):
                scope[var] = i
                self.exec_block(body, scope)
                i += step_v
                self.tick()
        elif tag == 'return':
            _, expr = stmt
            val = self.eval(expr, scope) if expr is not None else None
            raise _Return(val)
        elif tag == 'output':
            _, exprs = stmt
            for e in exprs:
                self.eval(e, scope)
        elif tag == 'exprstmt':
            _, expr = stmt
            self.eval(expr, scope)
        else:
            raise PseudoRuntimeError(f"Unknown statement '{tag}'")

    def get_container_ref(self, node, scope):
        if node[0] == 'var':
            name = node[1]
            if name not in scope:
                scope[name] = []
            return scope[name]
        elif node[0] == 'index':
            base = self.get_container_ref(node[1], scope)
            idx = self.eval(node[2], scope)
            if isinstance(base, dict):
                if idx not in base:
                    base[idx] = []
                return base[idx]
            elif isinstance(base, list):
                i = int(idx)
                while i >= len(base):
                    base.append([])
                return base[i]
            raise PseudoRuntimeError("Cannot index into this value")
        raise PseudoRuntimeError("Invalid assignment target")

    def assign_target(self, target, value, scope):
        if target[0] == 'var':
            scope[target[1]] = value
        elif target[0] == 'index':
            container = self.get_container_ref(target[1], scope)
            idx_val = self.eval(target[2], scope)
            if isinstance(container, dict):
                container[idx_val] = value
            elif isinstance(container, list):
                i = int(idx_val)
                while i >= len(container):
                    container.append(None)
                container[i] = value
            else:
                raise PseudoRuntimeError("Cannot index-assign into this value")
        else:
            raise PseudoRuntimeError("Invalid assignment target")

    def eval(self, node, scope):
        tag = node[0]
        if tag == 'num':
            return node[1]
        if tag == 'str':
            return node[1]
        if tag == 'bool':
            return node[1]
        if tag == 'arraylit':
            return [self.eval(e, scope) for e in node[1]]
        if tag == 'dictlit':
            return {self.eval(k, scope): self.eval(v, scope) for k, v in node[1]}
        if tag == 'var':
            name = node[1]
            if name in scope:
                return scope[name]
            if name in self.globals:
                return self.globals[name]
            raise PseudoRuntimeError(f"Undefined variable '{name}'")
        if tag == 'index':
            base = self.eval(node[1], scope)
            idx = self.eval(node[2], scope)
            if isinstance(base, dict):
                if idx not in base:
                    raise PseudoRuntimeError(f"Key {idx!r} not found")
                return base[idx]
            if isinstance(base, (list, str)):
                i = int(idx)
                try:
                    return base[i]
                except IndexError:
                    raise PseudoRuntimeError(f"Index {i} out of range")
            raise PseudoRuntimeError("Cannot index this value")
        if tag == 'binop':
            op = node[1]
            if op == 'AND':
                return truthy(self.eval(node[2], scope)) and truthy(self.eval(node[3], scope))
            if op == 'OR':
                return truthy(self.eval(node[2], scope)) or truthy(self.eval(node[3], scope))
            l = self.eval(node[2], scope)
            r = self.eval(node[3], scope)
            return apply_binop(op, l, r)
        if tag == 'unary':
            op = node[1]
            v = self.eval(node[2], scope)
            if op == '-':
                return -v
            if op == 'NOT':
                return not truthy(v)
            raise PseudoRuntimeError("Bad unary operator")
        if tag == 'call':
            name = node[1]
            args = [self.eval(a, scope) for a in node[2]]
            return self.call_any(name, args)
        raise PseudoRuntimeError(f"Cannot evaluate node '{tag}'")

    def call_any(self, name, args):
        key = name.upper()
        if key in self.funcs:
            if key == self.trace_key:
                self.calls += 1
            params, body = self.funcs[key]
            scope = {}
            for p, a in zip(params, args):
                scope[p] = a
            try:
                self.exec_block(body, scope)
            except _Return as r:
                return r.value
            return None
        if key == 'LENGTH':
            return len(args[0])
        if key == 'APPEND':
            return list(args[0]) + [args[1]]
        if key == 'ABS':
            return abs(args[0])
        if key == 'ROUND':
            return round(*args)
        if key == 'INT':
            return int(args[0])
        if key == 'STR':
            return str(args[0])
        if key == 'FLOAT':
            return float(args[0])
        if key == 'MAX':
            return max(args) if len(args) > 1 else max(args[0])
        if key == 'MIN':
            return min(args) if len(args) > 1 else min(args[0])
        if key == 'UPPER':
            return str(args[0]).upper()
        if key == 'LOWER':
            return str(args[0]).lower()
        if key == 'CONCAT':
            return ''.join(str(a) for a in args)
        if key == 'CONTAINS':
            container, item = args[0], args[1]
            if isinstance(container, dict):
                return item in container
            return item in container
        if key == 'KEYS':
            return list(args[0].keys())
        raise PseudoRuntimeError(f"Unknown function '{name}'")


def run_pseudocode_and_count(source, func_name, args, max_events=300_000, timeout_sec=3.0):
    """Mirrors the Python engine's run_and_count()'s signature/semantics."""
    stmts = parse(source)
    interp = PseudoInterp(stmts, trace_name=func_name, max_steps=max_events, timeout_sec=timeout_sec)
    interp.run_prelude()
    if func_name.upper() not in interp.funcs:
        raise PseudoRuntimeError(f"Your code must define a function named '{func_name}'.")
    result = interp.call(func_name, args)
    return result, interp.steps, interp.calls