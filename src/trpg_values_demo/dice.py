"""投骰与判定。

骰点记法为 ``NdM``（例如 ``1d20``、``2d6``），可带一个常量加值（``2d6+3``）。
判定把「骰点 + 记法加值 + 角色加值」与目标值比较，**大于等于**目标值算成功。
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass

__all__ = ["CheckResult", "DiceError", "parse_notation", "resolve_check", "roll"]

_NOTATION = re.compile(r"^\s*(\d*)\s*[dD]\s*(\d+)\s*([+-]\s*\d+)?\s*$")


class DiceError(ValueError):
    """骰点记法非法。"""


def parse_notation(notation: str) -> tuple[int, int, int]:
    """把 ``2d6+3`` 解析成 ``(骰子个数, 骰面数, 常量加值)``。"""
    match = _NOTATION.match(notation or "")
    if match is None:
        raise DiceError(f"无法解析骰点记法: {notation!r}（应形如 1d20 或 2d6+3）")

    count_text, faces_text, bonus_text = match.groups()
    count = int(count_text) if count_text else 1
    faces = int(faces_text)
    bonus = int(bonus_text.replace(" ", "")) if bonus_text else 0

    if count < 1:
        raise DiceError(f"骰子个数必须 >= 1: {notation!r}")
    if faces < 2:
        raise DiceError(f"骰面数必须 >= 2: {notation!r}")
    return count, faces, bonus


def _roll_dice(notation: str, rng: random.Random | None) -> tuple[tuple[int, ...], int]:
    count, faces, bonus = parse_notation(notation)
    source = rng if rng is not None else random
    rolls = tuple(source.randint(1, faces) for _ in range(count))
    return rolls, bonus


def roll(notation: str, rng: random.Random | None = None) -> int:
    """按记法投骰，返回总点数（含记法里写的常量加值）。"""
    rolls, bonus = _roll_dice(notation, rng)
    return sum(rolls) + bonus


@dataclass(frozen=True)
class CheckResult:
    """一次判定的结果。"""

    rolls: tuple[int, ...]
    bonus: int
    modifier: int
    target: int

    @property
    def total(self) -> int:
        return sum(self.rolls) + self.bonus + self.modifier

    @property
    def success(self) -> bool:
        return self.total >= self.target

    @property
    def margin(self) -> int:
        return self.total - self.target


def resolve_check(
    notation: str,
    modifier: int = 0,
    target: int = 0,
    rng: random.Random | None = None,
) -> CheckResult:
    """投骰并生成判定结果（``modifier`` 通常来自角色数值的派生值）。"""
    rolls, bonus = _roll_dice(notation, rng)
    return CheckResult(rolls=rolls, bonus=bonus, modifier=modifier, target=target)
