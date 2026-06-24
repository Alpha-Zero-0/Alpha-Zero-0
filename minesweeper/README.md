# Interactive Minesweeper Game

Play Minesweeper through GitHub issue comments or from the command line. The game state is saved to `game_state.json`, so each move continues from the previous board.

## Commands

Start a fresh game:

```text
new
```

Show the current board:

```text
show
```

Show the help text and current board:

```text
help
```

Reveal one cell:

```text
reveal ROW COL
```

Reveal multiple cells in one move:

```text
reveal ROW COL ROW COL ...
```

Example:

```text
reveal 0 0 0 1 1 1
```

Flag or unflag one cell:

```text
flag ROW COL
```

Flag or unflag multiple cells in one move:

```text
flag ROW COL ROW COL ...
```

Example:

```text
flag 2 3 2 4 3 4
```

Rows and columns are zero-indexed. On the default board, valid coordinates are `0` through `15`.

## Board Symbols

- `■` = hidden cell
- `F` = flagged cell
- `X` = incorrect flag after game over
- `*` = mine after game over
- blank cell = revealed cell with no adjacent mines
- `1`-`8` = number of adjacent mines

## Rules

- The default board is 16x16 with 40 mines.
- The first reveal is always safe, including the surrounding 3x3 area when possible.
- Revealing a blank cell flood-reveals connected blank cells and their bordering numbers.
- Revealing a mine ends the game and shows the full board.
- Revealing all non-mine cells wins the game.
- Flagging toggles a cell between flagged and unflagged.
- Revealed cells cannot be flagged.
- Batch reveal and flag commands are validated before they change the board; if any coordinate is out of bounds or malformed, the command is rejected.
- A batch reveal is applied from left to right and stops if the game is won or a mine is hit.

## GitHub Play

Comment on an issue with one of the commands above. GitHub Actions runs the game, saves the updated state, and replies with the rendered board.

The workflow also supports manual dispatch for:

- `new`
- `show`
- `help`

## Local Play

Run commands from the repository root:

```bash
python -m minesweeper.cli new --state-file game_state.json
python -m minesweeper.cli reveal 0 0 --state-file game_state.json
python -m minesweeper.cli reveal 0 1 1 1 --state-file game_state.json
python -m minesweeper.cli flag 2 3 2 4 --state-file game_state.json
python -m minesweeper.cli show --state-file game_state.json
```

## Project Files

```text
minesweeper/
├── __init__.py
├── cli.py
├── game.py
├── requirements.txt
└── state_manager.py
```

## Technical Notes

- Language: Python 3.10 in GitHub Actions.
- State storage: JSON through `StateManager`.
- Automation: `.github/workflows/minesweeper.yml`.
- Dependencies: none outside the Python standard library.
