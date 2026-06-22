"""
CLI interface for Minesweeper game
Used by GitHub Actions workflow
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from minesweeper.game import Minesweeper, GameStatus
from minesweeper.state_manager import StateManager


def format_help(game: Minesweeper) -> str:
    """Format help message with board coordinates"""
    help_text = """
**How to Play Minesweeper:**

Commands:
- `reveal ROW COL` - Reveal a cell (e.g., `reveal 0 0`)
- `flag ROW COL` - Flag/unflag a cell (e.g., `flag 2 3`)
- `new` - Start a new game
- `show` - Show current board state

Board Coordinates:
- Rows: 0-{} (top to bottom)
- Columns: 0-{} (left to right)

Current Board:
{}
""".format(game.height - 1, game.width - 1, game.render_board())
    return help_text


def main():
    parser = argparse.ArgumentParser(description="Minesweeper CLI")
    parser.add_argument("action", nargs="*", help="Action: reveal, flag, new, show, help")
    parser.add_argument("--state-file", default="game_state.json", help="State file location")
    
    args = parser.parse_args()
    action = args.action[0].lower() if args.action else "show"
    
    manager = StateManager(args.state_file)
    
    try:
        if action == "new":
            manager.clear_game()
            game = Minesweeper()
            manager.save_game(game)
            print("**New Game Started!**")
            print(format_help(game))
            
        elif action == "reveal":
            if len(args.action) < 3:
                print("Usage: reveal ROW COL")
                sys.exit(1)
            
            row, col = int(args.action[1]), int(args.action[2])
            game = manager.load_game()
            
            if not game.reveal(row, col):
                print("Invalid move! Cell already revealed or out of bounds.")
                print(game.render_board())
                sys.exit(1)
            
            manager.save_game(game)
            
            # Render appropriate output based on game status
            if game.status == GameStatus.WON.value:
                print("🎉 **YOU WON!** 🎉")
                print(game.render_board())
            elif game.status == GameStatus.LOST.value:
                print("💥 **GAME OVER!** You hit a mine! 💥")
                print(game.render_board(reveal_mines=True))
            else:
                print("Move accepted!")
                print(game.render_board())
            
        elif action == "flag":
            if len(args.action) < 3:
                print("Usage: flag ROW COL")
                sys.exit(1)
            
            row, col = int(args.action[1]), int(args.action[2])
            game = manager.load_game()
            
            if not game.toggle_flag(row, col):
                print("Invalid move! Can only flag hidden cells.")
                print(game.render_board())
                sys.exit(1)
            
            manager.save_game(game)
            print("Flag toggled!")
            print(game.render_board())
            
        elif action == "show":
            game = manager.load_game()
            print(format_help(game))
            if game.status != GameStatus.ACTIVE.value:
                if game.status == GameStatus.WON.value:
                    print("\n🎉 **GAME WON!** 🎉")
                else:
                    print("\n💥 **GAME OVER!**")
            
        elif action == "help":
            game = manager.load_game()
            print(format_help(game))
            
        else:
            print(f"Unknown action: {action}")
            parser.print_help()
            sys.exit(1)
            
    except ValueError as e:
        print(f"Error: Invalid input - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
