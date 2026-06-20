"""Bilingual strings."""

STRINGS = {
    "zh": {
        "title": "数织 / Nonogram",
        "menu_play": "p) 开始游戏",
        "menu_help": "h) 帮助",
        "menu_scores": "l) 排行榜",
        "menu_settings": "s) 设置",
        "menu_quit": "q) 退出",
        "menu_choice": "请选择 > ",
        "bye": "再见!",
        "unknown": "未知选项: {choice}",
        "help_title": "帮助",
        "help_body": (
            "数织(逻辑画): 根据每行/每列的提示数字, 还原黑白图案。\n"
            "数字表示该行/列从左到右(或上到下)连续填充格的长度,\n"
            "多个连续段之间至少要隔 1 个空格。\n"
            "操作:\n"
            "  f r c   填充 (r, c) 单元格\n"
            "  x r c   标记 (r, c) 为肯定空格\n"
            "  e r c   清除 (r, c)\n"
            "也可写为 'f3,5' / 'x3 5' 等形式。\n"
            "命令: u=悔棋  h=提示  v=验证(显示错误数)  r=重置  q=放弃\n"
        ),
        "press_enter": "按回车继续...",
        "settings_title": "设置",
        "settings_lang": "1) 语言: {value}",
        "settings_sound": "2) 声音: {value}",
        "settings_volume": "3) 音量: {value}",
        "settings_size": "4) 难度(尺寸): {value}",
        "settings_back": "b) 返回",
        "scores_title": "排行榜 (Top 10)",
        "scores_empty": "暂无成绩",
        "scores_row": "{rank:>2}. {name:<12} {score:>5}  ({puzzle}, {moves}步)",
        "name_prompt": "姓名(空= 不保存): ",
        "puzzle_label": "图案: {name}",
        "moves_label": "步数: {moves}",
        "input_move": "操作 > ",
        "bad_format": "格式不正确, 请使用 'f r c' 'x r c' 'e r c'",
        "illegal": "无效操作",
        "out_of_bounds": "坐标超出范围: ({row}, {col})",
        "nothing_undo": "无可悔棋",
        "reset_done": "已重置",
        "verify_label": "已填: {filled} / {total}, 错误: {errors}",
        "hint_label": "提示: ({r},{c}) {action}",
        "hint_fill": "填充",
        "hint_mark": "标记空格",
        "no_hint": "未找到必然格",
        "solved": "完成! 共 {moves} 步",
        "score_label": "得分: {score}",
        "result_solved": "完成",
        "result_quit": "放弃",
        "size_5": "5x5",
        "size_10": "10x10",
        "lang_zh": "中文",
        "lang_en": "英文",
        "on": "开",
        "off": "关",
    },
    "en": {
        "title": "Nonogram (Picross)",
        "menu_play": "p) Play",
        "menu_help": "h) Help",
        "menu_scores": "l) Leaderboard",
        "menu_settings": "s) Settings",
        "menu_quit": "q) Quit",
        "menu_choice": "Choose > ",
        "bye": "Bye!",
        "unknown": "Unknown option: {choice}",
        "help_title": "Help",
        "help_body": (
            "Nonogram: paint cells using the row & column clues.\n"
            "Each clue lists the lengths of consecutive filled-cell runs;\n"
            "runs are separated by at least one empty cell.\n"
            "Commands:\n"
            "  f r c   fill cell at (r, c)\n"
            "  x r c   mark (r, c) as definitely empty\n"
            "  e r c   erase mark / fill at (r, c)\n"
            "Also accepts 'f3,5' / 'x3 5' style. Coordinates are zero-based.\n"
            "  u=undo  h=hint  v=verify (show error count)  r=reset  q=quit\n"
        ),
        "press_enter": "Press Enter to continue...",
        "settings_title": "Settings",
        "settings_lang": "1) Language: {value}",
        "settings_sound": "2) Sound: {value}",
        "settings_volume": "3) Volume: {value}",
        "settings_size": "4) Difficulty (size): {value}",
        "settings_back": "b) Back",
        "scores_title": "Leaderboard (Top 10)",
        "scores_empty": "No scores yet",
        "scores_row": "{rank:>2}. {name:<12} {score:>5}  ({puzzle}, {moves} moves)",
        "name_prompt": "Name (empty = skip save): ",
        "puzzle_label": "Puzzle: {name}",
        "moves_label": "Moves: {moves}",
        "input_move": "Move > ",
        "bad_format": "Bad format. Use 'f r c', 'x r c', 'e r c'",
        "illegal": "Invalid move",
        "out_of_bounds": "Coordinates out of bounds: ({row}, {col})",
        "nothing_undo": "Nothing to undo",
        "reset_done": "Reset",
        "verify_label": "Filled {filled}/{total}, errors: {errors}",
        "hint_label": "Hint: ({r},{c}) {action}",
        "hint_fill": "fill",
        "hint_mark": "mark empty",
        "no_hint": "No forced cell found",
        "solved": "Solved in {moves} moves!",
        "score_label": "Score: {score}",
        "result_solved": "solved",
        "result_quit": "quit",
        "size_5": "5x5",
        "size_10": "10x10",
        "lang_zh": "Chinese",
        "lang_en": "English",
        "on": "on",
        "off": "off",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    table = STRINGS.get(lang) or STRINGS["en"]
    s = table.get(key)
    if s is None:
        s = STRINGS["en"].get(key, key)
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s
