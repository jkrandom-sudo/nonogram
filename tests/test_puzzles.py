import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import puzzles as puzzles_mod
from board import Board, FILLED


class TestPuzzles(unittest.TestCase):
    def test_list_puzzles_nonempty(self):
        keys = puzzles_mod.list_puzzles()
        self.assertGreater(len(keys), 0)

    def test_get_puzzle_unknown(self):
        with self.assertRaises(KeyError):
            puzzles_mod.get_puzzle("does_not_exist")

    def test_each_puzzle_well_formed(self):
        for key in puzzles_mod.list_puzzles():
            p = puzzles_mod.get_puzzle(key)
            self.assertIn("name_zh", p)
            self.assertIn("name_en", p)
            self.assertIn("size", p)
            self.assertIn("solution", p)
            sol = p["solution"]
            size = p["size"]
            self.assertEqual(len(sol), size, msg=f"{key} rows")
            for row in sol:
                self.assertEqual(len(row), size, msg=f"{key} cols")
                for v in row:
                    self.assertIn(v, (0, 1))

    def test_each_puzzle_has_filled_cells(self):
        for key in puzzles_mod.list_puzzles():
            sol = puzzles_mod.get_puzzle(key)["solution"]
            count = sum(1 for row in sol for v in row if v == FILLED)
            self.assertGreater(count, 0)

    def test_puzzles_by_size(self):
        small = puzzles_mod.puzzles_by_size(5)
        large = puzzles_mod.puzzles_by_size(10)
        self.assertGreater(len(small), 0)
        self.assertGreater(len(large), 0)
        # No overlap
        self.assertEqual(set(small) & set(large), set())

    def test_board_can_be_built_for_each(self):
        for key in puzzles_mod.list_puzzles():
            sol = puzzles_mod.get_puzzle(key)["solution"]
            b = Board(sol)
            self.assertEqual(b.rows, len(sol))


if __name__ == "__main__":
    unittest.main()
