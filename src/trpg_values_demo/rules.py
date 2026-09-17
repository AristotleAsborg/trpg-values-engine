"""从外部配置文件读取规则，并按公式派生角色数值。

配置文件是 JSON，结构如下::

    {
      "name": "我的规则系统",
      "derived": {
        "第一项": "(输入一 - 10) / 2",
        "第二项": "10 + 第一项 * 2"
      }
    }

``derived`` 是一个有序映射：按书写顺序求值，后面的公式可以直接引用
前面已经算出的派生值。换规则系统时只换这个文件，脚本本身不用改。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .character import Character
from .expressions import ExpressionError, evaluate

__all__ = ["Ruleset", "RulesetError"]


class RulesetError(ValueError):
    """规则配置非法，或者派生过程失败。"""


@dataclass(frozen=True)
class Ruleset:
    """一份外部规则配置：名字 + 派生公式表。"""

    name: str
    derived: dict[str, str]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Ruleset":
        if not isinstance(data, Mapping):
            raise RulesetError("规则配置必须是一个对象")

        name = data.get("name", "unnamed")
        if not isinstance(name, str) or not name:
            raise RulesetError("规则配置的 name 必须是非空字符串")

        raw_derived = data.get("derived")
        if not isinstance(raw_derived, Mapping) or not raw_derived:
            raise RulesetError("规则配置缺少非空的 derived 段")

        derived: dict[str, str] = {}
        for key, expression in raw_derived.items():
            if not isinstance(key, str) or not key:
                raise RulesetError("derived 的键必须是非空字符串")
            if not isinstance(expression, str) or not expression.strip():
                raise RulesetError(f"derived.{key} 必须是非空公式字符串")
            derived[key] = expression

        return cls(name=name, derived=derived)

    @classmethod
    def load(cls, path: str | Path) -> "Ruleset":
        source = Path(path)
        try:
            raw = source.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(f"规则配置文件不存在: {source}") from None

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RulesetError(f"规则配置文件不是合法 JSON: {source}: {exc}") from exc

        return cls.from_dict(data)

    def derive(self, character: Character) -> dict[str, Any]:
        """按配置里的公式算出全部派生值。

        可见变量依次是：角色卡的属性、技能，以及前面已经算出的派生值。
        """
        scope: dict[str, Any] = dict(character.abilities)
        scope.update(character.skills)

        result: dict[str, Any] = {}
        for key, expression in self.derived.items():
            try:
                value = evaluate(expression, scope)
            except ExpressionError as exc:
                raise RulesetError(f"派生值 {key!r} 的公式求值失败: {exc}") from exc
            result[key] = value
            scope[key] = value
        return result
