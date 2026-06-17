import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from board import Board, EMPTY, FILLED, MARKED, IllegalMove, derive_clues, derive_row_clues, derive_col_clues


def grid(rows):
    return [[1 if ch == "#" else 0 for ch in row] for row in rows]


class TestDeriveClues(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(derive_clues([0, 0, 0, 0]), [0])

    def test_single_run(self):
        self.assertEqual(derive_clues([1, 1, 1, 0, 0]), [3])

    def test_multiple_runs(self):
        self.assertEqual(derive_clues([1, 0, 1, 1, 0, 1]), [1, 2, 1])

    def test_full(self):
        self.assertEqual(derive_clues([1, 1, 1]), [3])

    def test_row_and_col_clues(self):
        sol = grid([
            "#.#",
            ".#.",
            "#.#",
        ])
        self.assertEqual(derive_row_clues(sol), [[1, 1], [1], [1, 1]])
        self.assertEqual(derive_col_clues(sol), [[1, 1], [1], [1, 1]])


class TestBoardBasics(unittest.TestCase):
    def setUp(self):
        self.sol = grid([
            ".#.",
            "###",
            ".#.",
        ])
        self.b = Board(self.sol)

    def test_dimensions(self):
        self.assertEqual(self.b.rows, 3)
        self.assertEqual(self.b.cols, 3)

    def test_initial_clues(self):
        self.assertEqual(self.b.row_clues, [[1], [3], [1]])
        self.assertEqual(self.b.col_clues, [[1], [3], [1]])

    def test_initial_grid_empty(self):
        for row in self.b.grid:
            for v in row:
                self.assertEqual(v, EMPTY)

    def test_fill_mark_erase(self):
        self.b.fill(0, 1)
        self.assertEqual(self.b.grid[0][1], FILLED)
        self.b.mark(0, 0)
        self.assertEqual(self.b.grid[0][0], MARKED)
        self.b.erase(0, 1)
        self.assertEqual(self.b.grid[0][1], EMPTY)

    def test_fill_out_of_bounds(self):
        with self.assertRaises(IllegalMove):
            self.b.fill(5, 5)
        with self.assertRaises(IllegalMove):
            self.b.fill(-1, 0)

    def test_invalid_solution_rejected(self):
        with self.assertRaises(ValueError):
            Board([])
        with self.assertRaises(ValueError):
            Board([[1, 0], [1]])
        with self.assertRaises(ValueError):
            Board([[1, 2]])  # 2 not allowed in solution

    def test_undo(self):
        self.b.fill(0, 1)
        self.b.fill(1, 1)
        self.assertTrue(self.b.undo())
        self.assertEqual(self.b.grid[1][1], EMPTY)
        self.assertEqual(self.b.grid[0][1], FILLED)
        self.assertTrue(self.b.undo())
        self.assertFalse(self.b.undo())

    def test_no_op_set_doesnt_record(self):
        self.b.set_cell(0, 0, EMPTY)
        self.assertFalse(self.b.history)

    def test_toggle_fill(self):
        self.b.toggle_fill(0, 1)
        self.assertEqual(self.b.grid[0][1], FILLED)
        self.b.toggle_fill(0, 1)
        self.assertEqual(self.b.grid[0][1], EMPTY)
        # toggle_fill from MARKED -> FILLED
        self.b.mark(0, 2)
        self.b.toggle_fill(0, 2)
        self.assertEqual(self.b.grid[0][2], FILLED)

    def test_toggle_mark(self):
        self.b.toggle_mark(0, 0)
        self.assertEqual(self.b.grid[0][0], MARKED)
        self.b.toggle_mark(0, 0)
        self.assertEqual(self.b.grid[0][0], EMPTY)


class TestBoardSolved(unittest.TestCase):
    def setUp(self):
        self.sol = grid([
            ".#.",
            "###",
            ".#.",
        ])
        self.b = Board(self.sol)

    def test_unsolved_initially(self):
        self.assertFalse(self.b.is_solved())

    def test_solved_when_filled_correctly(self):
        for r in range(3):
            for c in range(3):
                if self.sol[r][c] == FILLED:
                    self.b.fill(r, c)
        self.assertTrue(self.b.is_solved())

    def test_marks_dont_break_solve(self):
        # Fill all required + mark all empty cells
        for r in range(3):
            for c in range(3):
                if self.sol[r][c] == FILLED:
                    self.b.fill(r, c)
                else:
                    self.b.mark(r, c)
        self.assertTrue(self.b.is_solved())

    def test_extra_fill_breaks_solve(self):
        for r in range(3):
            for c in range(3):
                if self.sol[r][c] == FILLED:
                    self.b.fill(r, c)
        self.b.fill(0, 0)
        self.assertFalse(self.b.is_solved())
        self.assertEqual(self.b.errors(), 1)

    def test_filled_count_and_total(self):
        self.assertEqual(self.b.filled_count(), 0)
        self.assertEqual(self.b.total_filled_in_solution(), 5)
        self.b.fill(0, 1)
        self.assertEqual(self.b.filled_count(), 1)

    def test_reset(self):
        self.b.fill(0, 1)
        self.b.mark(0, 0)
        self.b.reset()
        self.assertEqual(self.b.filled_count(), 0)
        self.assertEqual(self.b.history, [])


class TestRender(unittest.TestCase):
    def test_render_contains_clues_and_cells(self):
        b = Board(grid([
            ".#.",
            "###",
            ".#.",
        ]))
        text = b.render_text()
        self.assertIn("·", text)
        b.fill(1, 1)
        text2 = b.render_text()
        self.assertIn("●", text2)
        b.mark(0, 0)
        text3 = b.render_text()
        self.assertIn("✗", text3)


if __name__ == "__main__":
    unittest.main()
