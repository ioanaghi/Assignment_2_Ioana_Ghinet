from logic.runner import prove_safe, prove_mine


def find_hint(game):
    """
    Scans unrevealed cells.
    1. Try to prove SAFE.
    2. Try to prove MINE.
    Returns the first one found.
    """

    # Prioritize neighbors of revealed cells for efficiency
    candidates = set()
    for (rr, rc) in game.revealed:
        for n in game.neighbors(rr, rc):
            if n not in game.revealed:
                candidates.add(n)

    sorted_candidates = sorted(list(candidates))  # Deterministic order

    # 1. Look for Safe
    for (r, c) in sorted_candidates:
        is_safe, _ = prove_safe(game, r, c)
        if is_safe:
            return {"type": "safe", "r": r, "c": c}

    # 2. Look for Mine
    for (r, c) in sorted_candidates:
        is_mine, _ = prove_mine(game, r, c)
        if is_mine:
            return {"type": "mine", "r": r, "c": c}

    return {"type": "none", "message": "No move found by logic."}