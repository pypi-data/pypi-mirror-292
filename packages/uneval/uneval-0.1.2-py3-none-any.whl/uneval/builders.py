import ast
from typing import Sequence, Mapping, Iterable

from .convert_code import to_ast
from .expression import Expression


def and_(*values):
    node = ast.BoolOp(ast.And(), [to_ast(expr) for expr in values])
    return Expression(node)


def or_(*values):
    node = ast.BoolOp(ast.Or(), [to_ast(expr) for expr in values])
    return Expression(node)


def not_(expr):
    node = ast.UnaryOp(ast.Not(), to_ast(expr))
    return Expression(node)


def in_(element, coll):
    node = ast.Compare(to_ast(element), [ast.In()], [to_ast(coll)])
    return Expression(node)


class _NameQuoter:
    """Helper to create symbols."""
    def __getattr__(self, item) -> Expression:
        return self(item)

    def __call__(self, item) -> Expression:
        return Expression(ast.Name(item, ctx=ast.Load()))


quote = _NameQuoter()


def if_(test, body, orelse=True) -> Expression:
    """Create an if expression."""
    test, body = to_ast(test), to_ast(body)
    if orelse is True:  # TODO Should we keep this optimalisation?
        node = ast.BoolOp(ast.Or(), values=[ast.UnaryOp(ast.Not(), test), body])
    else:
        node = ast.IfExp(test, body, to_ast(orelse))
    return Expression(node)


def for_(element, *generators, type=None) -> Expression:
    """Create a for-comprehension."""
    element = to_ast(element)
    generators = [_comprehension(gen) for gen in generators]

    if type is None or type is iter:
        res = ast.GeneratorExp(element, generators)
    elif type is list:
        res = ast.ListComp(element, generators)
    elif type is set:
        res = ast.SetComp(element, generators)
    elif type is dict:
        key, value = element
        res = ast.DictComp(key, value, generators)
    else:
        raise TypeError(f"Unknown type {type}")
    return Expression(res)


def _comprehension(comp):
    """Convert comprehension to ast.comprehension."""
    if isinstance(comp, ast.comprehension):
        return comp
    elif isinstance(comp, Sequence):
        [target, iter, *ifs] = comp
        target = _ContextReplacer(ast.Store()).visit(to_ast(target))
        ifs = [to_ast(e) for e in ifs]
        return ast.comprehension(to_ast(target), to_ast(iter), ifs, is_async=False)
    elif isinstance(comp, Mapping):
        return ast.comprehension(**comp)
    else:
        raise TypeError("Not a comprehension")


class _ContextReplacer(ast.NodeTransformer):
    """Replace context of whole subtree."""
    def __init__(self, ctx):
        self.ctx = ctx

    def visit_Name(self, node):
        node.ctx = self.ctx
        return node

    def visit_Attribute(self, node):
        self.generic_visit(node)
        node.ctx = self.ctx
        return node


def fstr(*values):
    """Build an F-string."""
    output = []
    for value in values:
        match value:
            case str():
                output.append(to_ast(value))
            case ast.Constant(str()) | ast.FormattedValue():
                output.append(value)
            case _:
                output.append(fmt(value))

    return Expression(ast.JoinedStr(values=output))


def fmt(value, format_spec=None, conversion=-1):
    """Format a values using format_spec."""
    if format_spec is not None:
        format_spec = to_ast(format_spec)

        if not isinstance(format_spec, ast.JoinedStr):
            format_spec = ast.JoinedStr(values=[format_spec])

    return ast.FormattedValue(
        to_ast(value),
        conversion=conversion,
        format_spec=format_spec)


def lambda_(args: Iterable[Expression | ast.Name], body) -> Expression:
    """Generate a lambda expression."""
    if isinstance(args, Iterable):
        args = [ast.arg(arg=to_ast(arg).id) for arg in args]
        args = ast.arguments(posonlyargs=[], args=args, kwonlyargs=[], kw_defaults=[], defaults=[])
    elif not isinstance(args, ast.arguments):
        raise TypeError("args should be a sequence")
    node = ast.Lambda(args, to_ast(body))
    return Expression(node)


# Illegal unicode alias (not pep8-compliant, please don't tell anyone)
λ_ = lambda_
