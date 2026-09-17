"""通用 TRPG 数值引擎。

提供三件事：

* :mod:`trpg_values_demo.expressions` —— 对外部配置里写的公式做安全求值；
* :mod:`trpg_values_demo.rules` —— 读外部规则配置并派生角色数值；
* :mod:`trpg_values_demo.dice` —— 投骰与判定；
* :mod:`trpg_values_demo.character` —— 角色卡状态与存盘 / 读回。

任何具体规则系统的数值规则都不在这里，而是放在外部配置文件里。
"""

from .character import Character, CharacterError
from .dice import CheckResult, DiceError, parse_notation, resolve_check, roll
from .expressions import ExpressionError, evaluate
from .rules import Ruleset, RulesetError

__version__ = "0.1.0"

__all__ = [
    "Character",
    "CharacterError",
    "CheckResult",
    "DiceError",
    "ExpressionError",
    "Ruleset",
    "RulesetError",
    "__version__",
    "evaluate",
    "parse_notation",
    "resolve_check",
    "roll",
]
