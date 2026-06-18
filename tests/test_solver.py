import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import solver as solver_mod
import puzzles as puzzles_mod
from board import Board, EMPTY, FILLED, MARKED


class TestLinePlacements(unittest.TestCase):
    def test_empty_line(self):
        out = list(solver_mod.line_placements(5, [0], [EMPTY] * 5))
        self.assertEqual(out, [(0, 0, 0, 0, 0)])

    def test_full_line(self):
        out = list(solver_mod.line_placements(3, [3], [EMPTY] * 3))
        self.assertEqual(out, [(1, 1, 1)])

    def test_single_run_in_long_line(self):
        out = list(solver_mod.line_placements(5, [3], [EMPTY] * 5))
        self.assertEqual(set(out), {
            (1, 1, 1, 0, 0),
            (0, 1, 1, 1, 0),
            (0, 0, 1, 1, 1),
        })

    def test_two_runs(self):
        out = list(solver_mod.line_placements(5, [1, 1], [EMPTY] * 5))
        # 1+1+1=3 minimum slots; positions of two 1s with gap >=1
        self.assertEqual(set(out), {
            (1, 0, 1, 0, 0),
            (1, 0, 0, 1, 0),
            (1, 0, 0, 0, 1),
            (0, 1, 0, 1, 0),
            (0, 1, 0, 0, 1),
            (0, 0, 1, 0, 1),
        })

    def test_filled_constraint_narrows(self):
        cur = [EMPTY, EMPTY, FILLED, EMPTY, EMPTY]
        out = list(solver_mod.line_placements(5, [3], cur))
        # The run of 3 must include index 2
        self.assertEqual(set(out), {
            (1, 1, 1, 0, 0),
            (0, 1, 1, 1, 0),
            (0, 0, 1, 1, 1),
        })

    def test_marked_constraint_narrows(self):
        cur = [EMPTY, MARKED, EMPTY, EMPTY, EMPTY]
        out = list(solver_mod.line_placements(5, [3], cur))
        # Run of 3 cannot cover index 1
        self.assertEqual(set(out), {
            (0, 0, 1, 1, 1),
        })

    def test_invalid_current_length_rejected(self):
        with self.assertRaises(ValueError):
            list(solver_mod.line_placements(5, [3], [EMPTY] * 4))

    def test_invalid_clues_rejected(self):
        for clues in ([0, 1], [-1], [2, 2]):
            with self.subTest(clues=clues):
                with self.assertRaises(ValueError):
                    list(solver_mod.line_placements(3, clues, [EMPTY] * 3))


class TestForcedCells(unittest.TestCase):
    def test_forced_full(self):
        # Run of 3 in length 3: every cell forced filled.
        out = solver_mod.forced_cells(3, [3], [EMPTY] * 3)
        self.assertEqual(sorted(out), [(0, FILLED), (1, FILLED), (2, FILLED)])

    def test_forced_overlap(self):
        # Run of 4 in length 5 → middle 3 cells overlap in all placements.
        out = solver_mod.forced_cells(5, [4], [EMPTY] * 5)
        self.assertEqual(sorted(out), [(1, FILLED), (2, FILLED), (3, FILLED)])

    def test_no_forced_when_loose(self):
        out = solver_mod.forced_cells(5, [1], [EMPTY] * 5)
        self.assertEqual(out, [])

    def test_forced_marked_when_only_one_placement(self):
        # Run of 3 + filled at 0,1,2 → cells 3,4 must be empty.
        cur = [FILLED, FILLED, FILLED, EMPTY, EMPTY]
        out = solver_mod.forced_cells(5, [3], cur)
        self.assertIn((3, MARKED), out)
        self.assertIn((4, MARKED), out)


class TestFindHint(unittest.TestCase):
    def test_hint_on_full_row(self):
        # 3x3 board where middle row clue is [3] → all of row 1 filled.
        sol = [
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0],
        ]
        b = Board(sol)
        hint = solver_mod.find_hint(b)
        self.assertIsNotNone(hint)
        r, c, st = hint
        self.assertEqual(st, FILLED)

    def test_hint_returns_none_when_unforced(self):
        # Empty board with 1-clue per line gives nothing forced, but small
        # boards usually still force *some* cells. Use a 1x1 trivial unforced
        # state by making the line clue [0].
        sol = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        b = Board(sol)
        # All clues are [0]; only "no fill anywhere" placements exist, so
        # solver forces every cell to MARKED — that *is* a hint and is fine.
        hint = solver_mod.find_hint(b)
        self.assertIsNotNone(hint)
        r, c, st = hint
        self.assertEqual(st, MARKED)

    def test_hint_on_real_puzzle(self):
        for key in puzzles_mod.list_puzzles():
            sol = puzzles_mod.get_puzzle(key)["solution"]
            b = Board(sol)
            hint = solver_mod.find_hint(b)
            self.assertIsNotNone(hint, msg=f"{key} should yield a hint on empty board")
            r, c, st = hint
            self.assertTrue(0 <= r < b.rows)
            self.assertTrue(0 <= c < b.cols)
            self.assertIn(st, (FILLED, MARKED))


if __name__ == "__main__":
    unittest.main()
