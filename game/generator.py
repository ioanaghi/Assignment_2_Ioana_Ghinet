import random
from typing import List, Set, Tuple

from game.state import GameState
from logic.runner import prove_safe


def _auto_start(game: GameState, safe_cells: List[Tuple[int, int]]):
    zeros = [p for p in safe_cells if game.clue_number(p[0], p[1]) == 0]
    if zeros:
        start_r, start_c = random.choice(zeros)
    else:
        start_r, start_c = random.choice(safe_cells)
    game.reveal(start_r, start_c)


def _provably_safe_candidates(game: GameState) -> Set[Tuple[int, int]]:
    candidates = set()
    for (rr, rc) in game.revealed:
        for n in game.neighbors(rr, rc):
            if n not in game.revealed and n not in game.flags:
                candidates.add(n)
    return candidates


def _logic_solvable(game: GameState) -> bool:
    safe_total = game.safe_cells_total()

    while len(game.revealed) < safe_total:
        candidates = _provably_safe_candidates(game)
        if not candidates:
            return False

        newly_safe: List[Tuple[int, int]] = []
        for (r, c) in sorted(candidates):
            is_safe, _ = prove_safe(game, r, c)
            if is_safe:
                newly_safe.append((r, c))

        if not newly_safe:
            return False

        for (r, c) in newly_safe:
            game.reveal(r, c)

    return True


def generate_game(rows: int, cols: int, num_mines: int) -> GameState:
    all_cells = [(r, c) for r in range(rows) for c in range(cols)]

    if num_mines >= len(all_cells):
        num_mines = len(all_cells) - 1

    safe_target = len(all_cells) - num_mines
    attempts = 30

    for _ in range(attempts):
        mine_locs = set(random.sample(all_cells, num_mines))
        game = GameState(rows, cols, mine_locs)

        safe_cells = [p for p in all_cells if p not in mine_locs]
        if not safe_cells:
            continue

        _auto_start(game, safe_cells)

        if len(game.revealed) >= safe_target:
            return game

        if _logic_solvable(game):
            return game

    mine_locs = set(random.sample(all_cells, num_mines))
    game = GameState(rows, cols, mine_locs)
    safe_cells = [p for p in all_cells if p not in mine_locs]
    if safe_cells:
        _auto_start(game, safe_cells)
    return game
