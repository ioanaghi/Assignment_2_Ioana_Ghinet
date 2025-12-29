from typing import Set, Tuple, List


class GameState:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines  # Set of (r,c) tuples
        self.revealed: Set[Tuple[int, int]] = set()

    def neighbors(self, r, c) -> List[Tuple[int, int]]:
        neighs = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighs.append((nr, nc))
        return neighs

    def clue_number(self, r, c) -> int:
        # Calculate clue based on ground truth mines
        count = 0
        for nr, nc in self.neighbors(r, c):
            if (nr, nc) in self.mines:
                count += 1
        return count

    def reveal(self, r, c) -> int:
        self.revealed.add((r, c))
        return self.clue_number(r, c)