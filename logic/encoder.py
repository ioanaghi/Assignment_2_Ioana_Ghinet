import itertools
from typing import Iterable, List, Tuple
from game.state import GameState


def _literal(r: int, c: int, negated: bool = False) -> str:
    atom = f"Mine({r},{c})"
    return f"-{atom}" if negated else atom


def _clause(literals: Iterable[str]) -> str:
    lits = list(literals)
    return f"({' | '.join(lits)})."


def _encode_count(neighbors: List[Tuple[int, int]], count: int) -> List[str]:
    clauses: List[str] = []
    k = len(neighbors)

    if count < 0 or count > k:
        return clauses

    # At least count mines: every subset of size (k - count + 1) has a mine.
    min_subset = k - count + 1
    if 0 < min_subset <= k:
        for subset in itertools.combinations(neighbors, min_subset):
            clauses.append(_clause(_literal(r, c) for r, c in subset))

    # At most count mines: every subset of size (count + 1) has a non-mine.
    max_subset = count + 1
    if 0 < max_subset <= k:
        for subset in itertools.combinations(neighbors, max_subset):
            clauses.append(_clause(_literal(r, c, negated=True) for r, c in subset))

    return clauses


def encode_board(game: GameState) -> List[str]:
    clauses: List[str] = []

    for (r, c), clue in game.revealed.items():
        clauses.append(f"{_literal(r, c, negated=True)}.")
        neighs = game.neighbors(r, c)
        clauses.extend(_encode_count(neighs, clue))

    for (r, c) in sorted(game.flags):
        if (r, c) not in game.revealed:
            clauses.append(f"{_literal(r, c)}.")

    return clauses
