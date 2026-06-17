"""Nonogram line solver — finds cells that are forced to be filled or empty
given a single line's clues, used to generate hints.

Strategy: enumerate all valid placements of the clue runs on the line that
are consistent with the player's current state, then any cell that is
filled in *every* such placement is forced filled, and any cell that is
empty in every such placement is forced empty.
"""
from typing import List, Optional, Tuple

from board import EMPTY, FILLED, MARKED


def line_placements(length: int, clues: List[int], current: List[int]):
    """Yield all valid fill patterns for `clues` on a line of `length`,
    consistent with the player's `current` state.

    Each yielded pattern is a tuple of length `length` with values 0/1 where
    1 = filled and 0 = empty. Patterns must satisfy:
      - Where `current[i] == FILLED`, the pattern has 1.
      - Where `current[i] == MARKED`, the pattern has 0.
      - Where `current[i] == EMPTY`, no constraint.
    """
    if not clues or clues == [0]:
        # All-empty line is the only placement
        pattern = [0] * length
        if _consistent(pattern, current):
            yield tuple(pattern)
        return

    def helper(start_pos: int, idx: int, pattern: List[int]):
        if idx == len(clues):
            # Remaining cells stay 0; check consistency.
            if _consistent(pattern, current):
                yield tuple(pattern)
            return
        run = clues[idx]
        remaining_runs = clues[idx + 1:]
        # Smallest length needed for remaining runs (including the gap before each)
        remaining = sum(remaining_runs) + len(remaining_runs)
        max_start = length - remaining - run
        for s in range(start_pos, max_start + 1):
            new_pattern = pattern[:]
            ok = True
            # Prefix between start_pos and s must be 0; check player state
            for i in range(start_pos, s):
                if current[i] == FILLED:
                    ok = False
                    break
            if not ok:
                continue
            # The run at [s, s+run) must be 1
            for i in range(s, s + run):
                if current[i] == MARKED:
                    ok = False
                    break
                new_pattern[i] = 1
            if not ok:
                continue
            # Cell after the run (if any) must be 0
            if s + run < length:
                if current[s + run] == FILLED:
                    continue
                # cell stays 0 in new_pattern
            yield from helper(s + run + 1, idx + 1, new_pattern)

    yield from helper(0, 0, [0] * length)


def _consistent(pattern: List[int], current: List[int]) -> bool:
    for i, p in enumerate(pattern):
        cur = current[i]
        if cur == FILLED and p != 1:
            return False
        if cur == MARKED and p != 0:
            return False
    return True


def forced_cells(length: int, clues: List[int], current: List[int]) -> List[Tuple[int, int]]:
    """Return [(index, state), ...] cells that are forced.

    state is either FILLED (1) or MARKED-as-empty (we use the value 2 to
    indicate "definitely empty"). Cells already matching their forced
    state are excluded.
    """
    placements = list(line_placements(length, clues, current))
    if not placements:
        return []
    forced: List[Tuple[int, int]] = []
    for i in range(length):
        all_one = all(p[i] == 1 for p in placements)
        all_zero = all(p[i] == 0 for p in placements)
        if all_one and current[i] != FILLED:
            forced.append((i, FILLED))
        elif all_zero and current[i] != MARKED:
            forced.append((i, MARKED))
    return forced


def find_hint(board) -> Optional[Tuple[int, int, int]]:
    """Find a forced cell on any row or column of `board`.

    Returns (r, c, state) or None.
    """
    rows, cols = board.rows, board.cols
    # Try rows first
    for r in range(rows):
        line = board.grid[r]
        forced = forced_cells(cols, board.row_clues[r], line)
        if forced:
            i, st = forced[0]
            return (r, i, st)
    for c in range(cols):
        line = [board.grid[r][c] for r in range(rows)]
        forced = forced_cells(rows, board.col_clues[c], line)
        if forced:
            i, st = forced[0]
            return (i, c, st)
    return None
