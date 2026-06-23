"""
Minesweeper Game Logic
Simple implementation for GitHub Actions integration
"""

import random
import json
from dataclasses import dataclass, asdict
from typing import List, Tuple
from enum import Enum


class CellState(Enum):
    """State of a cell in the game"""
    HIDDEN = "hidden"
    REVEALED = "revealed"
    FLAGGED = "flagged"


class GameStatus(Enum):
    """Status of the game"""
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"


@dataclass
class Cell:
    """Represents a single cell in the Minesweeper board"""
    is_mine: bool
    state: str  # "hidden", "revealed", "flagged"
    adjacent_mines: int = 0
    suppress_number: bool = False

    def to_dict(self):
        return {
            "is_mine": self.is_mine,
            "state": self.state,
            "adjacent_mines": self.adjacent_mines,
            "suppress_number": self.suppress_number
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            is_mine=data["is_mine"],
            state=data["state"],
            adjacent_mines=data.get("adjacent_mines", 0),
            suppress_number=data.get("suppress_number", False)
        )


class Minesweeper:
    """Minesweeper game engine"""

    def __init__(self, width: int = 8, height: int = 8, mines: int = 10):
        self.width = width
        self.height = height
        self.mine_count = mines
        self.board: List[List[Cell]] = []
        self.status = GameStatus.ACTIVE.value
        self.moves = 0
        self._initialize_board()

    def _initialize_board(self):
        """Initialize empty board"""
        self.board = [
            [Cell(is_mine=False, state=CellState.HIDDEN.value) for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def _place_mines(self):
        """Place mines randomly on the board"""
        placed = 0
        while placed < self.mine_count:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)
            if not self.board[row][col].is_mine:
                self.board[row][col].is_mine = True
                placed += 1

    def _calculate_adjacent_mines(self):
        """Calculate number of adjacent mines for each cell"""
        for row in range(self.height):
            for col in range(self.width):
                if not self.board[row][col].is_mine:
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < self.height and 0 <= nc < self.width:
                                if self.board[nr][nc].is_mine:
                                    count += 1
                    self.board[row][col].adjacent_mines = count

    def _first_move(self, row: int, col: int):
        """Generate board with first move being safe"""
        self._place_mines()
        # If first move is on a mine, relocate it
        if self.board[row][col].is_mine:
            self.board[row][col].is_mine = False
            # Place mine elsewhere
            placed = False
            while not placed:
                r = random.randint(0, self.height - 1)
                c = random.randint(0, self.width - 1)
                if (r, c) != (row, col) and not self.board[r][c].is_mine:
                    self.board[r][c].is_mine = True
                    placed = True
        self._calculate_adjacent_mines()

    def _reveal_flood_fill(self, row: int, col: int):
        """Flood fill algorithm to reveal safe areas"""
        if not (0 <= row < self.height and 0 <= col < self.width):
            return
        
        cell = self.board[row][col]
        if cell.state != CellState.HIDDEN.value:
            return

        cell.state = CellState.REVEALED.value

        if cell.adjacent_mines == 0 and not cell.is_mine:
            # Recursively reveal adjacent cells
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    self._reveal_flood_fill(row + dr, col + dc)

    def _first_click_reveal(self, row: int, col: int) -> None:
        """Reveal the entire connected non-mine region starting at (row, col).

        This is a special first-click behavior: reveal all connected cells that are not mines
        (connectivity via 8-neighborhood). After this, suppression of interior numbers is applied.
        """
        stack = [(row, col)]
        visited = set()
        while stack:
            r, c = stack.pop()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            if not (0 <= r < self.height and 0 <= c < self.width):
                continue
            cell = self.board[r][c]
            if cell.is_mine:
                continue
            if cell.state == CellState.REVEALED.value:
                continue
            cell.state = CellState.REVEALED.value
            # push neighbors regardless of adjacent_mines (we reveal whole connected non-mine component)
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        if (nr, nc) not in visited and not self.board[nr][nc].is_mine:
                            stack.append((nr, nc))

    def reveal(self, row: int, col: int) -> bool:
        """
        Reveal a cell. Returns True if valid move, False if already revealed/flagged.
        """
        if not (0 <= row < self.height and 0 <= col < self.width):
            return False

        cell = self.board[row][col]
        
        if cell.state != CellState.HIDDEN.value:
            return False

        # First move setup
        first_click = (self.moves == 0)
        if first_click:
            self._first_move(row, col)

        if cell.is_mine:
            cell.state = CellState.REVEALED.value
            self.status = GameStatus.LOST.value
        else:
            if first_click:
                # Special first-click behavior: reveal whole connected non-mine region
                self._first_click_reveal(row, col)
            else:
                self._reveal_flood_fill(row, col)

            if self._check_win():
                self.status = GameStatus.WON.value

        # After the first click, suppress interior numbers so only edge numbers show
        if first_click and self.status == GameStatus.ACTIVE.value:
            self._suppress_interior_numbers()

        self.moves += 1
        return True

    def toggle_flag(self, row: int, col: int) -> bool:
        """Toggle flag on a hidden cell"""
        if not (0 <= row < self.height and 0 <= col < self.width):
            return False

        cell = self.board[row][col]

        if cell.state == CellState.HIDDEN.value:
            cell.state = CellState.FLAGGED.value
            return True
        elif cell.state == CellState.FLAGGED.value:
            cell.state = CellState.HIDDEN.value
            return True

        return False

    def _check_win(self) -> bool:
        """Check if player has won"""
        for row in self.board:
            for cell in row:
                if not cell.is_mine and cell.state != CellState.REVEALED.value:
                    return False
        return True

    def render_board(self, reveal_mines: bool = False) -> str:
        """
        Render the board as a string for display.
        reveal_mines: If True, shows all mines (for game over)
        """
        lines = ["```"]
        lines.append("  " + "  ".join(str(i) for i in range(self.width)))
        
        for row_idx, row in enumerate(self.board):
            line = f"{row_idx} "
            for cell in row:
                if cell.state == CellState.HIDDEN.value:
                    line += "■ "
                elif cell.state == CellState.FLAGGED.value:
                    line += "🚩 "
                elif cell.is_mine and reveal_mines:
                    line += "💣 "
                elif cell.adjacent_mines == 0:
                    line += "⬜ "
                else:
                    # If suppress_number is set (only used after first click), show empty instead
                    if getattr(cell, 'suppress_number', False):
                        line += "⬜ "
                    else:
                        line += f"{cell.adjacent_mines} "
            lines.append(line)
        lines.append("```")
        
        return "\n".join(lines)

    def get_state(self) -> dict:
        """Serialize game state to dictionary"""
        return {
            "width": self.width,
            "height": self.height,
            "mine_count": self.mine_count,
            "status": self.status,
            "moves": self.moves,
            "board": [
                [cell.to_dict() for cell in row]
                    for row in self.board
                ]
        }

    @classmethod
    def from_state(cls, state: dict) -> "Minesweeper":
        """Deserialize game state from dictionary"""
        game = cls(state["width"], state["height"], state["mine_count"])
        game.status = state["status"]
        game.moves = state["moves"]
        game.board = [
            [Cell.from_dict(cell_data) for cell_data in row]
            for row in state["board"]
        ]
        return game

    def _suppress_interior_numbers(self) -> None:
        """Mark revealed cells that are interior (all neighbors revealed) to hide their numbers.

        Applied only after the first click so the revealed area looks cleaner: interior
        cells (even if they have a non-zero adjacent_mines) will display as empty.
        """
        for r in range(self.height):
            for c in range(self.width):
                cell = self.board[r][c]
                # Only consider revealed cells with numbers
                if cell.state != CellState.REVEALED.value:
                    continue
                if cell.adjacent_mines == 0:
                    # zeros already render as empty
                    cell.suppress_number = False
                    continue

                # Check neighbors; if any neighbor is still hidden or flagged, this is an edge
                interior = True
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.height and 0 <= nc < self.width:
                            neighbor = self.board[nr][nc]
                            if neighbor.state != CellState.REVEALED.value:
                                interior = False
                                break
                    if not interior:
                        break

                cell.suppress_number = interior


if __name__ == "__main__":
    # Test the game
    game = Minesweeper(8, 8, 10)
    game.reveal(0, 0)
    print(game.render_board())
    print(f"Status: {game.status}")
