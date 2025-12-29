from typing import Dict, List, Set, Tuple


class GameState:
    def __init__(self, rows: int, cols: int, mines: Set[Tuple[int, int]]):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.revealed: Dict[Tuple[int, int], int] = {}
        self.flags: Set[Tuple[int, int]] = set()
        self.game_over = False
        self.outcome = None  # "win" or "lose"

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        neighs: List[Tuple[int, int]] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc):
                    neighs.append((nr, nc))
        return neighs

    def clue_number(self, r: int, c: int) -> int:
        count = 0
        for nr, nc in self.neighbors(r, c):
            if (nr, nc) in self.mines:
                count += 1
        return count

    def reveal(self, r: int, c: int) -> int:
        clue = self.clue_number(r, c)
        self.revealed[(r, c)] = clue
        if (r, c) in self.flags:
            self.flags.remove((r, c))
        return clue

    def safe_cells_total(self) -> int:
        return self.rows * self.cols - len(self.mines)

    def check_win(self) -> bool:
        if len(self.revealed) >= self.safe_cells_total():
            self.game_over = True
            self.outcome = "win"
            return True
        return False

    def mark_loss(self):
        self.game_over = True
        self.outcome = "lose"

    def toggle_flag(self, r: int, c: int) -> bool:
        if (r, c) in self.revealed:
            return False
        if (r, c) in self.flags:
            self.flags.remove((r, c))
            return False
        self.flags.add((r, c))
        return True
