from __future__ import annotations

import datetime as dt
import enum
from enum import auto
from re import search
from typing import TYPE_CHECKING, Any

import sqlalchemy
from click import ParamType, argument, command, echo, option
from click.testing import CliRunner
from hypothesis import given
from hypothesis.strategies import (
    DataObject,
    SearchStrategy,
    data,
    dates,
    datetimes,
    integers,
    just,
    lists,
    sampled_from,
    times,
)
from pytest import mark, param

import utilities.click
import utilities.datetime
import utilities.types
from utilities.click import (
    Date,
    DirPath,
    ExistingDirPath,
    ExistingFilePath,
    FilePath,
    ListDates,
    ListEnums,
    ListInts,
    ListMonths,
    ListStrs,
    LocalDateTime,
    Time,
    Timedelta,
    ZonedDateTime,
)
from utilities.datetime import serialize_month
from utilities.hypothesis import (
    durations,
    months,
    sqlite_engines,
    text_ascii,
    timedeltas_2w,
)
from utilities.sqlalchemy import serialize_engine
from utilities.text import join_strs
from utilities.whenever import (
    serialize_date,
    serialize_duration,
    serialize_local_datetime,
    serialize_time,
    serialize_timedelta,
    serialize_zoned_datetime,
)
from utilities.zoneinfo import UTC

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence
    from pathlib import Path


class _Truth(enum.Enum):
    true = auto()
    false = auto()


class TestEnum:
    def test_repr(self) -> None:
        param = utilities.click.Enum(_Truth)
        expected = f"Enum({_Truth})"
        assert repr(param) == expected

    @given(data=data(), truth=sampled_from(_Truth))
    def test_case_insensitive(self, *, data: DataObject, truth: _Truth) -> None:
        @command()
        @argument("truth", type=utilities.click.Enum(_Truth))
        def cli(*, truth: _Truth) -> None:
            echo(f"truth = {truth}")

        name = truth.name
        as_str = data.draw(sampled_from([name, name.lower()]))
        result = CliRunner().invoke(cli, [as_str])
        assert result.exit_code == 0
        assert result.stdout == f"truth = {truth}\n"

    @given(truth=sampled_from(_Truth))
    def test_case_sensitive(self, *, truth: _Truth) -> None:
        @command()
        @argument("truth", type=utilities.click.Enum(_Truth, case_sensitive=True))
        def cli(*, truth: _Truth) -> None:
            echo(f"truth = {truth}")

        result = CliRunner().invoke(cli, [truth.name])
        assert result.exit_code == 0
        assert result.stdout == f"truth = {truth}\n"

        result = CliRunner().invoke(cli, ["invalid"])
        assert result.exit_code == 2

    @given(truth=sampled_from(_Truth))
    def test_option(self, *, truth: _Truth) -> None:
        @command()
        @option("--truth", type=utilities.click.Enum(_Truth), default=truth)
        def cli(*, truth: _Truth) -> None:
            echo(f"truth = {truth}")

        result = CliRunner().invoke(cli)
        assert result.exit_code == 0
        assert result.stdout == f"truth = {truth}\n"


class TestFileAndDirPaths:
    def test_existing_dir_path(self, *, tmp_path: Path) -> None:
        @command()
        @argument("path", type=ExistingDirPath)
        def cli(*, path: Path) -> None:
            from pathlib import Path

            assert isinstance(path, Path)

        result = CliRunner().invoke(cli, [str(tmp_path)])
        assert result.exit_code == 0

        file_path = tmp_path.joinpath("file.txt")
        file_path.touch()
        result = CliRunner().invoke(cli, [str(file_path)])
        assert result.exit_code == 2
        assert search("is a file", result.stdout)

        non_existent = tmp_path.joinpath("non-existent")
        result = CliRunner().invoke(cli, [str(non_existent)])
        assert result.exit_code == 2
        assert search("does not exist", result.stdout)

    def test_existing_file_path(self, *, tmp_path: Path) -> None:
        @command()
        @argument("path", type=ExistingFilePath)
        def cli(*, path: Path) -> None:
            from pathlib import Path

            assert isinstance(path, Path)

        result = CliRunner().invoke(cli, [str(tmp_path)])
        assert result.exit_code == 2
        assert search("is a directory", result.stdout)

        file_path = tmp_path.joinpath("file.txt")
        file_path.touch()
        result = CliRunner().invoke(cli, [str(file_path)])
        assert result.exit_code == 0

        non_existent = tmp_path.joinpath("non-existent")
        result = CliRunner().invoke(cli, [str(non_existent)])
        assert result.exit_code == 2
        assert search("does not exist", result.stdout)

    def test_dir_path(self, *, tmp_path: Path) -> None:
        @command()
        @argument("path", type=DirPath)
        def cli(*, path: Path) -> None:
            from pathlib import Path

            assert isinstance(path, Path)

        result = CliRunner().invoke(cli, [str(tmp_path)])
        assert result.exit_code == 0

        file_path = tmp_path.joinpath("file.txt")
        file_path.touch()
        result = CliRunner().invoke(cli, [str(file_path)])
        assert result.exit_code == 2
        assert search("is a file", result.stdout)

        non_existent = tmp_path.joinpath("non-existent")
        result = CliRunner().invoke(cli, [str(non_existent)])
        assert result.exit_code == 0

    def test_file_path(self, *, tmp_path: Path) -> None:
        @command()
        @argument("path", type=FilePath)
        def cli(*, path: Path) -> None:
            from pathlib import Path

            assert isinstance(path, Path)

        result = CliRunner().invoke(cli, [str(tmp_path)])
        assert result.exit_code == 2
        assert search("is a directory", result.stdout)

        file_path = tmp_path.joinpath("file.txt")
        file_path.touch()
        result = CliRunner().invoke(cli, [str(file_path)])
        assert result.exit_code == 0

        non_existent = tmp_path.joinpath("non-existent")
        result = CliRunner().invoke(cli, [str(non_existent)])
        assert result.exit_code == 0


def _serialize_iterable_enums(values: Iterable[enum.Enum], /) -> str:
    return join_strs(e.name for e in values)


class TestListEnums:
    def test_repr(self) -> None:
        param = ListEnums(_Truth)
        expected = "ListEnum(true,false)"
        assert repr(param) == expected

    @given(values=lists(sampled_from(_Truth), min_size=1, unique=True))
    def test_command(self, *, values: Sequence[_Truth]) -> None:
        @command()
        @argument("values", type=ListEnums(_Truth))
        def cli(*, values: Sequence[_Truth]) -> None:
            echo(f"values = {values}")

        joined = _serialize_iterable_enums(values)
        result = CliRunner().invoke(cli, [joined])
        assert result.exit_code == 0
        assert result.stdout == f"values = {values}\n"

        result = CliRunner().invoke(cli, ["invalid"])
        assert result.exit_code == 2

    @given(values=lists(sampled_from(_Truth), min_size=1, unique=True))
    def test_option(self, *, values: list[str]) -> None:
        @command()
        @option("--values", type=ListEnums(_Truth), default=values)
        def cli(*, values: Sequence[str]) -> None:
            echo(f"values = {values}")

        result = CliRunner().invoke(cli)
        assert result.exit_code == 0
        assert result.stdout == f"values = {values}\n"


def _serialize_iterable_dates(values: Iterable[dt.date], /) -> str:
    return join_strs(map(serialize_date, values))


def _serialize_iterable_ints(values: Iterable[int], /) -> str:
    return join_strs(map(str, values))


def _serialize_iterable_months(values: Iterable[utilities.datetime.Month], /) -> str:
    return join_strs(map(serialize_month, values))


def _serialize_iterable_strs(values: Iterable[str], /) -> str:
    return join_strs(values)


class TestParameters:
    cases = (
        param(Date(), dt.date, dates(), serialize_date, True),
        param(
            utilities.click.Duration(),
            utilities.types.Duration,
            durations(min_number=0, min_timedelta=dt.timedelta(0), two_way=True),
            serialize_duration,
            True,
        ),
        param(
            utilities.click.Engine(),
            sqlalchemy.Engine,
            sqlite_engines(),
            serialize_engine,
            True,
        ),
        param(
            ListDates(), list[dt.date], lists(dates()), _serialize_iterable_dates, True
        ),
        param(
            ListInts(),
            list[int],
            lists(integers(0, 10)),
            _serialize_iterable_ints,
            True,
        ),
        param(
            ListMonths(),
            list[utilities.datetime.Month],
            lists(months()),
            _serialize_iterable_months,
            True,
        ),
        param(
            ListStrs(),
            list[str],
            lists(text_ascii(), min_size=5),
            _serialize_iterable_strs,
            False,
        ),
        param(
            LocalDateTime(), dt.datetime, datetimes(), serialize_local_datetime, True
        ),
        param(
            utilities.click.Month(),
            utilities.datetime.Month,
            months(),
            serialize_month,
            True,
        ),
        param(Time(), dt.time, times(), serialize_time, True),
        param(
            Timedelta(),
            dt.timedelta,
            timedeltas_2w(min_value=dt.timedelta(0)),
            serialize_timedelta,
            True,
        ),
        param(
            ZonedDateTime(),
            dt.datetime,
            datetimes(timezones=just(UTC)),
            serialize_zoned_datetime,
            True,
        ),
    )

    @given(data=data())
    @mark.parametrize(("param", "cls", "strategy", "serialize", "failable"), cases)
    def test_argument(
        self,
        *,
        data: DataObject,
        param: ParamType,
        cls: Any,
        strategy: SearchStrategy[Any],
        serialize: Callable[[Any], str],
        failable: bool,
    ) -> None:
        runner = CliRunner()

        @command()
        @argument("value", type=param)
        def cli(*, value: cls) -> None:
            echo(f"value = {serialize(value)}")

        result = CliRunner().invoke(cli, ["--help"])
        assert result.exit_code == 0

        value_str = serialize(data.draw(strategy))
        result = CliRunner().invoke(cli, [value_str])
        assert result.exit_code == 0
        assert result.stdout == f"value = {value_str}\n"

        result = runner.invoke(cli, ["error"])
        expected = 2 if failable else 0
        assert result.exit_code == expected

    @given(data=data())
    @mark.parametrize(("param", "cls", "strategy", "serialize", "failable"), cases)
    def test_option(
        self,
        *,
        data: DataObject,
        param: ParamType,
        cls: Any,
        strategy: SearchStrategy[Any],
        serialize: Callable[[Any], str],
        failable: bool,
    ) -> None:
        value = data.draw(strategy)

        @command()
        @option("--value", type=param, default=value)
        def cli(*, value: cls) -> None:
            echo(f"value = {serialize(value)}")

        result = CliRunner().invoke(cli, ["--help"])
        assert result.exit_code == 0

        result = CliRunner().invoke(cli)
        assert result.exit_code == 0
        assert result.stdout == f"value = {serialize(value)}\n"

        _ = failable
