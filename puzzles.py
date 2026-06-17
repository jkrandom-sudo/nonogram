"""Bundled nonogram puzzles.

Each puzzle is a name + a 0/1 grid (the solution). Row & column clues are
derived from the grid in board.py. Hand-crafted to look like simple
pictograms when solved.
"""
from typing import Dict, List


def _grid(rows: List[str]) -> List[List[int]]:
    """Convert a list of strings made of '#' and '.' into a 0/1 grid."""
    return [[1 if ch == "#" else 0 for ch in row] for row in rows]


PUZZLES: Dict[str, Dict] = {
    "easy_heart": {
        "name_zh": "爱心",
        "name_en": "Heart",
        "size": 5,
        "solution": _grid([
            ".#.#.",
            "#####",
            "#####",
            ".###.",
            "..#..",
        ]),
    },
    "easy_arrow": {
        "name_zh": "箭头",
        "name_en": "Arrow",
        "size": 5,
        "solution": _grid([
            "..#..",
            ".###.",
            "#####",
            "..#..",
            "..#..",
        ]),
    },
    "easy_smiley": {
        "name_zh": "笑脸",
        "name_en": "Smiley",
        "size": 5,
        "solution": _grid([
            ".###.",
            "#.#.#",
            "#####",
            "#...#",
            ".###.",
        ]),
    },
    "medium_house": {
        "name_zh": "小房子",
        "name_en": "House",
        "size": 10,
        "solution": _grid([
            "....##....",
            "...####...",
            "..######..",
            ".########.",
            "##########",
            "##########",
            "##......##",
            "##.####.##",
            "##.#..#.##",
            "##.####.##",
        ]),
    },
    "medium_tree": {
        "name_zh": "圣诞树",
        "name_en": "Tree",
        "size": 10,
        "solution": _grid([
            "....##....",
            "...####...",
            "..######..",
            ".########.",
            "....##....",
            "...####...",
            "..######..",
            ".########.",
            "##########",
            "....##....",
        ]),
    },
    "medium_cat": {
        "name_zh": "小猫",
        "name_en": "Cat",
        "size": 10,
        "solution": _grid([
            "##......##",
            "###....###",
            "##########",
            "##.####.##",
            "##.####.##",
            "##########",
            "###.##.###",
            "##########",
            "..######..",
            "..##..##..",
        ]),
    },
}


def list_puzzles() -> List[str]:
    return list(PUZZLES.keys())


def get_puzzle(key: str) -> Dict:
    if key not in PUZZLES:
        raise KeyError(f"unknown puzzle: {key}")
    return PUZZLES[key]


def puzzles_by_size(size: int) -> List[str]:
    return [k for k, v in PUZZLES.items() if v["size"] == size]
