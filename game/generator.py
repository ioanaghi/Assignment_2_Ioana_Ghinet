import random
from game.state import GameState


def generate_game(rows, cols, num_mines) -> GameState:
    all_cells = [(r, c) for r in range(rows) for c in range(cols)]

    # Safety check
    if num_mines >= len(all_cells):
        num_mines = len(all_cells) - 1

    mine_locs = set(random.sample(all_cells, num_mines))
    game = GameState(rows, cols, mine_locs)

    # --- CRITICAL: Auto-reveal a safe starting cell ---
    # Without this, the player has 0 information and logic cannot prove anything.
    safe_cells = [p for p in all_cells if p not in mine_locs]

    if safe_cells:
        # Try to find a '0' clue first (easiest start)
        zeros = [p for p in safe_cells if game.clue_number(p[0], p[1]) == 0]

        if zeros:
            start_r, start_c = random.choice(zeros)
        else:
            # Fallback to any safe cell if no zeros exist
            start_r, start_c = random.choice(safe_cells)

        game.reveal(start_r, start_c)

    return game