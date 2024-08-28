from collections.abc import Callable, Mapping, Sequence
from typing import Any

from plum import dispatch


@dispatch
def apply_packed(fnct: Callable, squn: Sequence) -> Any:
    return fnct(*squn)


@dispatch
def apply_packed(fnct: Callable, tbl_assc: Mapping) -> Any:
    return fnct(**tbl_assc)


def packed(fnct: Callable) -> Callable:
    def fnct_packed(to_be_unpacked: Sequence | Mapping) -> Any:
        return apply_packed(fnct, to_be_unpacked)

    return fnct_packed


if __name__ == "__main__":

    data_args = [1, 2]
    data_kwargs = {"x": 1, "y": 2}

    def f(x: int, y: int) -> int:
        added = x + y
        print(f"{x} added to {y} produces {added}")
        return added

    assert f(*data_args) == 3
    assert f(**data_kwargs) == 3

    assert packed(f)(data_args) == 3
    assert packed(f)(data_kwargs) == 3

    assert apply_packed(f, data_args) == 3
    assert apply_packed(f, data_kwargs) == 3
