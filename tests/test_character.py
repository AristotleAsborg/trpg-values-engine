"""角色卡存盘与读回（验收条件：下一次运行接着用同一张卡）。

所有落盘都发生在仓库内的 .scratch/ 下，用例结束就删掉，
不触碰系统临时目录。
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import trpg_values_demo
from trpg_values_demo.character import Character, CharacterError

SCRATCH = Path(__file__).resolve().parent.parent / ".scratch"


@pytest.fixture()
def scratch():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        yield SCRATCH
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)


def _make_card() -> Character:
    return Character(
        name="张三",
        abilities={"力量": 16, "敏捷": 12, "体质": 14},
        skills={"侦查": 3},
    )


def test_package_exposes_character() -> None:
    assert trpg_values_demo.Character is Character


def test_save_then_load_roundtrip(scratch: Path) -> None:
    card_path = scratch / "card.json"
    card = _make_card()
    card.save(card_path)
    assert card_path.exists()

    reloaded = Character.load(card_path)
    assert reloaded.to_dict() == card.to_dict()
    assert reloaded.name == "张三"
    assert reloaded.abilities["力量"] == 16
    assert reloaded.skills == {"侦查": 3}


def test_second_run_continues_the_same_card(scratch: Path) -> None:
    card_path = scratch / "card.json"
    Character(name="李四", abilities={"力量": 8}, skills={}).save(card_path)

    first_run = Character.load(card_path)
    first_run.abilities["力量"] += 2
    first_run.save(card_path)

    second_run = Character.load(card_path)
    assert second_run.name == "李四"
    assert second_run.abilities["力量"] == 10


def test_load_missing_file_raises(scratch: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Character.load(scratch / "nope.json")


def test_rejects_broken_payloads(scratch: Path) -> None:
    broken = scratch / "broken.json"
    broken.write_text("{ 这不是 JSON", encoding="utf-8")
    with pytest.raises(CharacterError):
        Character.load(broken)

    with pytest.raises(CharacterError):
        Character.from_dict({"name": "", "abilities": {}})

    with pytest.raises(CharacterError):
        Character.from_dict({"name": "x", "abilities": {"力量": "很多"}})
