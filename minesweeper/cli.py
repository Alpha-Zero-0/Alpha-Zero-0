"""
CLI interface for Minesweeper game
Used by GitHub Actions workflow
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from minesweeper.game import Minesweeper
from minesweeper.leaderboard import Leaderboard
from minesweeper.state_manager import StateManager


def parse_coordinate_pairs(values: list[str], command: str) -> list[tuple[int, int]]:
    if not values or len(values) % 2 != 0:
        raise ValueError(f"Usage: {command} ROW COL [ROW COL ...]")

    coords = []
    for idx in range(0, len(values), 2):
        coords.append((int(values[idx]), int(values[idx + 1])))
    return coords


def validate_coordinates(game: Minesweeper, coords: list[tuple[int, int]]) -> None:
    for row, col in coords:
        if not (0 <= row < game.size and 0 <= col < game.size):
            raise ValueError(f"Cell out of bounds: {row} {col}")


def format_help(game: Minesweeper) -> str:
    """Format help message with board coordinates"""
    help_text = """
**How to Play Minesweeper:**

Commands:
- `reveal ROW COL [ROW COL ...]` - Reveal one or more cells (e.g., `reveal 0 0 0 1`)
- `flag ROW COL [ROW COL ...]` - Flag/unflag one or more cells (e.g., `flag 2 3 2 4`)
- `new` - Start a new game
- `show` - Show current board state
- `help` - Show this help text
- `leaderboard` - Show the top Minesweeper players

Board Coordinates:
- Rows: 0-{} (top to bottom)
- Columns: 0-{} (left to right)

Current Board:
{}
""".format(game.height - 1, game.width - 1, game.render_board(reveal_mines=game.hitBomb))
    return help_text


def main():
    parser = argparse.ArgumentParser(description="Minesweeper CLI")
    parser.add_argument("action", nargs="*", help="Action: reveal, flag, new, show, help, leaderboard")
    parser.add_argument("--state-file", default="game_state.json", help="State file location")
    parser.add_argument("--leaderboard-file", default="minesweeper_leaderboard.json", help="Leaderboard file location")
    parser.add_argument("--player", default="local", help="Player username for win/loss tracking")
    
    args = parser.parse_args()
    action = args.action[0].lower() if args.action else "show"
    
    manager = StateManager(args.state_file)
    leaderboard = Leaderboard(args.leaderboard_file)
    
    try:
        if action == "new":
            manager.clear_game()
            game = Minesweeper()
            manager.save_game(game)
            print("**New Game Started!**")
            print(format_help(game))
            
        elif action == "reveal":
            coords = parse_coordinate_pairs(args.action[1:], "reveal")
            game = manager.load_game()
            validate_coordinates(game, coords)

            if game.winner or game.hitBomb:
                print(game.render_board(reveal_mines=True))
                sys.exit(0)

            applied = 0
            skipped = 0

            for row, col in coords:
                cell = game.board[row][col]
                if cell.revealed or cell.flagged:
                    skipped += 1
                    continue

                if applied == 0 and not game.timerId:
                    game.set_timer()

                hit_bomb = game.reveal(row, col)
                applied += 1
                if hit_bomb or game.winner:
                    break

            manager.save_game(game)
            
            # Render appropriate output based on game status
            if game.hitBomb:
                leaderboard.record_result(args.player, won=False)
                print("💥 **GAME OVER!** You hit a mine! 💥")
                print(game.render_board(reveal_mines=True))
                print("")
                print(leaderboard.render_markdown())
            elif game.winner:
                leaderboard.record_result(args.player, won=True)
                print("🎉 **YOU WON!** 🎉")
                print(game.render_board())
                print("")
                print(leaderboard.render_markdown())
            else:
                print(f"Move accepted! Revealed {applied} cell(s).")
                if skipped:
                    print(f"Skipped {skipped} already revealed or flagged cell(s).")
                print(game.render_board())
            
        elif action == "flag":
            coords = parse_coordinate_pairs(args.action[1:], "flag")
            game = manager.load_game()
            validate_coordinates(game, coords)

            toggled = 0
            skipped = 0
            for row, col in coords:
                was_flagged = game.board[row][col].flagged
                is_flagged = game.toggle_flag(row, col)
                if was_flagged != is_flagged:
                    toggled += 1
                else:
                    skipped += 1

            manager.save_game(game)
            print(f"Flag toggled! Updated {toggled} cell(s).")
            if skipped:
                print(f"Skipped {skipped} revealed cell(s).")
            print(game.render_board())
            
        elif action == "show":
            game = manager.load_game()
            print(format_help(game))
            if game.hitBomb or game.winner:
                if game.winner:
                    print("\n🎉 **GAME WON!** 🎉")
                else:
                    print("\n💥 **GAME OVER!**")
            
        elif action == "help":
            game = manager.load_game()
            print(format_help(game))

        elif action == "leaderboard":
            print(leaderboard.render_markdown())
            
        else:
            print(f"Unknown action: {action}")
            parser.print_help()
            sys.exit(1)
            
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
