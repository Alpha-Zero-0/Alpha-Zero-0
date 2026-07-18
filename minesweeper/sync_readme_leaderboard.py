"""
Refresh the Minesweeper leaderboard block in the root README.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from minesweeper.leaderboard import Leaderboard


START_MARKER = "<!-- MINESWEEPER_LEADERBOARD_START -->"
END_MARKER = "<!-- MINESWEEPER_LEADERBOARD_END -->"

# Define the HTML for the first image
IMAGE_TOP_SOLVERS = """
<div style="display: flex; justify-content: center; align-items: center; gap: 20px;">
  <img width="250" height="250" alt="giphy-2" src="https://github.com/user-attachments/assets/79ed7122-d568-415f-84cd-71253935923d" />
</div>
"""

# Define the HTML for the second image
IMAGE_MOST_EXPLODED = """
<div style="display: flex; justify-content: center; align-items: center; gap: 20px;">
  <img width="250" height="250" alt="giphy-4" src="https://github.com/user-attachments/assets/ef4a2e7c-5a89-4ca5-b8bb-6624be5e0f35" />
</div>
"""

def update_readme(readme_path: Path, leaderboard_file: str) -> None:
    content = readme_path.read_text()
    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError("README is missing Minesweeper leaderboard markers")

    before, rest = content.split(START_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)
    
    # Generate the standard markdown text from your leaderboard tool
    leaderboard = Leaderboard(leaderboard_file).render_markdown()
    
    # Inject the first image directly under the "Top Solvers" header
    if "### Top Solvers" in leaderboard:
        leaderboard = leaderboard.replace(
            "### Top Solvers", 
            f"### Top Solvers\n\n{IMAGE_TOP_SOLVERS.strip()}"
        )
        
    # Inject the second image directly under the "Most Exploded" header
    if "### Most Exploded" in leaderboard:
        leaderboard = leaderboard.replace(
            "### Most Exploded", 
            f"### Most Exploded\n\n{IMAGE_MOST_EXPLODED.strip()}"
        )
    
    # Reassemble the document with the updated leaderboard content
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
