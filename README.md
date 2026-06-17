# 数织 / Nonogram (Picross)

终端版数织 (逻辑画) — 根据每行/每列的提示数字, 还原黑白图案。  
A terminal nonogram / picross puzzle game.

## 特性 / Features

- 6 个内置图案: 5×5 (爱心、箭头、笑脸) 与 10×10 (小房子、圣诞树、小猫)
- 中英双语界面
- 行/列提示自动推导, 内置 line solver 提供智能提示 (h)
- 支持填充 (f) / 标记空格 (x) / 清除 (e)
- 悔棋 (u) / 验证错误数 (v) / 重置 (r)
- 终端铃声音效, 可关或调音量 (0~3)
- 持久化设置与排行榜 (Top 10, 保存于 `~/.nonogram_*.json`)

## 启动 / Run

需要 Python 3.8+, 不依赖任何第三方库:

```sh
python3 game.py
```

## 操作 / Commands

游戏主循环中:

| 命令 | 含义 |
|------|------|
| `f r c` 或 `f3,5` | 在 (r, c) 填充黑格 |
| `x r c` 或 `x3 5` | 在 (r, c) 标记为肯定空格 |
| `e r c` | 清除 (r, c) |
| `u` | 悔棋 |
| `h` | 提示 (寻找一个必然格) |
| `v` | 验证 (显示已填数 / 总数 / 错误数) |
| `r` | 重置 |
| `q` | 放弃本局 |

坐标从 0 开始, `r` 是行, `c` 是列。

## 测试 / Tests

```sh
python3 tests/run_tests.py
```

包含 88 个单元测试, 覆盖 board / solver / puzzles / 游戏循环 / 设置与排行榜 / 国际化 / 音效。

## 项目结构 / Layout

```
nonogram/
├── game.py        # 主菜单与回合循环
├── board.py       # 棋盘状态与提示推导
├── puzzles.py     # 内置图案
├── solver.py      # 行/列 line solver, 用于提示
├── score.py       # 排行榜
├── settings.py    # 设置持久化
├── sound.py       # 终端铃声
├── i18n.py        # 中英文字符串
└── tests/         # 单元测试
```
