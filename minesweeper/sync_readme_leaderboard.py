"""
Refresh the Minesweeper leaderboard block in the root README.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from minesweeper.leaderboard import Leaderboard


START_MARKER = "<!-- MINESWEEPER_LEADERBOARD_START -->"
END_MARKER = "<!-- MINESWEEPER_LEADERBOARD_END -->"


def update_readme(readme_path: Path, leaderboard_file: str) -> None:
    content = readme_path.read_text()
    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError("README is missing Minesweeper leaderboard markers")

    before, rest = content.split(START_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)
    leaderboard = Leaderboard(leaderboard_file).render_markdown()
    updated = f"{before}{START_MARKER}\n{leaderboard}\n{END_MARKER}{after}"
    readme_path.write_text(updated)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Minesweeper leaderboard into README")
    parser.add_argument("--readme", default="README.md", help="Root README path")
    parser.add_argument("--leaderboard-file", default="minesweeper_leaderboard.json")
    args = parser.parse_args()

    update_readme(Path(args.readme), args.leaderboard_file)


if __name__ == "__main__":
    main()
