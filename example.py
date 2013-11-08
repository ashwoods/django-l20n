def foo():
    return "Foo"

def bar():
    return foo() + " Bar " + foo()

def plurals(n):
    if n == 1:
        return "one"
    else:
        return "many"
