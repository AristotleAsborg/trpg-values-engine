"""角色卡：属性 / 技能等基础数值，以及 JSON 存盘与读回。

派生值（修正值、HP/MP……）不写死在角色卡里，而是由 :class:`Ruleset`
按外部配置的公式算出来。存盘只保存基础数值，因此换规则系统后
同一张角色卡能原样复用。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

__all__ = ["Character", "CharacterError"]


class CharacterError(ValueError):
    """角色卡数据非法。"""


def _int_map(value: Any, field_name: str) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise CharacterError(f"{field_name} 必须是一个对象")

    result: dict[str, int] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise CharacterError(f"{field_name} 的键必须是非空字符串")
        if isinstance(item, bool) or not isinstance(item, int):
            raise CharacterError(f"{field_name}.{key} 必须是整数")
        result[key] = item
    return result


@dataclass
class Character:
    """一张角色卡的基础状态。"""

    name: str
    abilities: dict[str, int] = field(default_factory=dict)
    skills: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": 1,
            "name": self.name,
            "abilities": dict(self.abilities),
            "skills": dict(self.skills),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Character":
        if not isinstance(data, Mapping):
            raise CharacterError("角色卡内容必须是一个对象")

        name = data.get("name")
        if not isinstance(name, str) or not name:
            raise CharacterError("角色卡缺少合法的 name")

        return cls(
            name=name,
            abilities=_int_map(data.get("abilities"), "abilities"),
            skills=_int_map(data.get("skills"), "skills"),
        )

    def save(self, path: str | Path) -> Path:
        """把角色卡写成 JSON 文件，返回实际写入的路径。"""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
        target.write_text(payload + "\n", encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: str | Path) -> "Character":
        """从 JSON 文件读回角色卡，便于下一次运行接着用同一张卡。"""
        source = Path(path)
        try:
            raw = source.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(f"角色卡不存在: {source}") from None

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CharacterError(f"角色卡不是合法 JSON: {source}: {exc}") from exc

        return cls.from_dict(data)
