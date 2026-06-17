"""Persistent leaderboard (top 10)."""
import json
import time
from pathlib import Path
from typing import List, Optional


DEFAULT_PATH = Path.home() / ".nonogram_scores.json"
MAX_ENTRIES = 10


def load(path: Optional[Path] = None) -> List[dict]:
    if path is None:
        path = DEFAULT_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return []


def save(scores: List[dict], path: Optional[Path] = None) -> None:
    if path is None:
        path = DEFAULT_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def add(name: str, score: int, puzzle: str, moves: int, path: Optional[Path] = None) -> List[dict]:
    scores = load(path)
    scores.append({
        "name": name[:12] if name else "anon",
        "score": int(score),
        "puzzle": puzzle,
        "moves": int(moves),
        "time": int(time.time()),
    })
    scores.sort(key=lambda e: (-int(e.get("score", 0)), int(e.get("time", 0))))
    scores = scores[:MAX_ENTRIES]
    save(scores, path)
    return scores


def compute_score(size: int, moves: int, hints_used: int = 0) -> int:
    """Bigger boards are worth more; fewer moves and fewer hints score higher."""
    base = size * size * 50
    move_penalty = max(0, moves - size * size) * 2
    hint_penalty = hints_used * 25
    return max(0, base - move_penalty - hint_penalty)
