"""命令行入口：加载规则与角色卡，算派生值，做一次判定，并写回角色卡。"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from .character import Character
from .dice import resolve_check
from .rules import Ruleset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trpg-values-demo",
        description="通用 TRPG 数值引擎：外部配置驱动的派生计算与骰点判定",
    )
    parser.add_argument("--rules", required=True, help="规则配置文件（JSON）")
    parser.add_argument("--card", required=True, help="角色卡文件（JSON，不存在则新建）")
    parser.add_argument("--dice", default="1d20", help="判定用骰点记法，默认 1d20")
    parser.add_argument("--target", type=int, default=15, help="判定目标值，默认 15")
    parser.add_argument("--modifier", default="", help="用作加值的派生值名称（如 DEX修正）")
    parser.add_argument("--seed", type=int, default=None, help="随机种子，便于复现")
    return parser


def _default_character() -> Character:
    """首次运行时使用的起始角色卡。具体数值来自外部规则文件的使用者约定。"""
    return Character(
        name="示例角色",
        abilities={"STR": 16, "DEX": 12, "CON": 14, "INT": 10},
        skills={"perception": 3, "stealth": 1},
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ruleset = Ruleset.load(args.rules)

    card_path = Path(args.card)
    if card_path.exists():
        character = Character.load(card_path)
        print(f"[load] 读回已有角色卡 {character.name}（{card_path}）")
    else:
        character = _default_character()
        character.save(card_path)
        print(f"[new ] 新建角色卡 {character.name}（已写入 {card_path}）")

    derived = ruleset.derive(character)
    print(f"[rule] {ruleset.name}")
    for key, value in derived.items():
        print(f"       {key} = {value}")

    modifier: int | float = 0
    if args.modifier:
        if args.modifier in derived:
            modifier = derived[args.modifier]
        else:
            print(f"[warn] 派生值里没有 {args.modifier!r}，加值按 0 处理")

    rng = random.Random(args.seed) if args.seed is not None else None
    result = resolve_check(args.dice, modifier=modifier, target=args.target, rng=rng)
    verdict = "成功" if result.success else "失败"
    print(
        f"[roll] {args.dice} -> {list(result.rolls)} "
        f"(+{modifier}) 合计 {result.total} vs 目标 {result.target} => {verdict}"
    )
    return 0
