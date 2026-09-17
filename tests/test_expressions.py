"""公式求值：导入、正例、边界、反例。"""

from __future__ import annotations

import pytest

from trpg_values_demo import __version__
from trpg_values_demo.expressions import ExpressionError, evaluate


def test_package_imports() -> None:
    assert __version__


def test_configured_modifier_formula() -> None:
    assert evaluate("(力量 - 10) // 2", {"力量": 16}) == 3
    assert evaluate("(力量 - 10) // 2", {"力量": 10}) == 0


def test_formula_can_reference_earlier_derived_value() -> None:
    scope: dict[str, object] = {"体质": 14}
    scope["体质修正"] = evaluate("(体质 - 10) // 2", scope)
    assert scope["体质修正"] == 2
    assert evaluate("10 + 体质修正 * 2", scope) == 14


def test_negative_rounding_follows_python_floor() -> None:
    # (9 - 10) // 2 == -1，而不是 0
    assert evaluate("(力量 - 10) // 2", {"力量": 9}) == -1


def test_conditionals_and_comparisons() -> None:
    assert evaluate("1 if 力量 >= 10 else -1", {"力量": 10}) == 1
    assert evaluate("1 if 力量 >= 10 else -1", {"力量": 9}) == -1


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os')",
        "(1).__class__",
        "力量.bit_length()",
        "[x for x in (1, 2)]",
        "力量[0]",
    ],
)
def test_rejects_unsafe_syntax(expression: str) -> None:
    with pytest.raises(ExpressionError):
        evaluate(expression, {"力量": 16})


def test_rejects_unknown_variable() -> None:
    with pytest.raises(ExpressionError):
        evaluate("(未知属性 - 10) // 2", {"力量": 16})


def test_rejects_division_by_zero() -> None:
    with pytest.raises(ExpressionError):
        evaluate("1 / 0", {})


def test_rejects_broken_syntax() -> None:
    with pytest.raises(ExpressionError):
        evaluate("(力量 - 10", {"力量": 16})
