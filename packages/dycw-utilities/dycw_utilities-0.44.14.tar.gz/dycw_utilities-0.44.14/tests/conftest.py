from __future__ import annotations

from os import environ
from typing import TYPE_CHECKING, Any

from pytest import fixture, mark

from utilities.platform import IS_NOT_LINUX

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy import Engine, Table

FLAKY = mark.flaky(reruns=5, reruns_delay=1)
SKIPIF_CI = mark.skipif("CI" in environ, reason="Skipped for CI")
SKIPIF_CI_AND_NOT_LINUX = mark.skipif(
    ("CI" in environ) and IS_NOT_LINUX, reason="Skipped for CI/non-Linux"
)


# hypothesis

try:
    from utilities.hypothesis import setup_hypothesis_profiles
except ModuleNotFoundError:
    pass
else:
    setup_hypothesis_profiles()


# sqlalchemy


try:
    pass
except ModuleNotFoundError:
    pass
else:

    @fixture(scope="session")
    def create_postgres_engine() -> Callable[..., Engine]:
        """Create a Postgres engine."""

        def inner(*tables_or_mapped_classes: Table | type[Any]) -> Engine:
            from utilities.sqlalchemy import (
                create_engine,
                ensure_tables_created,
                ensure_tables_dropped,
            )

            engine = create_engine(
                "postgresql", host="localhost", port=5432, database="testing"
            )
            ensure_tables_dropped(engine, *tables_or_mapped_classes)
            ensure_tables_created(engine, *tables_or_mapped_classes)
            return engine

        return inner
