from __future__ import annotations

from collections import deque
import random
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional


BOMB_IMAGE = "💣"
FLAG_IMAGE = "🚩"
WRONG_BOMB_IMAGE = "❌"
SMILE_FACE = "🙂"
DEAD_FACE = "☹"
COOL_FACE = "😎"
BOARD_BOMB = "*"
BOARD_FLAG = "⚑"
BOARD_WRONG_FLAG = "X"
BOARD_HIDDEN = "□" 
BOARD_EMPTY = " "
CELL_WIDTH = 3

SIZE_LOOKUP = {
    9: {"totalBombs": 10, "tableWidth": "245px"},
    16: {"totalBombs": 40, "tableWidth": "420px"},
    30: {"totalBombs": 160, "tableWidth": "794px"},
}

COLORS = [
    "",
    "#0000FA",
    "#4B802D",
    "#DB1300",
    "#202081",
    "#690400",
    "#457A7A",
    "#1B1B1B",
    "#7A7A7A",
]


class CellState(Enum):
    HIDDEN = "hidden"
    REVEALED = "revealed"
    FLAGGED = "flagged"


class GameStatus(Enum):
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"


@dataclass
class Cell:
    row: int
    col: int
    board: List[List["Cell"]]
    bomb: bool = False
    revealed: bool = False
    flagged: bool = False
    adjBombs: int = 0

    def get_adj_cells(self) -> List["Cell"]:
        adj: List[Cell] = []
        last_row = len(self.board) - 1
        last_col = len(self.board[0]) - 1

        if self.row > 0 and self.col > 0:
            adj.append(self.board[self.row - 1][self.col - 1])
        if self.row > 0:
            adj.append(self.board[self.row - 1][self.col])
        if self.row > 0 and self.col < last_col:
            adj.append(self.board[self.row - 1][self.col + 1])
        if self.col < last_col:
            adj.append(self.board[self.row][self.col + 1])
        if self.row < last_row and self.col < last_col:
            adj.append(self.board[self.row + 1][self.col + 1])
        if self.row < last_row:
            adj.append(self.board[self.row + 1][self.col])
        if self.row < last_row and self.col > 0:
            adj.append(self.board[self.row + 1][self.col - 1])
        if self.col > 0:
            adj.append(self.board[self.row][self.col - 1])

        return adj

    def calc_adj_bombs(self) -> None:
        self.adjBombs = sum(1 for cell in self.get_adj_cells() if cell.bomb)

    def flag(self) -> bool:
        if not self.revealed:
            self.flagged = not self.flagged
            return self.flagged
        return self.flagged

    def reveal(self) -> bool:
        """Reveal the cell. Returns True if a bomb was hit."""
        if self.revealed:
            return False

        self.revealed = True
        return self.bomb


class Minesweeper:
    """Direct translation of the JS Minesweeper game state and logic."""

    def __init__(self, size: int = 9, total_bombs: Optional[int] = None):
        self.size = size
        self.width = size
        self.height = size
        self.total_bombs = total_bombs if total_bombs is not None else SIZE_LOOKUP[size]["totalBombs"]
        self.table_width = SIZE_LOOKUP[size]["tableWidth"]
        self.board: List[List[Cell]] = []
        self.status = "active"
        self.bombCount = 0
        self.timeElapsed = 0
        self.adjBombs = None
        self.hitBomb = False
        self.elapsedTime = 0
        self.timerId = None
        self.winner = False
        self._mines_placed = False
        self._build_table()
        self.board = self._build_arrays()
        self._build_cells()
        self.bombCount = self.total_bombs

    def _build_arrays(self) -> List[List[Cell]]:
        arr: List[List[Optional[Cell]]] = [[None for _ in range(self.size)] for _ in range(self.size)]
        return arr  # type: ignore[return-value]

    def _build_cells(self) -> None:
        for row_idx, row_arr in enumerate(self.board):
            for col_idx, _ in enumerate(row_arr):
                self.board[row_idx][col_idx] = Cell(row_idx, col_idx, self.board)

    def _safe_zone(self, row: int, col: int) -> set[tuple[int, int]]:
        safe_zone = {(row, col)}
        for adj_row in range(max(0, row - 1), min(self.size, row + 2)):
            for adj_col in range(max(0, col - 1), min(self.size, col + 2)):
                safe_zone.add((adj_row, adj_col))
        return safe_zone

    def _place_bombs(self, safe_row: int, safe_col: int) -> None:
        if self._mines_placed:
            return

        safe_zone = self._safe_zone(safe_row, safe_col)
        available_cells = [
            cell
            for row in self.board
            for cell in row
            if (cell.row, cell.col) not in safe_zone
        ]

        if self.total_bombs > len(available_cells):
            raise ValueError("Not enough cells to place mines while preserving the first-click safe zone")

        for cell in random.sample(available_cells, self.total_bombs):
            cell.bomb = True

        self.run_code_for_all_cells(lambda cell: cell.calc_adj_bombs())
        self._mines_placed = True

    def _build_table(self) -> None:
        # Kept for structural parity with the JS version; the CLI uses render().
        return None

    def run_code_for_all_cells(self, cb: Callable[[Cell], None]) -> None:
        for row_arr in self.board:
            for cell in row_arr:
                cb(cell)

    def set_timer(self) -> None:
        # No background timer in the CLI implementation; kept for parity.
        self.elapsedTime += 1
        self.timeElapsed = self.elapsedTime

    def reveal_all(self) -> None:
        for row_arr in self.board:
            for cell in row_arr:
                cell.revealed = True

    def get_bomb_count(self) -> int:
        count = 0
        for row in self.board:
            count += sum(1 for cell in row if cell.bomb)
        return count

    def get_winner(self) -> bool:
        for row in self.board:
            for cell in row:
                if not cell.revealed and not cell.bomb:
                    return False
        return True

    def _flood_reveal(self, row: int, col: int) -> bool:
        queue = deque([self.board[row][col]])

        while queue:
            cell = queue.popleft()
            if cell.revealed or cell.flagged:
                continue

            hit_bomb = cell.reveal()
            if hit_bomb:
                return True

            if cell.adjBombs == 0:
                for adj_cell in cell.get_adj_cells():
                    if not adj_cell.revealed and not adj_cell.flagged:
                        queue.append(adj_cell)

        return False

    def reveal(self, row: int, col: int) -> bool:
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        if self.winner or self.hitBomb:
            return False

        cell = self.board[row][col]
        if cell.revealed or cell.flagged:
            return False

        if not self._mines_placed:
            self._place_bombs(row, col)

        hit_bomb = self._flood_reveal(row, col)
        if hit_bomb:
            self.hitBomb = True
            self.status = GameStatus.LOST.value
            self.reveal_all()
        else:
            self.winner = self.get_winner()
            if self.winner:
                self.status = GameStatus.WON.value
        return hit_bomb

    def toggle_flag(self, row: int, col: int) -> bool:
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        if self.winner or self.hitBomb:
            return False

        cell = self.board[row][col]
        if cell.revealed:
            return False

        new_flagged = cell.flag()
        self.bombCount += -1 if new_flagged else 1
        return new_flagged

    def _display_cell(self, cell: Cell, reveal_mines: bool = False) -> str:
        if reveal_mines:
            if cell.bomb:
                return BOARD_BOMB
            if cell.flagged:
                return BOARD_WRONG_FLAG
            if cell.revealed and cell.adjBombs:
                return str(cell.adjBombs)
            if cell.revealed:
                return BOARD_EMPTY
            return BOARD_HIDDEN

        if cell.flagged:
            return BOARD_FLAG
        if cell.revealed:
            if cell.bomb:
                return BOARD_BOMB
            if cell.adjBombs:
                return str(cell.adjBombs)
            return BOARD_EMPTY
        return BOARD_HIDDEN

    def _format_cell(self, cell: Cell, reveal_mines: bool = False) -> str:
        return f"{self._display_cell(cell, reveal_mines):^{CELL_WIDTH}}"

    def _board_header(self) -> str:
        columns = "|".join(f"{idx:^{CELL_WIDTH}}" for idx in range(self.size))
        return f"    |{columns}|"

    def _board_separator(self) -> str:
        return f"----+{'+'.join('-' * CELL_WIDTH for _ in range(self.size))}+"

    def _render_board_rows(self, reveal_mines: bool = False) -> List[str]:
        lines = [self._board_header(), self._board_separator()]
        for row_idx, row in enumerate(self.board):
            rendered = "|".join(self._format_cell(cell, reveal_mines) for cell in row)
            lines.append(f"{row_idx:>3} |{rendered}|")
            lines.append(self._board_separator())
        return lines

    def render(self) -> str:
        bomb_counter = str(self.bombCount).zfill(3)
        face = SMILE_FACE
        if self.hitBomb:
            face = DEAD_FACE
        elif self.winner:
            face = COOL_FACE

        lines = [
            "╔════════════════════════════════════╗",
            f"║ Bombs: {bomb_counter}   Face: {face}   Moves: {str(self.elapsedTime).zfill(3)} ║",
            "╚════════════════════════════════════╝",
            "",
            "```",
        ]
        lines.extend(self._render_board_rows())
        lines.append("```")

        if self.hitBomb:
            lines.append("")
            lines.append("💥 **GAME OVER!** You hit a mine! 💥")

        elif self.winner:
            lines.append("")
            lines.append("🎉 **YOU WON!** 🎉")

        return "\n".join(lines)

    def render_board(self, reveal_mines: bool = False) -> str:
        if not reveal_mines:
            return self.render()

        bomb_counter = str(self.bombCount).zfill(3)
        lines = [
            "╔════════════════════════════════════╗",
            f"║ Bombs: {bomb_counter}   Face: {DEAD_FACE}   Moves: {str(self.elapsedTime).zfill(3)} ║",
            "╚════════════════════════════════════╝",
            "",
            "```",
        ]
        lines.extend(self._render_board_rows(reveal_mines=True))
        lines.append("```")
        lines.append("")
        lines.append("💥 **GAME OVER!**")
        return "\n".join(lines)

    def get_state(self) -> dict:
        return {
            "size": self.size,
            "width": self.width,
            "height": self.height,
            "total_bombs": self.total_bombs,
            "mine_count": self.total_bombs,
            "bombCount": self.bombCount,
            "timeElapsed": self.timeElapsed,
            "moves": self.elapsedTime,
            "adjBombs": self.adjBombs,
            "hitBomb": self.hitBomb,
            "elapsedTime": self.elapsedTime,
            "timerId": self.timerId,
            "winner": self.winner,
            "status": self.status,
            "minesPlaced": self._mines_placed,
            "board": [[cell_to_state(cell) for cell in row] for row in self.board],
        }

    @classmethod
    def from_state(cls, state: dict) -> "Minesweeper":
        size = state.get("size", state.get("width", 16))
        total_bombs = state.get("total_bombs", state.get("mine_count", SIZE_LOOKUP.get(size, SIZE_LOOKUP[16])["totalBombs"]))
        game = cls(size=size, total_bombs=total_bombs)
        game.bombCount = state.get("bombCount", game.get_bomb_count())
        game.timeElapsed = state.get("timeElapsed", 0)
        game.adjBombs = state.get("adjBombs")
        game.hitBomb = state.get("hitBomb", False)
        game.elapsedTime = state.get("elapsedTime", game.timeElapsed)
        game.timerId = state.get("timerId")
        game.winner = state.get("winner", False)
        game.status = state.get("status", "lost" if game.hitBomb else "won" if game.winner else "active")

        board_state = state.get("board")
        if board_state:
            game.board = []
            for row_idx, row in enumerate(board_state):
                board_row = []
                for col_idx, cell_state in enumerate(row):
                    cell = Cell.from_state(cell_state, row_idx, col_idx, game.board if game.board else [])
                    board_row.append(cell)
                game.board.append(board_row)
            for row in game.board:
                for cell in row:
                    cell.board = game.board
            game._mines_placed = state.get("minesPlaced", any(cell.bomb for row in game.board for cell in row))
        return game


def cell_to_state(cell: Cell) -> dict:
    return {
        "row": cell.row,
        "col": cell.col,
        "bomb": cell.bomb,
        "revealed": cell.revealed,
        "flagged": cell.flagged,
        "adjBombs": cell.adjBombs,
        "adjacent_mines": cell.adjBombs,
    }


# Patch Cell.from_state signature after class definition for readability.
def _cell_from_state(cls, data: dict, row: int, col: int, board: List[List[Cell]]) -> Cell:
    cell = cls(row=row, col=col, board=board or [], bomb=data.get("bomb", False))
    cell.revealed = data.get("revealed", False)
    cell.flagged = data.get("flagged", False)
    cell.adjBombs = data.get("adjBombs", data.get("adjacent_mines", 0))
    return cell


Cell.from_state = classmethod(_cell_from_state)  # type: ignore[attr-defined]


if __name__ == "__main__":
    game = Minesweeper()
    game.reveal(0, 0)
    print(game.render())
