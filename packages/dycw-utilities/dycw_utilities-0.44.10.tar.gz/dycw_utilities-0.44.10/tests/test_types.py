from __future__ import annotations

import datetime as dt
from pathlib import Path
from types import NoneType
from typing import Any, cast

from pytest import mark, param, raises

from utilities.datetime import get_now, get_today
from utilities.sentinel import sentinel
from utilities.types import (
    Duration,
    EnsureBoolError,
    EnsureClassError,
    EnsureDateError,
    EnsureDatetimeError,
    EnsureFloatError,
    EnsureHashableError,
    EnsureIntError,
    EnsureMemberError,
    EnsureNotNoneError,
    EnsureNumberError,
    EnsureSizedError,
    EnsureSizedNotStrError,
    EnsureTimeError,
    Number,
    PathLike,
    ensure_bool,
    ensure_class,
    ensure_date,
    ensure_datetime,
    ensure_float,
    ensure_hashable,
    ensure_int,
    ensure_member,
    ensure_not_none,
    ensure_number,
    ensure_sized,
    ensure_sized_not_str,
    ensure_time,
    get_class,
    get_class_name,
    if_not_none,
    is_hashable,
    is_sized,
    is_sized_not_str,
    issubclass_except_bool_int,
    make_isinstance,
)


class TestDuration:
    @mark.parametrize("x", [param(0), param(0.0), param(dt.timedelta(0))])
    def test_success(self, *, x: Duration) -> None:
        assert isinstance(x, Duration)

    def test_error(self) -> None:
        assert not isinstance("0", Duration)


class TestEnsureBool:
    @mark.parametrize(
        ("obj", "nullable"), [param(True, False), param(True, True), param(None, True)]
    )
    def test_main(self, *, obj: bool | None, nullable: bool) -> None:
        _ = ensure_bool(obj, nullable=nullable)

    @mark.parametrize(
        ("nullable", "match"),
        [
            param(False, "Object .* must be a boolean"),
            param(True, "Object .* must be a boolean or None"),
        ],
    )
    def test_error(self, *, nullable: bool, match: str) -> None:
        with raises(EnsureBoolError, match=f"{match}; got .* instead"):
            _ = ensure_bool(sentinel, nullable=nullable)


class TestEnsureClass:
    @mark.parametrize(
        ("obj", "cls", "nullable"),
        [
            param(True, bool, False),
            param(True, bool, True),
            param(True, (bool,), False),
            param(True, (bool,), True),
            param(None, bool, True),
        ],
    )
    def test_main(self, *, obj: Any, cls: Any, nullable: bool) -> None:
        _ = ensure_class(obj, cls, nullable=nullable)

    @mark.parametrize(
        ("nullable", "match"),
        [
            param(False, "Object .* must be an instance of .*"),
            param(True, "Object .* must be an instance of .* or None"),
        ],
    )
    def test_error(self, *, nullable: bool, match: str) -> None:
        with raises(EnsureClassError, match=f"{match}; got .* instead"):
            _ = ensure_class(sentinel, bool, nullable=nullable)


class TestEnsureDate:
    @mark.parametrize(
        ("obj", "nullable"),
        [param(get_today(), False), param(get_today(), True), param(None, True)],
    )
    def test_main(self, *, obj: dt.date | None, nullable: bool) -> None:
        _ = ensure_date(obj, nullable=nullable)

    @mark.parametrize(
        ("nullable", "match"),
        [
            param(False, "Object .* must be a date"),
            param(True, "Object .* must be a date or None"),
        ],
    )
    def test_error(self, *, nullable: bool, match: str) -> None:
        with raises(EnsureDateError, match=f"{match}; got .* instead"):
            _ = ensure_date(sentinel, nullable=nullable)


class TestEnsureDatetime:
    @mark.parametrize(
        ("obj", "nullable"),
        [param(get_now(), False), param(get_now(), True), param(None, True)],
    )
    def test_main(self, *, obj: dt.datetime | None, nullable: bool) -> None:
        _ = ensure_datetime(obj, nullable=nullable)

    @mark.parametrize(
        ("nullable", "match"),
        [
            param(False, "Object .* must be a datetime"),
            param(True, "Object .* must be a datetime or None"),
        ],
    )
    def test_error(self, *, nullable: bool, match: str) -> None:
        with raises(EnsureDatetimeError, match=f"{match}; got .* instead"):
            _ = ensure_datetime(sentinel, nullable=nullable)


class TestEnsureFloat:
    @mark.parametrize(
        ("obj", "nullable"), [param(0.0, False), param(0.0, True), param(None, True)]
    )
    def test_main(self, *, obj: float | None, nullable: bool) -> None:
        _ = ensure_float(obj, nullable=nullable)

    @mark.parametrize(
        ("nullable", "match"),
        [
            param(False, "Object .* must be a float"),
            param(True, "Object .* must be a float or None"),
        ],
    )
    def test_error(self, *, nullable: bool, match: str) -> None:
        with raises(EnsureFloatError, match=f"{match}; got .* instead"):
            _ = ensure_float(sentinel, nullable=nullable)


class TestEnsureHashable:
    @mark.parametrize("obj", [param(0), param((1, 2, 3))])
    def test_main(self, *, obj: Any) -> None:
        assert ensure_hashable(obj) == obj

    def test_error(self) -> None:
        with raises(EnsureHashableError, match=r"Object .* must be hashable\."):
            _ = ensure_hashable([1, 2, 3])


class TestEnsureInt:
    @mark.parametrize(
        ("obj", "nullable"), [param(0, False), param(0, True), param(None, True)]
    )
    def test_main(self, *, obj: int | None, nullable: bool) -> None:
        _ = ensure_int(obj, nullable=nullable)

    @mark.parametrize(
        ("nullable", "match"),
        [
            param(False, "Object .* must be an integer"),
            param(True, "Object .* must be an integer or None"),
        ],
    )
    def test_error(self, *, nullable: bool, match: str) -> None:
        with raises(EnsureIntError, match=f"{match}; got .* instead"):
            _ = ensure_int(sentinel, nullable=nullable)


class TestEnsureMember:
    @mark.parametrize(
        ("obj", "nullable"),
        [
            param(True, True),
            param(True, False),
            param(False, True),
            param(False, False),
            param(None, True),
        ],
    )
    def test_main(self, *, obj: Any, nullable: bool) -> None:
        _ = ensure_member(obj, {True, False}, nullable=nullable)

    @mark.parametrize(
        ("nullable", "match"),
        [
            param(False, "Object .* must be a member of .*"),
            param(True, "Object .* must be a member of .* or None"),
        ],
    )
    def test_error(self, *, nullable: bool, match: str) -> None:
        with raises(EnsureMemberError, match=match):
            _ = ensure_member(sentinel, {True, False}, nullable=nullable)


class TestEnsureNotNone:
    def test_main(self) -> None:
        maybe_int = cast(int | None, 0)
        result = ensure_not_none(maybe_int)
        assert result == 0

    def test_error(self) -> None:
        with raises(EnsureNotNoneError, match="Object .* must not be None"):
            _ = ensure_not_none(None)


class TestEnsureNumber:
    @mark.parametrize(
        ("obj", "nullable"),
        [param(0, False), param(0.0, False), param(0.0, True), param(None, True)],
    )
    def test_main(self, *, obj: Number, nullable: bool) -> None:
        _ = ensure_number(obj, nullable=nullable)

    @mark.parametrize(
        ("nullable", "match"),
        [
            param(False, "Object .* must be a number"),
            param(True, "Object .* must be a number or None"),
        ],
    )
    def test_error(self, *, nullable: bool, match: str) -> None:
        with raises(EnsureNumberError, match=f"{match}; got .* instead"):
            _ = ensure_number(sentinel, nullable=nullable)


class TestEnsureSized:
    @mark.parametrize("obj", [param([]), param(()), param("")])
    def test_main(self, *, obj: Any) -> None:
        _ = ensure_sized(obj)

    def test_error(self) -> None:
        with raises(EnsureSizedError, match=r"Object .* must be sized"):
            _ = ensure_sized(None)


class TestEnsureSizedNotStr:
    @mark.parametrize("obj", [param([]), param(())])
    def test_main(self, *, obj: Any) -> None:
        _ = ensure_sized_not_str(obj)

    @mark.parametrize("obj", [param(None), param("")])
    def test_error(self, *, obj: Any) -> None:
        with raises(
            EnsureSizedNotStrError, match="Object .* must be sized, but not a string"
        ):
            _ = ensure_sized_not_str(obj)


class TestEnsureTime:
    @mark.parametrize(
        ("obj", "nullable"),
        [
            param(get_now().time(), False),
            param(get_now().time(), True),
            param(None, True),
        ],
    )
    def test_main(self, *, obj: dt.time | None, nullable: bool) -> None:
        _ = ensure_time(obj, nullable=nullable)

    @mark.parametrize(
        ("nullable", "match"),
        [
            param(False, "Object .* must be a time"),
            param(True, "Object .* must be a time or None"),
        ],
    )
    def test_error(self, *, nullable: bool, match: str) -> None:
        with raises(EnsureTimeError, match=f"{match}; got .* instead"):
            _ = ensure_time(sentinel, nullable=nullable)


class TestGetClass:
    @mark.parametrize(
        ("obj", "expected"), [param(None, NoneType), param(NoneType, NoneType)]
    )
    def test_main(self, *, obj: Any, expected: type[Any]) -> None:
        assert get_class(obj) is expected


class TestGetClassName:
    def test_class(self) -> None:
        class Example: ...

        assert get_class_name(Example) == "Example"

    def test_instance(self) -> None:
        class Example: ...

        assert get_class_name(Example()) == "Example"


class TestIfNotNone:
    def test_uses_first(self) -> None:
        result = if_not_none(0, "0")
        assert result == 0

    def test_uses_second(self) -> None:
        result = if_not_none(None, 0)
        assert result == 0


class TestIsHashable:
    @mark.parametrize(
        ("obj", "expected"),
        [param(0, True), param((1, 2, 3), True), param([1, 2, 3], False)],
    )
    def test_main(self, *, obj: Any, expected: bool) -> None:
        assert is_hashable(obj) is expected


class TestIsSized:
    @mark.parametrize(
        ("obj", "expected"),
        [param(None, False), param([], True), param((), True), param("", True)],
    )
    def test_main(self, *, obj: Any, expected: bool) -> None:
        assert is_sized(obj) is expected


class TestIsSizedNotStr:
    @mark.parametrize(
        ("obj", "expected"),
        [param(None, False), param([], True), param((), True), param("", False)],
    )
    def test_main(self, *, obj: Any, expected: bool) -> None:
        assert is_sized_not_str(obj) is expected


class TestIsSubclassExceptBoolInt:
    @mark.parametrize(
        ("x", "y", "expected"),
        [param(bool, bool, True), param(bool, int, False), param(int, int, True)],
    )
    def test_main(self, *, x: type[Any], y: type[Any], expected: bool) -> None:
        assert issubclass_except_bool_int(x, y) is expected

    def test_subclass_of_int(self) -> None:
        class MyInt(int): ...

        assert not issubclass_except_bool_int(bool, MyInt)


class TestMakeIsInstance:
    @mark.parametrize(
        ("obj", "expected"), [param(True, True), param(False, True), param(None, False)]
    )
    def test_main(self, *, obj: bool | None, expected: bool) -> None:
        func = make_isinstance(bool)
        result = func(obj)
        assert result is expected


class TestNumber:
    @mark.parametrize("x", [param(0), param(0.0)])
    def test_ok(self, *, x: Number) -> None:
        assert isinstance(x, Number)

    def test_error(self) -> None:
        assert not isinstance(None, Number)


class TestPathLike:
    @mark.parametrize("path", [param(Path.home()), param("~")])
    def test_main(self, *, path: PathLike) -> None:
        assert isinstance(path, PathLike)

    def test_error(self) -> None:
        assert not isinstance(None, PathLike)
