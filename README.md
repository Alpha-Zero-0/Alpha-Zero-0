# Hi, I'm David
<div align="center">
  <img width="345" height="340" alt="giphy-3" src="https://github.com/user-attachments/assets/1458c328-3141-4e2e-ac82-9e8db3dcd919" />
</div>

### Programming Languages
<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/Go-00ADD8?logo=go&logoColor=white" />
  <img src="https://img.shields.io/badge/R-276DC3?logo=r&logoColor=white" />
</div>

### Data & Backend
<div align="center">
  <img src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Firebase-FFCA28?logo=firebase&logoColor=black" />
</div>

### Game Development
<div align="center">
  <img src="https://img.shields.io/badge/Godot-478CBF?logo=godotengine&logoColor=white" />
</div>

### Tools, Automation & Publishing
<div align="center">
  <img src="https://img.shields.io/badge/VS%20Code-007ACC?logo=visualstudiocode&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white" />
  <img src="https://img.shields.io/badge/Power%20Automate-0066FF?logo=powerautomate&logoColor=white" />
  <img src="https://img.shields.io/badge/LaTeX-008080?logo=latex&logoColor=white" />
</div>

## Github
<div align="center">
  <!-- Top Row: Streak and Languages -->
  <img src="https://streak-stats.demolab.com?user=Alpha-Zero-0&theme=radical" alt="GitHub Streak" />
  <img src="https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=Alpha-Zero-0&theme=radical" alt="Top Languages" />
  <img src="https://metrics.lecoq.io/Alpha-Zero-0?template=classic&base=0&plugin_languages=yes&plugin_languages_limit=5" alt="Top Languages" />
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=Alpha-Zero-0&layout=donut&theme=radical" alt="Top Languages" />
  <img src="https://skillicons.dev/icons?i=py,html,css,js,git&theme=dark" alt="My Skills" />
  
  <br/><br/>
  
  <!-- Middle Row: Activity Graph (Wide) -->
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=Alpha-Zero-0&theme=react-dark" alt="GitHub Activity Graph" width="100%" />
  
  <br/><br/>
  
  <!-- Bottom Row: Heat Map (Wide) -->
  <img src="https://ghchart.rshah.org/Alpha-Zero-0" alt="GitHub Heat Map" width="100%" />
</div>


## LEETCODE
<div align="center">
  <img src="https://leetcard.jacoblin.cool/HIHIHIHIA?username=Alpha-Zero-0&theme=dark&ext=heatmap" alt="LeetCode Heatmap" width="50%" />
</div>

## Mini Game

### Minesweeper

Play Minesweeper through GitHub issue comments. The game lives in the `minesweeper/` folder, and GitHub Actions saves the board to `game_state.json` after every move.

Comment one of these commands on an issue:

```text
new
reveal ROW COL
reveal ROW COL ROW COL ...
flag ROW COL
flag ROW COL ROW COL ...
```

Examples:

```text
reveal 0 0 0 1 1 1
flag 2 3 2 4 3 4
```

Board symbols:

| Symbol | Meaning |
| --- | --- |
| `■` | Hidden cell |
| `F` | Flagged cell |
| `X` | Incorrect flag after game over |
| `*` | Mine after game over |
| blank | Revealed cell with no adjacent mines |
| `1`-`8` | Number of adjacent mines |

Rules:

- The first reveal is always safe, including the surrounding 3x3 area when possible.
- Blank cells flood-reveal connected blank cells and their bordering numbers.
- Revealing a mine ends the game and records a leaderboard loss for the player who triggered it.
- Revealing every non-mine cell wins the game and records a leaderboard win for the player who solved it.
- Batch reveal and flag commands are validated before the board changes.
- A batch reveal is applied from left to right and stops if the game is won or a mine is hit.

### Leaderboard

<!-- MINESWEEPER_LEADERBOARD_START -->
### Top Solvers

<img width="250" height="250" alt="giphy-2" src="https://github.com/user-attachments/assets/67d7eab7-cf99-493f-af40-2d012a8f66ae" />

| Rank | Player | Wins | Losses |
| ---: | --- | ---: | ---: |
| 1 | @Alpha-Zero-0 | 1 | 1 |

### Most Exploded

<img width="250" height="250" alt="giphy" src="https://github.com/user-attachments/assets/7959a7f3-ebbb-4cac-88a7-b14a36455bf6" />

| Rank | Player | Losses | Wins |
| ---: | --- | ---: | ---: |
| 1 | @Alpha-Zero-0 | 1 | 1 |
<!-- MINESWEEPER_LEADERBOARD_END -->

Local commands from the repository root:

```bash
python -m minesweeper.cli new --state-file game_state.json
python -m minesweeper.cli reveal 0 0 --state-file game_state.json
python -m minesweeper.cli reveal 0 1 1 1 --state-file game_state.json
python -m minesweeper.cli flag 2 3 2 4 --state-file game_state.json
python -m minesweeper.cli leaderboard --leaderboard-file minesweeper_leaderboard.json
```
