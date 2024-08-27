import inspect

from .convert_code import to_ast, to_bytecode
from .builders import quote, λ_


class _FunctionFactory:
    """Helper to create functions.

    The parameters of this function can be single-letters.
    """
    def __call__(self, body):
        """Create a lambda without parameters.

        >>> hello_world = F("Hello World!")
        >>> hello_world()
        "Hello World!"
        """
        if cf := inspect.currentframe():
            # Closures only work in CPython
            pf = cf.f_back
            locals, globals = pf.f_locals, pf.f_globals
            del cf, pf
        else:
            locals, globals = {}, {}

        return eval(to_bytecode(λ_((), to_ast(body))), globals, locals)

    def __getattr__(self, item):
        """Create a lambda with single-letter parameters.
        >>> x, y = quote.x, quote.y
        >>> plus10 = F.x(x + 10)
        >>> plus10(5)
        15
        >>> multiply = F.xy(x * y)
        >>> multiply(5, 7)
        35
        """
        parameters = [quote(a) for a in item]

        if cf := inspect.currentframe():
            # Closures only work in CPython
            pf = cf.f_back
            locals, globals = pf.f_locals, pf.f_globals
            del cf, pf
        else:
            locals, globals = {}, {}

        def accept_body(body):
            """Call with an expression to register as a body."""
            return eval(to_bytecode(λ_(parameters, to_ast(body))), globals, locals)

        return accept_body


# λ is for naughty programmers. Use F for pep8-compliance.
F = λ = _FunctionFactory()
