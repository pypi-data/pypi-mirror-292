from collections.abc import Callable, Mapping, Sequence
from inspect import signature
from operator import contains
from typing import Any

from plum import dispatch
from toolz import curry as crr
from toolz import keyfilter


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


@dispatch
def apply_packed_filtered(fnct: Callable, squn: Sequence) -> Any:
    return fnct(*squn[: len(signature(fnct).parameters)])


@dispatch
def apply_packed_filtered(fnct: Callable, tbl_assc: Mapping) -> Any:
    return fnct(**keyfilter(crr(contains)(signature(fnct).parameters.keys()), tbl_assc))


def packedpart(fnct: Callable) -> Callable:
    def fnct_packed(to_be_unpacked: Sequence | Mapping) -> Any:
        return apply_packed_filtered(fnct, to_be_unpacked)

    return fnct_packed


if __name__ == "__main__":

    def test_fnct_add(x: int, y: int) -> int:
        added = x + y
        print(f"{x} added to {y} produces {added}")
        return added

    data_args = [1, 2]
    data_kwargs = {"x": 1, "y": 2}
    assert apply_packed(test_fnct_add, data_args) == 3
    assert packed(test_fnct_add)(data_args) == 3
    assert apply_packed(test_fnct_add, data_kwargs) == 3
    assert packed(test_fnct_add)(data_kwargs) == 3

    data_args_excess = [1, 2, 3]
    data_kwargs_excess = {"x": 1, "y": 2, "z": 3}
    assert apply_packed_filtered(test_fnct_add, data_args_excess) == 3
    assert packedpart(test_fnct_add)(data_args_excess) == 3
    assert apply_packed_filtered(test_fnct_add, data_kwargs_excess) == 3
    assert packedpart(test_fnct_add)(data_kwargs_excess) == 3
