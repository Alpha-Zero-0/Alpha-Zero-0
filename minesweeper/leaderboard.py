"""
Leaderboard helpers for the Minesweeper game.
"""

from __future__ import annotations

import json
import os
from typing import Any


class Leaderboard:
    """Tracks wins and losses by GitHub username."""

    def __init__(self, leaderboard_file: str = "minesweeper_leaderboard.json"):
        self.leaderboard_file = leaderboard_file

    def load(self) -> dict[str, Any]:
        if not os.path.exists(self.leaderboard_file):
            return _empty_leaderboard()

        try:
            with open(self.leaderboard_file, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return _empty_leaderboard()

        if not isinstance(data, dict) or not isinstance(data.get("players"), dict):
            return _empty_leaderboard()
        return data

    def save(self, data: dict[str, Any]) -> None:
        with open(self.leaderboard_file, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)

    def record_result(self, player: str, won: bool) -> None:
        player = player.strip() or "local"
        data = self.load()
        stats = data["players"].setdefault(player, {"wins": 0, "losses": 0})
        stats["wins"] = int(stats.get("wins", 0))
        stats["losses"] = int(stats.get("losses", 0))

        if won:
            stats["wins"] += 1
        else:
            stats["losses"] += 1

        self.save(data)

    def top_winners(self, limit: int = 5) -> list[tuple[str, int, int]]:
        return _rank_players(self.load(), "wins", limit)

    def top_failures(self, limit: int = 5) -> list[tuple[str, int, int]]:
        return _rank_players(self.load(), "losses", limit)

    def render_markdown(self, limit: int = 5) -> str:
        return "\n\n".join(
            [
                _render_table("Top Solvers", self.top_winners(limit), "Wins"),
                _render_table("Most Exploded", self.top_failures(limit), "Losses"),
            ]
        )


def _empty_leaderboard() -> dict[str, Any]:
    return {"players": {}}


def _rank_players(data: dict[str, Any], field: str, limit: int) -> list[tuple[str, int, int]]:
    players = data.get("players", {})
    rows = []
    for player, stats in players.items():
        score = int(stats.get(field, 0))
        if score <= 0:
            continue
        rows.append((player, int(stats.get("wins", 0)), int(stats.get("losses", 0))))

    field_idx = 1 if field == "wins" else 2
    rows.sort(key=lambda row: (-row[field_idx], row[0].lower()))
    return rows[:limit]


def _render_table(title: str, rows: list[tuple[str, int, int]], score_label: str) -> str:
    other_label = "Losses" if score_label == "Wins" else "Wins"
    lines = [
        f"### {title}",
        "",
        f"| Rank | Player | {score_label} | {other_label} |",
        "| ---: | --- | ---: | ---: |",
    ]

    if not rows:
        lines.append("| - | No completed games yet | 0 | 0 |")
        return "\n".join(lines)

    for idx, (player, wins, losses) in enumerate(rows, start=1):
        score = wins if score_label == "Wins" else losses
        other_score = losses if score_label == "Wins" else wins
        lines.append(f"| {idx} | @{player} | {score} | {other_score} |")
    return "\n".join(lines)
