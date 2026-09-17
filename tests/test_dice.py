"""投骰与判定：正例、边界、反例。"""

from __future__ import annotations

import random

import pytest

from trpg_values_demo.dice import (
    CheckResult,
    DiceError,
    parse_notation,
    resolve_check,
    roll,
)


def test_parse_notation() -> None:
    assert parse_notation("2d6+3") == (2, 6, 3)
    assert parse_notation("d20") == (1, 20, 0)
    assert parse_notation(" 1d8 + 2 ") == (1, 8, 2)


def test_roll_stays_within_bounds_and_varies() -> None:
    rng = random.Random(20240501)
    values = [roll("2d6", rng=rng) for _ in range(300)]
    assert all(2 <= value <= 12 for value in values)
    assert len(set(values)) > 1


def test_check_success_and_failure() -> None:
    rng = random.Random(7)

    always_hit = resolve_check("1d20", modifier=100, target=10, rng=rng)
    assert always_hit.success
    assert always_hit.margin > 0

    always_miss = resolve_check("1d20", modifier=-100, target=10, rng=rng)
    assert not always_miss.success
    assert always_miss.margin < 0


def test_tie_on_target_counts_as_success() -> None:
    result = CheckResult(rolls=(9,), bonus=1, modifier=0, target=10)
    assert result.total == 10
    assert result.success
    assert result.margin == 0


def test_rejects_bad_notation() -> None:
    with pytest.raises(DiceError):
        parse_notation("d")
    with pytest.raises(DiceError):
        parse_notation("1d1")
    with pytest.raises(DiceError):
        parse_notation("0d6")
    with pytest.raises(DiceError):
        roll("not-a-dice")
