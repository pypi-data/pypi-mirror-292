import functools
import operator
from typing import Iterable, TypeVar

_T = TypeVar("_T")


def flatten(the_list: Iterable[Iterable[_T]]) -> list[_T]:
    return functools.reduce(operator.iconcat, the_list, [])
