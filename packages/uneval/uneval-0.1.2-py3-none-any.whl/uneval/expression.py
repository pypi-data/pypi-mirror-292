import ast
import operator
from typing import TypeVar

from .convert_code import to_ast

TExpression = TypeVar("TExpression", bound="Expression")


class Expression:
    # _node can be retrieved by as_ast(expression) or by match/case
    __slots__ = ("_node",)
    __match_args__ = ("_node",)

    """Represents a python expression."""
    def __init__(self, expr: ast.AST):
        if isinstance(expr, ast.AST):
            self._node = expr
        elif isinstance(expr, Expression):
            self._node = expr._node
        elif isinstance(expr, str):
            self._node = ast.parse(expr, mode='eval').body
        else:
            raise TypeError("String or AST expected")

    def _unop(op, node_cls):
        def unary(self) -> TExpression:
            node = self._node
            return Expression(ast.UnaryOp(node_cls(), node))
        unary.__name__ = "__" + op.__name__ + "__"
        unary.__doc__ = f"""Generate a new expression applying {op.__name__}"""
        return unary

    def _binop(op, node_cls):
        def forward(self, other) -> TExpression:
            try:
                left, right = self._node, to_ast(other)
            except TypeError:
                return NotImplemented
            else:
                return Expression(ast.BinOp(left, node_cls(), right))

        forward.__name__ = "__" + op.__name__ + "__"
        forward.__doc__ = f"""Generate a new expression applying {op.__name__}"""

        def backward(self, other) -> TExpression:
            try:
                left, right = self._node, to_ast(other)
            except TypeError:
                return NotImplemented
            else:
                return Expression(ast.BinOp(right, node_cls(), left))

        backward.__name__ = "__" + op.__name__ + "__"
        backward.__doc__ = f"""Generate a new expression applying {op.__name__}"""

        return forward, backward

    def _compare(op, node_cls):
        def compare(self, other) -> TExpression:
            try:
                left, right = self._node, to_ast(other)
            except TypeError:
                return NotImplemented
            else:
                return Expression(ast.Compare(left, [node_cls()], [right]))

        compare.__name__ = "__" + op.__name__ + "__"
        compare.__doc__ = f"""Generate a new expression applying {op.__name__}"""
        return compare

    __pos__ = _unop(operator.pos, ast.UAdd)
    __neg__ = _unop(operator.neg, ast.USub)
    __invert__ = _unop(operator.invert, ast.Invert)
    __add__, __radd__ = _binop(operator.add, ast.Add)
    __sub__, __rsub__ = _binop(operator.sub, ast.Sub)
    __mul__, __rmul__ = _binop(operator.mul, ast.Mult)
    __or__, __ror__ = _binop(operator.or_, ast.BitOr)
    __and__, __rand__ = _binop(operator.and_, ast.BitAnd)
    __xor__, __rxor__ = _binop(operator.xor, ast.BitXor)
    __floordiv__, __rfloordiv__ = _binop(operator.floordiv, ast.FloorDiv)
    __truediv__, __rtruediv__ = _binop(operator.truediv, ast.Div)
    __mod__, __rmod__ = _binop(operator.mod, ast.Mod)
    __pow__, __rpow__ = _binop(operator.pow, ast.Pow)
    __matmul__, __rmatmul__ = _binop(operator.matmul, ast.MatMult)
    __lshift__, __rlshift__ = _binop(operator.lshift, ast.LShift)
    __rshift__, __rrshift__ = _binop(operator.rshift, ast.RShift)
    __ge__ = _compare(operator.ge, ast.GtE)
    __gt__ = _compare(operator.gt, ast.Gt)
    __lt__ = _compare(operator.lt, ast.Lt)
    __le__ = _compare(operator.le, ast.LtE)
    __eq__ = _compare(operator.eq, ast.Eq)
    __ne__ = _compare(operator.ne, ast.NotEq)

    def __getattr__(self, item) -> TExpression:
        if item.startswith('_') and item.endswith('_'):
            # Protocol not supported. Use quote.generic(exp) instead of generic(exp)
            msg = f"{item} not supported on {type(self).__name__}"
            raise AttributeError(msg, name=item, obj=self)
        node = ast.Attribute(self._node, item, ctx=ast.Load())
        return Expression(node)

    # Iteration is not useful. Use quote.iter(exp) instead.
    __iter__ = None

    def __getitem__(self, item) -> TExpression:
        node = ast.Subscript(self._node, to_ast(item), ctx=ast.Load())
        return Expression(node)

    def __call__(self, *args, **kwargs) -> TExpression:
        ast_args = [to_ast(arg) for arg in args]
        ast_kwargs = [
            ast.keyword(arg=to_ast(k), value=to_ast(v))
            for k, v in kwargs.items()
        ]
        node = ast.Call(self._node, args=ast_args, keywords=ast_kwargs)
        return Expression(node)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}: {self}>"

    def __str__(self) -> str:
        return ast.unparse(self._node)


# Declared here to avoid circular import
@to_ast.register
def _(exp: Expression) -> ast.AST:
    return exp._node
