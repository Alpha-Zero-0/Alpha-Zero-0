"""Minesweeper game logic."""

import random
from dataclasses import dataclass
from enum import Enum
from typing import List


class CellState(Enum):
    """State of a cell in the game."""

    HIDDEN = "hidden"
    REVEALED = "revealed"
    FLAGGED = "flagged"


class GameStatus(Enum):
    """Game outcome state."""

    ACTIVE = "active"
    WON = "won"
    LOST = "lost"


@dataclass
class Cell:
    """Single Minesweeper cell."""

    row: int
    col: int
    bomb: bool = False
    revealed: bool = False
    flagged: bool = False
    adjacent_mines: int = 0

    def get_adj_cells(self, game: "Minesweeper") -> List["Cell"]:
        adj = []
        last_row = game.height - 1
        last_col = game.width - 1

        if self.row > 0 and self.col > 0:
            adj.append(game.board[self.row - 1][self.col - 1])
        if self.row > 0:
            adj.append(game.board[self.row - 1][self.col])
        if self.row > 0 and self.col < last_col:
            adj.append(game.board[self.row - 1][self.col + 1])
        if self.col < last_col:
            adj.append(game.board[self.row][self.col + 1])
        if self.row < last_row and self.col < last_col:
            adj.append(game.board[self.row + 1][self.col + 1])
        if self.row < last_row:
            adj.append(game.board[self.row + 1][self.col])
        if self.row < last_row and self.col > 0:
            adj.append(game.board[self.row + 1][self.col - 1])
        if self.col > 0:
            adj.append(game.board[self.row][self.col - 1])

        return adj

    def calc_adj_mines(self, game: "Minesweeper") -> None:
        self.adjacent_mines = sum(1 for cell in self.get_adj_cells(game) if cell.bomb)

    def flag(self) -> bool:
        if not self.revealed:
            self.flagged = not self.flagged
            return self.flagged
        return self.flagged

    def reveal(self, game: "Minesweeper") -> bool:
        """Reveal this cell. Returns True if a bomb was hit."""
        if self.revealed or self.flagged:
            return False

        self.revealed = True
        if self.bomb:
            return True

        if self.adjacent_mines == 0:
            for cell in self.get_adj_cells(game):
                if not cell.revealed and not cell.bomb:
                    cell.reveal(game)

        return False

    def to_dict(self) -> dict:
        return {
            "row": self.row,
            "col": self.col,
            "bomb": self.bomb,
            "revealed": self.revealed,
            "flagged": self.flagged,
            "adjacent_mines": self.adjacent_mines,
        }

    @classmethod
    def from_dict(cls, data: dict, row: int, col: int) -> "Cell":
        # Support both the old schema (is_mine/state) and the newer schema.
        bomb = data.get("bomb", data.get("is_mine", False))
        revealed = data.get("revealed", data.get("state") == CellState.REVEALED.value)
        flagged = data.get("flagged", data.get("state") == CellState.FLAGGED.value)
        adjacent_mines = data.get("adjacent_mines", data.get("adjBombs", 0))

        return cls(
            row=row,
            col=col,
            bomb=bomb,
            revealed=revealed,
            flagged=flagged,
            adjacent_mines=adjacent_mines,
        )


class Minesweeper:
    """Minesweeper engine with classic reveal/flag behavior."""

    def __init__(self, width: int = 8, height: int = 8, mines: int = 10):
        self.width = width
        self.height = height
        self.mine_count = mines
        self.board: List[List[Cell]] = self._build_board()
        self.status = GameStatus.ACTIVE.value
        self.moves = 0
        self._place_bombs()
        self._calculate_adjacent_mines()

    def _build_board(self) -> List[List[Cell]]:
        return [
            [Cell(row=row, col=col) for col in range(self.width)]
            for row in range(self.height)
        ]

    def _place_bombs(self) -> None:
        remaining = self.mine_count
        while remaining > 0:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)
            cell = self.board[row][col]
            if not cell.bomb:
                cell.bomb = True
                remaining -= 1

    def _calculate_adjacent_mines(self) -> None:
        for row in self.board:
            for cell in row:
                if not cell.bomb:
                    cell.calc_adj_mines(self)

    def reveal(self, row: int, col: int) -> bool:
        """Reveal a cell. Returns True if a bomb was hit."""
        if not (0 <= row < self.height and 0 <= col < self.width):
            return False
        if self.status != GameStatus.ACTIVE.value:
            return False

        cell = self.board[row][col]
        hit_bomb = cell.reveal(self)
        self.moves += 1

        if hit_bomb:
            self.status = GameStatus.LOST.value
            self.reveal_all()
            return True

        if self._check_win():
            self.status = GameStatus.WON.value

        return False

    def toggle_flag(self, row: int, col: int) -> bool:
        """Toggle a flag on a hidden cell."""
        if not (0 <= row < self.height and 0 <= col < self.width):
            return False
        if self.status != GameStatus.ACTIVE.value:
            return False
        return self.board[row][col].flag()

    def reveal_all(self) -> None:
        for row in self.board:
            for cell in row:
                cell.revealed = True

    def _check_win(self) -> bool:
        for row in self.board:
            for cell in row:
                if not cell.bomb and not cell.revealed:
                    return False
        return True

    def bomb_counter(self) -> int:
        flagged = sum(1 for row in self.board for cell in row if cell.flagged)
        return self.mine_count - flagged

    def _face(self) -> str:
        if self.status == GameStatus.LOST.value:
            return "☹"
        if self.status == GameStatus.WON.value:
            return "😎"
        return "🙂"

    def _cell_display(self, cell: Cell, reveal_mines: bool = False) -> str:
        if cell.flagged and not cell.revealed:
            return "🚩"
        if cell.revealed:
            if cell.bomb:
                return "💣"
            if cell.adjacent_mines == 0:
                return " "
            return str(cell.adjacent_mines)
        if reveal_mines and cell.bomb:
            return "💣"
        return "■"

    def render_board(self, reveal_mines: bool = False) -> str:
        """Render a board view suitable for GitHub comments."""
        status_line = (
            f"╔════════════════════════════════════╗\n"
            f"║ Bombs: {self.bomb_counter():03d}   Face: {self._face()}   Moves: {self.moves:03d} ║\n"
            f"╚════════════════════════════════════╝"
        )

        header = "   " + " ".join(f"{col:>2}" for col in range(self.width))
        rows = [header]
        for row_idx, row in enumerate(self.board):
            rendered_cells = [self._cell_display(cell, reveal_mines=reveal_mines) for cell in row]
            rows.append(f"{row_idx:>2} " + "  ".join(f"{cell:>1}" for cell in rendered_cells))

        return "\n".join([status_line, "", "```", *rows, "```"])

    def get_state(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "mine_count": self.mine_count,
            "status": self.status,
            "moves": self.moves,
            "board": [[cell.to_dict() for cell in row] for row in self.board],
        }

    @classmethod
    def from_state(cls, state: dict) -> "Minesweeper":
        game = cls(state["width"], state["height"], state["mine_count"])
        game.status = state.get("status", GameStatus.ACTIVE.value)
        game.moves = state.get("moves", 0)

        board_state = state.get("board", [])
        game.board = []
        for row_idx, row in enumerate(board_state):
            board_row = []
            for col_idx, cell_data in enumerate(row):
                board_row.append(Cell.from_dict(cell_data, row_idx, col_idx))
            game.board.append(board_row)

        # If the file contains an older or truncated state, rebuild a clean board.
        if not game.board or len(game.board) != game.height:
            return cls(game.width, game.height, game.mine_count)

        return game


if __name__ == "__main__":
    game = Minesweeper(8, 8, 10)
    game.reveal(0, 0)
    print(game.render_board())
    print(f"Status: {game.status}")
