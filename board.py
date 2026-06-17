"""Nonogram (数织 / Picross) board.

A nonogram puzzle gives **row and column clues** describing the lengths of
consecutive runs of filled cells. The player paints cells filled or marks
them as definitely-empty until the grid matches a unique solution.

Cell states:
  0 — unknown / empty
  1 — filled (●)
  2 — crossed-out / marked empty (✗)  — a player aid, ignored at win-check.

A win is reached when every cell that is "filled" in the solution is set
to state 1 by the player. State 2 marks do not need to match exactly —
they only help the player reason; the puzzle is solved as soon as the
filled-cell set is correct.
"""
from typing import List, Optional, Tuple


EMPTY = 0
FILLED = 1
MARKED = 2


class IllegalMove(Exception):
    pass


def derive_clues(line: List[int]) -> List[int]:
    """Given a line of solution values (0/1), return its clue list.

    An all-empty line returns [0] by convention.
    """
    runs: List[int] = []
    cur = 0
    for v in line:
        if v == FILLED:
            cur += 1
        else:
            if cur > 0:
                runs.append(cur)
            cur = 0
    if cur > 0:
        runs.append(cur)
    if not runs:
        return [0]
    return runs


def derive_row_clues(solution: List[List[int]]) -> List[List[int]]:
    return [derive_clues(row) for row in solution]


def derive_col_clues(solution: List[List[int]]) -> List[List[int]]:
    if not solution:
        return []
    cols = len(solution[0])
    return [derive_clues([row[c] for row in solution]) for c in range(cols)]


class Board:
    def __init__(self, solution: List[List[int]]):
        if not solution or not solution[0]:
            raise ValueError("solution must be non-empty")
        self.rows = len(solution)
        self.cols = len(solution[0])
        for row in solution:
            if len(row) != self.cols:
                raise ValueError("solution rows have inconsistent length")
            for v in row:
                if v not in (EMPTY, FILLED):
                    raise ValueError("solution cells must be 0 or 1")
        self.solution: List[List[int]] = [row[:] for row in solution]
        self.row_clues: List[List[int]] = derive_row_clues(self.solution)
        self.col_clues: List[List[int]] = derive_col_clues(self.solution)
        self.grid: List[List[int]] = [[EMPTY] * self.cols for _ in range(self.rows)]
        self.history: List[Tuple[int, int, int, int]] = []  # (r, c, prev, new)

    def reset(self) -> None:
        self.grid = [[EMPTY] * self.cols for _ in range(self.rows)]
        self.history = []

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def set_cell(self, r: int, c: int, state: int) -> None:
        if state not in (EMPTY, FILLED, MARKED):
            raise IllegalMove(f"invalid state: {state}")
        if not self.in_bounds(r, c):
            raise IllegalMove(f"out of bounds: ({r}, {c})")
        prev = self.grid[r][c]
        if prev == state:
            return
        self.grid[r][c] = state
        self.history.append((r, c, prev, state))

    def fill(self, r: int, c: int) -> None:
        self.set_cell(r, c, FILLED)

    def mark(self, r: int, c: int) -> None:
        self.set_cell(r, c, MARKED)

    def erase(self, r: int, c: int) -> None:
        self.set_cell(r, c, EMPTY)

    def toggle_fill(self, r: int, c: int) -> None:
        """Cycle EMPTY → FILLED → EMPTY (skip MARKED)."""
        if not self.in_bounds(r, c):
            raise IllegalMove(f"out of bounds: ({r}, {c})")
        cur = self.grid[r][c]
        if cur == FILLED:
            self.set_cell(r, c, EMPTY)
        else:
            self.set_cell(r, c, FILLED)

    def toggle_mark(self, r: int, c: int) -> None:
        """Cycle EMPTY → MARKED → EMPTY (skip FILLED)."""
        if not self.in_bounds(r, c):
            raise IllegalMove(f"out of bounds: ({r}, {c})")
        cur = self.grid[r][c]
        if cur == MARKED:
            self.set_cell(r, c, EMPTY)
        else:
            self.set_cell(r, c, MARKED)

    def undo(self) -> bool:
        if not self.history:
            return False
        r, c, prev, _new = self.history.pop()
        self.grid[r][c] = prev
        return True

    def is_solved(self) -> bool:
        for r in range(self.rows):
            for c in range(self.cols):
                want = self.solution[r][c] == FILLED
                got = self.grid[r][c] == FILLED
                if want != got:
                    return False
        return True

    def filled_count(self) -> int:
        return sum(1 for row in self.grid for v in row if v == FILLED)

    def total_filled_in_solution(self) -> int:
        return sum(1 for row in self.solution for v in row if v == FILLED)

    def errors(self) -> int:
        """Count cells the player filled that are not filled in the solution."""
        bad = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == FILLED and self.solution[r][c] != FILLED:
                    bad += 1
        return bad

    def render_text(self) -> str:
        # Compute the column-clue header height
        max_col_clue = max((len(cl) for cl in self.col_clues), default=1)
        # Row-clue width on the left
        row_clue_strs = [" ".join(str(x) for x in cl) for cl in self.row_clues]
        row_label_width = max((len(s) for s in row_clue_strs), default=0)
        lines: List[str] = []
        # Column-clue header rows
        for i in range(max_col_clue):
            line = " " * (row_label_width + 2)
            for cl in self.col_clues:
                pad = max_col_clue - len(cl)
                idx = i - pad
                if 0 <= idx < len(cl):
                    line += f"{cl[idx]:>2}"
                else:
                    line += "  "
            lines.append(line)
        # Grid rows
        for r in range(self.rows):
            label = row_clue_strs[r].rjust(row_label_width)
            cells = []
            for c in range(self.cols):
                v = self.grid[r][c]
                if v == FILLED:
                    cells.append(" ●")
                elif v == MARKED:
                    cells.append(" ✗")
                else:
                    cells.append(" ·")
            lines.append(f"{label} |" + "".join(cells))
        return "\n".join(lines)
