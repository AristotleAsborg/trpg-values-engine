"""规则配置：外部公式解析与派生计算。

落盘同样只发生在仓库内的 .scratch/ 下。
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from trpg_values_demo.character import Character
from trpg_values_demo.expressions import ExpressionError
from trpg_values_demo.rules import Ruleset, RulesetError

SCRATCH = Path(__file__).resolve().parent.parent / ".scratch"


@pytest.fixture()
def scratch():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        yield SCRATCH
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)


def _ruleset() -> Ruleset:
    return Ruleset.from_dict(
        {
            "name": "测试规则",
            "derived": {
                "力量修正": "(力量 - 10) // 2",
                "体质修正": "(体质 - 10) // 2",
                "HP": "10 + 体质修正 * 2",
                "MP": "5 + 力量修正",
            },
        }
    )


def test_derive_matches_configured_formulas() -> None:
    card = Character(name="张三", abilities={"力量": 16, "体质": 14}, skills={})
    derived = _ruleset().derive(card)
    assert derived["力量修正"] == 3
    assert derived["体质修正"] == 2
    assert derived["HP"] == 14
    assert derived["MP"] == 8


def test_derive_can_read_skill_values() -> None:
    ruleset = Ruleset.from_dict(
        {"name": "技能规则", "derived": {"侦查判定": "侦查 + (智力 - 10) // 2"}}
    )
    card = Character(name="李四", abilities={"智力": 14}, skills={"侦查": 5})
    assert ruleset.derive(card)["侦查判定"] == 7


def test_ruleset_loads_from_external_file(scratch: Path) -> None:
    path = scratch / "rules.json"
    path.write_text(
        json.dumps(
            {"name": "外部规则", "derived": {"修正值": "(力量 - 10) // 2"}},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    ruleset = Ruleset.load(path)
    assert ruleset.name == "外部规则"

    card = Character(name="王五", abilities={"力量": 8}, skills={})
    assert ruleset.derive(card)["修正值"] == -1


def test_rejects_missing_derived_section() -> None:
    with pytest.raises(RulesetError):
        Ruleset.from_dict({"name": "坏配置"})

    with pytest.raises(RulesetError):
        Ruleset.from_dict({"name": "坏配置", "derived": {"x": "   "}})


def test_bad_formula_surfaces_as_ruleset_error() -> None:
    ruleset = Ruleset.from_dict({"name": "坏公式", "derived": {"修正值": "(未知 - 10) // 2"}})
    with pytest.raises(RulesetError):
        ruleset.derive(Character(name="x", abilities={}, skills={}))


def test_expression_error_is_a_value_error() -> None:
    assert issubclass(ExpressionError, ValueError)
