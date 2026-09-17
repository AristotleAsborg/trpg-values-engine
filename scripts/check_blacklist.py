#!/usr/bin/env python3
"""确认引擎源码里没有硬编码某个规则系统的数值。

规则系统的具体公式与属性名只应该出现在外部配置文件里。
``src/trpg_values_demo/`` 下如果出现下面这些字面量，就说明规则被写回脚本了。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "trpg_values_demo"

BLACKLIST = ("// 2", "力量", "敏捷", "体质", "智力")


def main() -> int:
    if not PACKAGE.is_dir():
        print(f"[blacklist] 找不到包目录: {PACKAGE}", file=sys.stderr)
        return 1

    hits: list[str] = []
    for path in sorted(PACKAGE.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in BLACKLIST:
                if pattern in line:
                    rel = path.relative_to(ROOT)
                    hits.append(f"{rel}:{lineno}: 命中 {pattern!r} -> {line.strip()}")

    if hits:
        print("[blacklist] 检测到被写死的规则内容，请移到外部配置文件：", file=sys.stderr)
        for hit in hits:
            print(f"  {hit}", file=sys.stderr)
        return 1

    print("[blacklist] OK：引擎源码中没有硬编码的规则系统内容")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
