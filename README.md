# trpg-values-demo

一个**通用 TRPG 数值引擎**的最小可运行骨架：

- **骰点判定**：投骰 + 加值 vs 目标值 → 成功 / 失败（支持 `1d20`、`2d6+3` 记法）。
- **角色数值派生**：属性 → 修正值、HP/MP 等，全部由**外部 JSON 配置**里的公式算出。
- **角色卡存档**：状态存成 JSON 文件，下一次运行读回同一张卡继续用。
- **规则不写死**：换规则系统只换配置文件，脚本代码一行都不用改。

## 安装

```bash
python -m pip install -e ".[dev]"
```

需要 Python 3.10+。运行期零第三方依赖（配置用 JSON，避免 TOML 在 3.10 上的兼容问题）。

## 跑测试

```bash
python -m pytest -q
python -m ruff check .
python scripts/check_blacklist.py
```

## 试用

第一次运行：`--card` 指向的文件不存在，脚本新建角色卡并写盘。

```bash
python -m trpg_values_demo \
  --rules rules/example_rules.json \
  --card .scratch/card.json \
  --modifier DEX修正 --target 12 --seed 7
```

第二次运行：把 `--card` 指向同一个路径，脚本读回刚才那张卡接着算。

```bash
python -m trpg_values_demo \
  --rules rules/example_rules.json \
  --card .scratch/card.json \
  --modifier DEX修正 --target 12 --seed 7
```

第一次输出里的 `[new ]` 会变成第二次的 `[load]`，说明用的是同一张角色卡。

## 规则配置

`rules/example_rules.json`（片段）：

```json
{
  "name": "示例规则（D20 风格）",
  "derived": {
    "STR修正": "(STR - 10) // 2",
    "CON修正": "(CON - 10) // 2",
    "HP": "10 + CON修正 * 2",
    "MP": "5 + INT修正"
  }
}
```

- `derived` 是一个**有序**映射：按书写顺序求值，后面的公式可以直接引用前面已经算出的派生值。
- 公式支持 `+ - * / // %`、比较运算、`and/or/not`、三元表达式，以及引用属性名 / 技能名 / 已算出的派生值。
- 函数调用、属性访问、下标、导入一律被拒绝——配置文件不能用来执行任意代码。

## 目录结构

```
src/trpg_values_demo/
  expressions.py   # 基于 AST 白名单的安全公式求值
  rules.py         # 读外部规则配置 + 派生计算
  dice.py          # 投骰与判定
  character.py     # 角色卡与 JSON 存盘 / 读回
  cli.py           # 命令行入口
rules/example_rules.json      # 外部规则配置示例
scripts/check_blacklist.py    # 防止规则被写死回引擎源码
 tests/                        # pytest 用例（不依赖系统临时目录）
```
