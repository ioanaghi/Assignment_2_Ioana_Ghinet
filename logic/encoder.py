from __future__ import annotations
from typing import List, Tuple
from itertools import combinations


def cell_const(r: int, c: int) -> str:
    return f"c{r}_{c}"


def clause_or(lits: List[str]) -> str:
    return " | ".join(lits) + "."


def neg_mine(x: str) -> str:
    return f"-Mine({x})"


def pos_mine(x: str) -> str:
    return f"Mine({x})"


def domain_axioms(rows: int, cols: int) -> str:
    cells = [cell_const(r, c) for r in range(rows) for c in range(cols)]

    # Domain Closure: all x (x=c0_0 | x=c0_1 | ...).
    # This tells Prover9 there are no other cells in the universe.
    closure = "all x (" + " | ".join([f"x={c}" for c in cells]) + ")."

    # We implicitly rely on Prover9 treating distinct string constants as distinct objects
    # unless forced otherwise. For rigorous FOL, we might add distinctness axioms,
    # but for these grid sizes, closure is usually sufficient combined with the finite domain settings.
    return closure


def exactly_k_mines(neigh: List[str], k: int) -> List[str]:
    """
    Encode "exactly k of neigh are mines".
    Standard CNF encoding for cardinality constraints.
    """
    m = len(neigh)
    out = []

    # Impossible cases
    if k < 0:
        out.append("False.")
        return out
    if k > m:
        out.append("False.")
        return out

    # 1. AtMostK: For every subset of size k+1, at least one is NOT a mine.
    #    (If k+1 were mines, we'd have too many).
    if k < m:
        for subset in combinations(neigh, k + 1):
            # Clause: -Mine(x1) | -Mine(x2) | ...
            out.append(clause_or([neg_mine(x) for x in subset]))

    # 2. AtLeastK: For every subset of size m-k+1, at least one IS a mine.
    #    (If m-k+1 were safe, we'd have only k-1 left for mines, which is too few).
    #    Example: 3 neighbors, K=1. Size=3. Subset {A,B,C}. Clause: Mine(A)|Mine(B)|Mine(C).
    if k > 0:
        size = m - k + 1
        for subset in combinations(neigh, size):
            out.append(clause_or([pos_mine(x) for x in subset]))

    return out


def state_axioms(game) -> str:
    lines = []

    # 1. Domain definition
    lines.append(domain_axioms(game.rows, game.cols))

    # 2. Add knowledge from REVEALED cells
    for (r, c) in game.revealed:
        x = cell_const(r, c)

        # Fact: Revealed cells are Safe (Not Mines)
        lines.append(f"-Mine({x}).")

        # Constraint: The number of mines in neighbors equals the clue
        k = game.clue_number(r, c)
        neigh_cells = game.neighbors(r, c)
        neigh_consts = [cell_const(rr, cc) for (rr, cc) in neigh_cells]

        lines.extend(exactly_k_mines(neigh_consts, k))

    return "\n".join(lines)