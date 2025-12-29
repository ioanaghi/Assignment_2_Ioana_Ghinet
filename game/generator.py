import random
from game.state import GameState


def generate_game(rows: int, cols: int, num_mines: int) -> GameState:
    all_cells = [(r, c) for r in range(rows) for c in range(cols)]

    if num_mines >= len(all_cells):
        num_mines = len(all_cells) - 1

    mine_locs = set(random.sample(all_cells, num_mines))
    game = GameState(rows, cols, mine_locs)

    safe_cells = [p for p in all_cells if p not in mine_locs]
    if safe_cells:
        zeros = [p for p in safe_cells if game.clue_number(p[0], p[1]) == 0]
        if zeros:
            start_r, start_c = random.choice(zeros)
        else:
            start_r, start_c = random.choice(safe_cells)
        game.reveal(start_r, start_c)

    return game
