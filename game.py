"""Nonogram — main menu and round loop."""
import random
import sys
from typing import Optional, Tuple

import puzzles as puzzles_mod
import score as score_mod
import settings as settings_mod
import solver as solver_mod
from board import Board, EMPTY, FILLED, MARKED, IllegalMove
from i18n import t
from sound import Sound


class QuitGame(Exception):
    pass


_ACTION_ALIASES = {
    "f": "fill",
    "fill": "fill",
    "x": "mark",
    "mark": "mark",
    "e": "erase",
    "erase": "erase",
}


def parse_move(text: str) -> Optional[Tuple[str, int, int]]:
    """Parse a move command. Returns (action, row, col) or None.

    action ∈ {'fill', 'mark', 'erase'}
    Accepted forms:
      'f 3 5'   spaced
      'f3,5'    compact with comma
      'f3 5'    compact with space
      'mark 3 5'
    """
    if not text:
        return None
    s = text.strip().lower()
    if not s:
        return None
    # Find action prefix
    action = None
    rest = s
    for prefix in ("fill", "mark", "erase"):
        if s.startswith(prefix):
            action = prefix
            rest = s[len(prefix):]
            break
    if action is None and s[0] in _ACTION_ALIASES:
        action = _ACTION_ALIASES[s[0]]
        rest = s[1:]
    if action is None:
        return None
    # Now extract two digits from rest
    for ch in ",()":
        rest = rest.replace(ch, " ")
    tokens = rest.split()
    if not tokens or not all(tok.isdigit() for tok in tokens):
        return None
    if len(tokens) == 2:
        r, c = int(tokens[0]), int(tokens[1])
    elif len(tokens) == 1 and len(tokens[0]) == 2:
        r, c = int(tokens[0][0]), int(tokens[0][1])
    elif len(tokens) == 1 and len(tokens[0]) >= 2:
        # e.g. "fill 35" with two-digit row+col packed
        return None
    else:
        return None
    return (action, r, c)


def play_round(s: dict, sound: Sound, input_func, output, rng=None) -> Optional[dict]:
    if rng is None:
        rng = random.Random()
    lang = s.get("lang", "zh")
    size = int(s.get("size", 5))
    keys = puzzles_mod.puzzles_by_size(size)
    if not keys:
        keys = puzzles_mod.list_puzzles()
    puzzle_key = rng.choice(keys)
    puzzle = puzzles_mod.get_puzzle(puzzle_key)
    name = puzzle[f"name_{lang}"] if f"name_{lang}" in puzzle else puzzle["name_en"]
    board = Board(puzzle["solution"])
    moves = 0
    hints_used = 0

    def write(msg=""):
        output.write(msg + "\n")

    write(t(lang, "puzzle_label", name=name))

    while True:
        write(board.render_text())
        write(t(lang, "moves_label", moves=moves))

        if board.is_solved():
            write(t(lang, "solved", moves=moves))
            sound.win()
            score = score_mod.compute_score(size, moves, hints_used)
            write(t(lang, "score_label", score=score))
            return {
                "result": "solved",
                "puzzle": puzzle_key,
                "size": size,
                "moves": moves,
                "score": score,
            }

        try:
            line = input_func(t(lang, "input_move"))
        except EOFError:
            raise QuitGame()
        cmd = line.strip().lower()
        if cmd == "q":
            return None
        if cmd == "u":
            if not board.undo():
                write(t(lang, "nothing_undo"))
            else:
                moves += 1
            continue
        if cmd == "r":
            board.reset()
            moves = 0
            hints_used = 0
            write(t(lang, "reset_done"))
            continue
        if cmd == "v":
            write(t(lang, "verify_label",
                    filled=board.filled_count(),
                    total=board.total_filled_in_solution(),
                    errors=board.errors()))
            continue
        if cmd == "h":
            mv = solver_mod.find_hint(board)
            if mv is None:
                write(t(lang, "no_hint"))
            else:
                r, c, st = mv
                action_txt = t(lang, "hint_fill" if st == FILLED else "hint_mark")
                write(t(lang, "hint_label", r=r, c=c, action=action_txt))
                hints_used += 1
            continue
        parsed = parse_move(cmd)
        if parsed is None:
            write(t(lang, "bad_format"))
            continue
        action, r, c = parsed
        try:
            if action == "fill":
                board.fill(r, c)
                sound.fill()
            elif action == "mark":
                board.mark(r, c)
                sound.mark()
            else:
                board.erase(r, c)
        except IllegalMove:
            write(t(lang, "illegal"))
            sound.illegal()
            continue
        moves += 1


def show_help(s: dict, input_func, output) -> None:
    lang = s.get("lang", "zh")
    output.write("\n=== " + t(lang, "help_title") + " ===\n")
    output.write(t(lang, "help_body") + "\n")
    try:
        input_func(t(lang, "press_enter"))
    except EOFError:
        pass


def show_scores(s: dict, input_func, output) -> None:
    lang = s.get("lang", "zh")
    scores = score_mod.load()
    output.write("\n=== " + t(lang, "scores_title") + " ===\n")
    if not scores:
        output.write(t(lang, "scores_empty") + "\n")
    else:
        for i, e in enumerate(scores, 1):
            output.write(t(
                lang, "scores_row",
                rank=i, name=e.get("name", "")[:12],
                score=e.get("score", 0),
                puzzle=e.get("puzzle", ""),
                moves=e.get("moves", 0),
            ) + "\n")
    try:
        input_func(t(lang, "press_enter"))
    except EOFError:
        pass


def settings_menu(s: dict, input_func, output) -> dict:
    while True:
        lang = s.get("lang", "zh")
        output.write("\n=== " + t(lang, "settings_title") + " ===\n")
        output.write(t(lang, "settings_lang", value=t(lang, f"lang_{lang}")) + "\n")
        output.write(t(lang, "settings_sound",
                       value=t(lang, "on" if s.get("sound") else "off")) + "\n")
        output.write(t(lang, "settings_volume", value=s.get("volume", 1)) + "\n")
        output.write(t(lang, "settings_size", value=t(lang, f"size_{s.get('size', 5)}")) + "\n")
        output.write(t(lang, "settings_back") + "\n")
        try:
            choice = input_func(t(lang, "menu_choice")).strip().lower()
        except EOFError:
            break
        if choice == "1":
            settings_mod.cycle_lang(s)
        elif choice == "2":
            settings_mod.toggle_sound(s)
        elif choice == "3":
            settings_mod.cycle_volume(s)
        elif choice == "4":
            settings_mod.cycle_size(s)
        elif choice == "b":
            break
        else:
            output.write(t(lang, "unknown", choice=choice) + "\n")
    settings_mod.save(s)
    return s


def main_menu(input_func=None, output=None, rng=None) -> None:
    if input_func is None:
        input_func = input
    if output is None:
        output = sys.stdout
    if rng is None:
        rng = random.Random()
    s = settings_mod.load()
    settings_mod.save(s)
    while True:
        lang = s.get("lang", "zh")
        output.write("\n=== " + t(lang, "title") + " ===\n")
        output.write(t(lang, "menu_play") + "\n")
        output.write(t(lang, "menu_help") + "\n")
        output.write(t(lang, "menu_scores") + "\n")
        output.write(t(lang, "menu_settings") + "\n")
        output.write(t(lang, "menu_quit") + "\n")
        try:
            choice = input_func(t(lang, "menu_choice")).strip().lower()
        except EOFError:
            output.write(t(lang, "bye") + "\n")
            return
        if choice == "q":
            output.write(t(lang, "bye") + "\n")
            return
        if choice == "p":
            sound = Sound(enabled=bool(s.get("sound", True)),
                          volume=int(s.get("volume", 1)),
                          output=output)
            try:
                result = play_round(s, sound, input_func, output, rng=rng)
            except QuitGame:
                output.write(t(lang, "bye") + "\n")
                return
            if result is None:
                continue
            try:
                name = input_func(t(lang, "name_prompt")).strip()
            except EOFError:
                name = ""
            if name:
                score_mod.add(name, result["score"], result["puzzle"], result["moves"])
        elif choice == "h":
            show_help(s, input_func, output)
        elif choice == "l":
            show_scores(s, input_func, output)
        elif choice == "s":
            settings_menu(s, input_func, output)
        else:
            output.write(t(lang, "unknown", choice=choice) + "\n")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print()
