import datetime as dt
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto, unique
from fractions import Fraction
from operator import eq
from typing import Any, Literal

from hypothesis import given
from hypothesis.strategies import (
    DataObject,
    SearchStrategy,
    binary,
    booleans,
    complex_numbers,
    data,
    dates,
    datetimes,
    decimals,
    dictionaries,
    floats,
    fractions,
    frozensets,
    integers,
    ip_addresses,
    lists,
    none,
    sampled_from,
    sets,
    text,
    times,
    tuples,
    uuids,
)
from pytest import mark, param, raises
from sqlalchemy import Engine

from utilities.hypothesis import (
    int64s,
    slices,
    sqlite_engines,
    temp_paths,
    text_ascii,
    timedeltas_2w,
    zoned_datetimes,
)
from utilities.math import MAX_INT64, MIN_INT64
from utilities.orjson import deserialize, serialize
from utilities.sentinel import sentinel
from utilities.typing import get_args
from utilities.zoneinfo import HONG_KONG, UTC

_TrueOrFalseLit = Literal["true", "false"]


def _filter_binary(obj: bytes, /) -> bool:
    try:
        _ = obj.decode()
    except UnicodeDecodeError:
        return False
    return True


def _filter_fraction(obj: Fraction, /) -> bool:
    return (MIN_INT64 <= obj.numerator <= MAX_INT64) and (
        MIN_INT64 <= obj.denominator <= MAX_INT64
    )


def _map_abs(obj: Any, /) -> Any:
    return abs(obj) if obj == 0.0 else obj


def _map_complex(obj: complex, /) -> complex:
    return complex(_map_abs(obj.real), _map_abs(obj.imag))


class TestSerializeAndDeserialize:
    @given(data=data())
    @mark.parametrize(
        ("elements", "two_way", "eq_obj_implies_eq_ser"),
        [
            param(binary().filter(_filter_binary), True, True),
            param(booleans(), True, True),
            param(
                complex_numbers(allow_infinity=False, allow_nan=False).map(
                    _map_complex
                ),
                True,
                True,
            ),
            param(dates(), True, True),
            param(datetimes(), True, True),
            param(
                zoned_datetimes(time_zone=sampled_from([HONG_KONG, UTC, dt.UTC])),
                True,
                True,
            ),
            param(
                decimals(allow_nan=False, allow_infinity=False).map(_map_abs),
                True,
                True,
            ),
            param(
                dictionaries(text_ascii(), int64s() | text_ascii(), max_size=3),
                True,
                True,
            ),
            param(
                dictionaries(int64s(), int64s() | text_ascii(), max_size=3), False, True
            ),
            param(
                floats(allow_nan=False, allow_infinity=False).map(_map_abs), True, True
            ),
            param(fractions().filter(_filter_fraction), True, True),
            param(frozensets(int64s(), max_size=3), True, True),
            param(frozensets(text_ascii(), max_size=3), True, True),
            param(frozensets(int64s() | text_ascii(), max_size=3), True, False),
            param(ip_addresses(v=4), True, True),
            param(ip_addresses(v=6), True, True),
            param(lists(int64s(), max_size=3), True, True),
            param(lists(lists(int64s(), max_size=3), max_size=3), True, True),
            param(none(), True, True),
            param(sets(int64s(), max_size=3), True, True),
            param(sets(text_ascii(), max_size=3), True, True),
            param(sets(int64s() | text_ascii(), max_size=3), True, False),
            param(slices(integers(0, 10)), True, True),
            param(temp_paths(), True, True),
            param(text(), True, True),
            param(timedeltas_2w(), True, True),
            param(times(), True, True),
            param(tuples(int64s(), int64s()), False, True),
            param(uuids(), False, True),
        ],
    )
    def test_main(
        self,
        *,
        data: DataObject,
        elements: SearchStrategy[Any],
        two_way: bool,
        eq_obj_implies_eq_ser: bool,
    ) -> None:
        self._run_tests(
            data, elements, two_way=two_way, eq_obj_implies_eq_ser=eq_obj_implies_eq_ser
        )

    @given(
        data=data(),
        date=dates(),
        int_=int64s(),
        local_datetime=datetimes(),
        text=text_ascii(),
        zoned_datetime=zoned_datetimes(
            time_zone=sampled_from([HONG_KONG, UTC, dt.UTC])
        ),
    )
    def test_dataclasses(
        self,
        *,
        data: DataObject,
        date: dt.date,
        int_: int,
        local_datetime: dt.datetime,
        text: str,
        zoned_datetime: dt.datetime,
    ) -> None:
        true_or_falses: tuple[_TrueOrFalseLit, ...] = get_args(_TrueOrFalseLit)
        true_or_false = data.draw(sampled_from(true_or_falses))

        @unique
        class Truth(Enum):
            true = auto()
            false = auto()

        truth = data.draw(sampled_from(Truth))

        @dataclass(kw_only=True)
        class Inner:
            date: dt.date
            enum: Truth
            int_: int
            literal: _TrueOrFalseLit
            local_datetime: dt.datetime
            text: str
            zoned_datetime: dt.datetime

        @dataclass(kw_only=True)
        class Outer:
            inner: Inner
            date: dt.date
            enum: Truth
            int_: int
            literal: _TrueOrFalseLit
            local_datetime: dt.datetime
            text: str
            zoned_datetime: dt.datetime

        obj = Outer(
            inner=Inner(
                date=date,
                enum=truth,
                int_=int_,
                literal=true_or_false,
                local_datetime=local_datetime,
                text=text,
                zoned_datetime=zoned_datetime,
            ),
            date=date,
            enum=truth,
            int_=int_,
            literal=true_or_false,
            local_datetime=local_datetime,
            text=text,
            zoned_datetime=zoned_datetime,
        )
        result = deserialize(serialize(obj), cls=Outer)
        assert result == obj

    @given(data=data())
    def test_engines(self, *, data: DataObject) -> None:
        def eq(x: Engine, y: Engine, /) -> bool:
            return x.url == y.url

        self._run_tests(
            data, sqlite_engines(), two_way=True, eq=eq, eq_obj_implies_eq_ser=True
        )

    def test_error(self) -> None:
        with raises(TypeError, match="Type is not JSON serializable: Sentinel"):
            _ = serialize(sentinel)

    def _run_tests(
        self,
        data: DataObject,
        elements: SearchStrategy[Any],
        /,
        *,
        two_way: bool = False,
        eq: Callable[[Any, Any], bool] = eq,
        eq_obj_implies_eq_ser: bool = False,
    ) -> None:
        x = data.draw(elements)
        ser_x = serialize(x)
        if two_way:
            deser_x = deserialize(ser_x)
            assert eq(deser_x, x)
        y = data.draw(elements)
        ser_y = serialize(y)
        if eq(x, y):
            if eq_obj_implies_eq_ser:
                assert ser_x == ser_y
        else:
            assert ser_x != ser_y
