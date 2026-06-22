"""
Game state manager for persisting Minesweeper games
"""

import json
import os
from datetime import datetime
from minesweeper.game import Minesweeper, GameStatus


class StateManager:
    """Manages saving and loading game states"""

    def __init__(self, state_file: str = "game_state.json"):
        self.state_file = state_file

    def save_game(self, game: Minesweeper) -> None:
        """Save current game state to file"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "game": game.get_state()
        }
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def load_game(self) -> Minesweeper:
        """Load game state from file"""
        if not os.path.exists(self.state_file):
            return Minesweeper()
        
        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
            return Minesweeper.from_state(state["game"])
        except (json.JSONDecodeError, KeyError, ValueError):
            # Return new game if file is corrupted
            return Minesweeper()

    def clear_game(self) -> None:
        """Clear saved game state"""
        if os.path.exists(self.state_file):
            os.remove(self.state_file)

    def has_active_game(self) -> bool:
        """Check if there's an active game in progress"""
        if not os.path.exists(self.state_file):
            return False
        
        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)
            game_status = state["game"]["status"]
            return game_status == GameStatus.ACTIVE.value
        except (json.JSONDecodeError, KeyError):
            return False
