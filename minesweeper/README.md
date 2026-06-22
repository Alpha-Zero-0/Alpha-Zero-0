# 🎮 Interactive Minesweeper Game

An interactive Minesweeper game that you can play directly on this GitHub profile using issue comments and GitHub Actions!

## How to Play

### Starting a New Game
Comment on any issue with:
```
new
```

### Making Moves
Use the following commands in issue comments:

**Reveal a cell:**
```
reveal ROW COL
```
Example: `reveal 0 0` (reveals cell at row 0, column 0)

**Flag/Unflag a cell:**
```
flag ROW COL
```
Example: `flag 2 3` (flags cell at row 2, column 3)

**Show current board:**
```
show
```

**Get help:**
```
help
```

## Board Layout
- **■** = Hidden cell
- **🚩** = Flagged cell
- **⬜** = Empty cell (0 adjacent mines)
- **1-8** = Number of adjacent mines
- **💣** = Mine (revealed after game over)

## Game Rules
- Classic Minesweeper rules apply
- First move is always safe (no mine)
- Reveal all safe cells to win
- One mine revealed = game over
- Board is 8x8 with 10 mines

## File Structure
```
minesweeper/
├── __init__.py          # Package initialization
├── game.py              # Core game logic
├── state_manager.py     # Game state persistence
├── cli.py               # Command-line interface
└── requirements.txt     # Python dependencies
```

## Game State
The game state is automatically saved to `game_state.json` and persisted in the repository. This allows continuous play across multiple moves.

## Local Testing
To test the game locally:

```bash
# Install (no external dependencies needed)
cd minesweeper

# Show help
python -m cli help

# Start new game
python -m cli new

# Make a move
python -m cli reveal 0 0

# Flag a cell
python -m cli flag 1 1
```

## Technical Details
- **Language:** Python 3.8+
- **State Storage:** JSON file in repository
- **Automation:** GitHub Actions workflow
- **Trigger:** Issue comments and workflow dispatch
- **Board Size:** 8x8 with 10 mines (configurable)

## Future Enhancements
- [ ] Difficulty levels (easy, medium, hard)
- [ ] Leaderboard/statistics tracking
- [ ] Mobile-friendly board rendering
- [ ] Different board sizes
- [ ] Multiplayer support
