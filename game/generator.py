import random
from typing import List, Set, Tuple

from game.state import GameState
from logic.runner import prove_safe


def _auto_start(game: GameState, safe_cells: List[Tuple[int, int]]):
    zeros = [p for p in safe_cells if game.clue(p[0], p[1]) == 0]
    if zeros:
        r, c = random.choice(zeros)
    else:
        r, c = random.choice(safe_cells)
    game.reveal(r, c)


def _cands(game: GameState) -> Set[Tuple[int, int]]:
    out = set()
    for (r, c) in game.revealed:
        for n in game.neigh(r, c):
            if n not in game.revealed and n not in game.flags:
                out.add(n)
    return out


def _can_solve(game: GameState) -> bool:
    need = game.safe_cells_total()
    while len(game.revealed) < need:
        cand = _cands(game)
        if not cand:
            return False
        progress = False
        for r, c in sorted(cand):
            safe, _ = prove_safe(game, r, c)
            if safe:
                game.reveal(r, c)
                progress = True
        if not progress:
            return False
    return True


def generate_game(rows: int, cols: int, num_mines: int) -> GameState:
    all_cells = [(r, c) for r in range(rows) for c in range(cols)]
    if num_mines >= len(all_cells):
        num_mines = len(all_cells) - 1

    while True:
        mine_locs = set(random.sample(all_cells, num_mines))
        game = GameState(rows, cols, mine_locs)
        safe_cells = [p for p in all_cells if p not in mine_locs]
        if not safe_cells:
            continue
        _auto_start(game, safe_cells)

        test = GameState(rows, cols, mine_locs)
        test.revealed = dict(game.revealed)
        test.flags = set(game.flags)

        if _can_solve(test):
            return game
