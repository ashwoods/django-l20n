import ast
import json
import codegen

l20n_json = open('example.l20n.ast').read()
l20n_ast = json.loads(l20n_json)

body = []

def expression(expr):
    if expr['type'] == "Identifier":
        n = ast.Name(lineno=1, col_offset=0)
        n.id = str(expr['name'])
        n.ctx = ast.Load()
        c = ast.Call(lineno=1, col_offset=0)
        c.func = n
        c.args = []
        c.keywords = []
        c.starargs = None
        c.kwargs = None
        return c
    if expr['type'] == "VariableExpression":
        n = ast.Name(lineno=1, col_offset=0)
        n.id = str(expr['id']['name'])
        n.ctx = ast.Load()
        return n
    if expr['type'] == "String":
        s = ast.Str(lineno=1, col_offset=0)
        s.s = expr['content']
        return s
    if expr['type'] == "Number":
        n = ast.Num(lineno=1, col_offset=0)
        n.n = expr['value']
        return n
    if expr['type'] == "ConditionalExpression":
        i = ast.IfExp(lineno=1, col_offset=0)
        i.test = expression(expr['test'])
        i.body = expression(expr['consequent'])
        i.orelse = expression(expr['alternate'])
        return i
    if expr['type'] == "BinaryExpression":
        # L20n binary expr transpile into Python's BinOp or Compare
        if expr['operator']['token'] in ('==',):
            c = ast.Compare(lineno=1, col_offset=0)
            c.left = expression(expr['left'])
            c.ops = [ast.Eq()]
            c.comparators = [expression(expr['right'])]
            return c
        if expr['operator']['token'] in ('+',):
            b = ast.BinOp(lineno=1, col_offset=0)
            b.left = expression(expr['left'])
            b.op = ast.Add()
            b.right = expression(expr['right'])
            return b


def part(expr):
    if isinstance(expr, ast.BinOp):
        return expr
    return expression(expr)


def concat(left, right):
    op = ast.BinOp(lineno=1, col_offset=0)
    op.left = part(left)
    op.op = ast.Add()
    op.right = part(right)
    return op


def entity(entry):
    fn = ast.FunctionDef(lineno=1, col_offset=0)
    fn.name = str(entry['id']['name'])
    fn.args = ast.arguments(args=[], vararg=None, kwarg=None, defaults=[])
    fn.decorator_list = []

    if entry['value']['type'] != "String":
        # Strings are the only suported L20n data type for now
        return None
    ret = ast.Return(lineno=1, col_offset=0)
    if entry['value']['content']['type'] == "String":
        ret.value = ast.Str(lineno=1, col_offset=0)
        ret.value.s = entry['value']['content']['content']
    else:
        ret.value = reduce(concat, entry['value']['content']['content'])
    fn.body = [ret]
    return fn


def macro(entry):
    fn = ast.FunctionDef(lineno=1, col_offset=0)
    fn.name = str(entry['id']['name'])
    fn.decorator_list = []
    args = []
    for arg in entry['args']:
        if arg['type'] != "VariableExpression":
            continue
        a = ast.Name(lineno=1, col_offset=0)
        a.id = str(arg['id']['name'])
        a.ctx = ast.Param()
        args.append(a)
    fn.args = ast.arguments(args=args, vararg=None, kwarg=None, defaults=[])

    ret = ast.Return(lineno=1, col_offset=0)
    ret.value = expression(entry['expression'])
    fn.body = [ret]
    return fn



for entry in l20n_ast['body']:
    if entry['type'] == "Entity":
        fn = entity(entry)
    elif entry['type'] == "Macro":
        fn = macro(entry)
    if fn is not None:
        body.append(fn)

mod = ast.Module(body)
import codegen
print codegen.to_source(mod)
context = {}
exec compile(mod, '<string>', 'exec') in context
print context['plurals'](1)
