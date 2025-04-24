import functools
from typing import *

P = ParamSpec("P")


def foo(a: int, b: str, c: float = 2.0) -> float:
    return a + int(b) + c


def verify_positive(fn: Callable[P, float]) -> Callable[P, float]:

    @functools.wraps(fn)
    def _verify_positive(*args: P.args, **kwargs: P.kwargs) -> float:

        res = fn(*args, **kwargs)
        if res < 0:
            print(f"Warning! Negative number {res}!")
        return res

    return _verify_positive


bar = verify_positive(foo)

baz = bar(1, "-5", 1.5)  # Ok
bazoo = bar(1, "-8")
print(baz, bazoo)
