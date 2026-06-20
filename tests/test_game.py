import io
import os
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import game as game_mod
import score as score_mod
import settings as settings_mod
from board import Board, FILLED
from sound import Sound


def grid(rows):
    return [[1 if ch == "#" else 0 for ch in row] for row in rows]


SIMPLE_SOL = grid([
    "#.",
    ".#",
])


HINT_SOL = grid([
    "###",
    "...",
    "###",
])


class StackedInput:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0

    def __call__(self, prompt=""):
        if self.calls >= len(self.replies):
            raise EOFError()
        reply = self.replies[self.calls]
        self.calls += 1
        return reply


class TestParseMove(unittest.TestCase):
    def test_spaced_form(self):
        self.assertEqual(game_mod.parse_move("f 3 5"), ("fill", 3, 5))

    def test_compact_comma(self):
        self.assertEqual(game_mod.parse_move("f3,5"), ("fill", 3, 5))

    def test_compact_space(self):
        self.assertEqual(game_mod.parse_move("f3 5"), ("fill", 3, 5))

    def test_mark_alias(self):
        self.assertEqual(game_mod.parse_move("x 1 2"), ("mark", 1, 2))
        self.assertEqual(game_mod.parse_move("mark 1 2"), ("mark", 1, 2))

    def test_erase_alias(self):
        self.assertEqual(game_mod.parse_move("e 0 0"), ("erase", 0, 0))
        self.assertEqual(game_mod.parse_move("erase 0 0"), ("erase", 0, 0))

    def test_two_digit_compact(self):
        self.assertEqual(game_mod.parse_move("f12"), ("fill", 1, 2))

    def test_invalid_returns_none(self):
        self.assertIsNone(game_mod.parse_move(""))
        self.assertIsNone(game_mod.parse_move("zzz"))
        self.assertIsNone(game_mod.parse_move("f"))
        self.assertIsNone(game_mod.parse_move("f a b"))

    def test_paren_form(self):
        self.assertEqual(game_mod.parse_move("f(1,2)"), ("fill", 1, 2))


class TestPlayRound(unittest.TestCase):
    def _setup(self, replies):
        out = io.StringIO()
        sound = Sound(enabled=False, output=out)
        # Use a deterministic puzzle by stubbing puzzles_by_size to return a single key
        # whose puzzle is our SIMPLE_SOL.
        return out, sound, StackedInput(replies)

    def test_solve_via_fill(self):
        out, sound, inp = self._setup(["f 0 0", "f 1 1"])
        with mock.patch.object(game_mod.puzzles_mod, "puzzles_by_size",
                               return_value=["test_puzzle"]):
            with mock.patch.object(game_mod.puzzles_mod, "get_puzzle",
                                   return_value={"name_zh": "测试", "name_en": "Test",
                                                  "size": 2, "solution": SIMPLE_SOL}):
                result = game_mod.play_round({"lang": "en", "size": 2}, sound,
                                             inp, out, rng=random.Random(0))
        self.assertIsNotNone(result)
        self.assertEqual(result["result"], "solved")
        self.assertEqual(result["moves"], 2)

    def test_quit(self):
        out, sound, inp = self._setup(["q"])
        with mock.patch.object(game_mod.puzzles_mod, "puzzles_by_size",
                               return_value=["test_puzzle"]):
            with mock.patch.object(game_mod.puzzles_mod, "get_puzzle",
                                   return_value={"name_zh": "测试", "name_en": "Test",
                                                  "size": 2, "solution": SIMPLE_SOL}):
                result = game_mod.play_round({"lang": "en", "size": 2}, sound,
                                             inp, out, rng=random.Random(0))
        self.assertIsNone(result)

    def test_undo(self):
        out, sound, inp = self._setup(["f 0 0", "u", "q"])
        with mock.patch.object(game_mod.puzzles_mod, "puzzles_by_size",
                               return_value=["test_puzzle"]):
            with mock.patch.object(game_mod.puzzles_mod, "get_puzzle",
                                   return_value={"name_zh": "测试", "name_en": "Test",
                                                  "size": 2, "solution": SIMPLE_SOL}):
                result = game_mod.play_round({"lang": "en", "size": 2}, sound,
                                             inp, out, rng=random.Random(0))
        self.assertIsNone(result)

    def test_reset(self):
        out, sound, inp = self._setup(["f 0 0", "f 1 1", "r", "q"])
        # Note: after the second fill the puzzle is solved, so play_round
        # would return solved before reaching 'r'. Use only one fill.
        out, sound, inp = self._setup(["f 0 0", "r", "q"])
        with mock.patch.object(game_mod.puzzles_mod, "puzzles_by_size",
                               return_value=["test_puzzle"]):
            with mock.patch.object(game_mod.puzzles_mod, "get_puzzle",
                                   return_value={"name_zh": "测试", "name_en": "Test",
                                                  "size": 2, "solution": SIMPLE_SOL}):
                result = game_mod.play_round({"lang": "en", "size": 2}, sound,
                                             inp, out, rng=random.Random(0))
        self.assertIsNone(result)
        text = out.getvalue()
        self.assertIn("Reset", text)

    def test_verify(self):
        out, sound, inp = self._setup(["v", "q"])
        with mock.patch.object(game_mod.puzzles_mod, "puzzles_by_size",
                               return_value=["test_puzzle"]):
            with mock.patch.object(game_mod.puzzles_mod, "get_puzzle",
                                   return_value={"name_zh": "测试", "name_en": "Test",
                                                  "size": 2, "solution": SIMPLE_SOL}):
                game_mod.play_round({"lang": "en", "size": 2}, sound,
                                    inp, out, rng=random.Random(0))
        self.assertIn("Filled", out.getvalue())

    def test_hint(self):
        out, sound, inp = self._setup(["h", "q"])
        with mock.patch.object(game_mod.puzzles_mod, "puzzles_by_size",
                               return_value=["test_puzzle"]):
            with mock.patch.object(game_mod.puzzles_mod, "get_puzzle",
                                   return_value={"name_zh": "测试", "name_en": "Test",
                                                  "size": 3, "solution": HINT_SOL}):
                game_mod.play_round({"lang": "en", "size": 3}, sound,
                                    inp, out, rng=random.Random(0))
        self.assertIn("Hint", out.getvalue())

    def test_bad_format(self):
        out, sound, inp = self._setup(["asdf", "q"])
        with mock.patch.object(game_mod.puzzles_mod, "puzzles_by_size",
                               return_value=["test_puzzle"]):
            with mock.patch.object(game_mod.puzzles_mod, "get_puzzle",
                                   return_value={"name_zh": "测试", "name_en": "Test",
                                                  "size": 2, "solution": SIMPLE_SOL}):
                game_mod.play_round({"lang": "en", "size": 2}, sound,
                                    inp, out, rng=random.Random(0))
        self.assertIn("Bad format", out.getvalue())

    def test_illegal_move(self):
        out, sound, inp = self._setup(["f 9 9", "q"])
        with mock.patch.object(game_mod.puzzles_mod, "puzzles_by_size",
                               return_value=["test_puzzle"]):
            with mock.patch.object(game_mod.puzzles_mod, "get_puzzle",
                                   return_value={"name_zh": "测试", "name_en": "Test",
                                                  "size": 2, "solution": SIMPLE_SOL}):
                game_mod.play_round({"lang": "en", "size": 2}, sound,
                                    inp, out, rng=random.Random(0))
        self.assertIn("out of bounds", out.getvalue())


class TestMainMenu(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._settings_path = Path(self._tmp.name) / "settings.json"
        self._scores_path = Path(self._tmp.name) / "scores.json"
        self._settings_patch = mock.patch.object(settings_mod, "DEFAULT_PATH",
                                                 self._settings_path)
        self._scores_patch = mock.patch.object(score_mod, "DEFAULT_PATH",
                                               self._scores_path)
        self._settings_patch.start()
        self._scores_patch.start()

    def tearDown(self):
        self._settings_patch.stop()
        self._scores_patch.stop()
        self._tmp.cleanup()

    def test_quit(self):
        out = io.StringIO()
        inp = StackedInput(["q"])
        game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertIn("再见", out.getvalue())

    def test_help(self):
        out = io.StringIO()
        inp = StackedInput(["h", "", "q"])
        game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertIn("帮助", out.getvalue())

    def test_scores_empty(self):
        out = io.StringIO()
        inp = StackedInput(["l", "", "q"])
        game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertIn("暂无成绩", out.getvalue())

    def test_play_then_save(self):
        out = io.StringIO()
        inp = StackedInput(["p", "alice", "q"])
        fake_result = {
            "result": "solved",
            "puzzle": "test",
            "size": 2,
            "moves": 2,
            "score": 200,
        }
        with mock.patch.object(game_mod, "play_round", return_value=fake_result):
            game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        scores = score_mod.load()
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0]["name"], "alice")

    def test_play_then_skip_save(self):
        out = io.StringIO()
        inp = StackedInput(["p", "", "q"])
        fake_result = {
            "result": "solved",
            "puzzle": "test",
            "size": 2,
            "moves": 2,
            "score": 200,
        }
        with mock.patch.object(game_mod, "play_round", return_value=fake_result):
            game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertEqual(score_mod.load(), [])

    def test_play_quit_returns_none_no_save(self):
        out = io.StringIO()
        inp = StackedInput(["p", "q"])
        with mock.patch.object(game_mod, "play_round", return_value=None):
            game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertEqual(score_mod.load(), [])

    def test_settings_menu_back(self):
        out = io.StringIO()
        inp = StackedInput(["s", "1", "b", "q"])  # toggle lang then back, then quit
        game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        s = settings_mod.load()
        self.assertEqual(s["lang"], "en")  # toggled from default zh

    def test_unknown_choice(self):
        out = io.StringIO()
        inp = StackedInput(["zzz", "q"])
        game_mod.main_menu(input_func=inp, output=out, rng=random.Random(0))
        self.assertIn("未知选项", out.getvalue())


if __name__ == "__main__":
    unittest.main()
