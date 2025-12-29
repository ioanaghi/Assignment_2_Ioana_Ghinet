from flask import Flask, jsonify, render_template, request

from game.generator import generate_game
from logic.runner import check_consistency, prove_safe

app = Flask(__name__)

GAME = None
DIFFICULTIES = {
    "easy": (8, 8, 10),
    "medium": (10, 10, 18),
    "hard": (12, 12, 30),
}


def _require_game():
    if GAME is None:
        return jsonify({"error": "No active game."}), 400
    return None


def _pack_revealed(game):
    return [
        {"r": r, "c": c, "clue": clue}
        for (r, c), clue in sorted(game.revealed.items())
    ]


def _pack_mines(game):
    return [{"r": r, "c": c} for r, c in sorted(game.mines)]


def _stop_if_over(game):
    if game.game_over:
        return (
            jsonify(
                {
                    "status": "over",
                    "outcome": game.outcome,
                    "message": "Game is already over.",
                }
            ),
            400,
        )
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/new_game", methods=["POST"])
def new_game():
    data = request.get_json(silent=True) or {}
    diff = data.get("difficulty", "easy")
    rows, cols, mines = DIFFICULTIES.get(diff, DIFFICULTIES["easy"])

    global GAME
    GAME = generate_game(rows, cols, mines)

    return jsonify(
        {
            "rows": GAME.rows,
            "cols": GAME.cols,
            "mines_total": len(GAME.mines),
            "revealed": _pack_revealed(GAME),
        }
    )


@app.route("/api/click", methods=["POST"])
def click_cell():
    if GAME is None:
        return _require_game()
    over = _stop_if_over(GAME)
    if over:
        return over

    data = request.get_json(silent=True) or {}
    r = data.get("r")
    c = data.get("c")

    if r is None or c is None:
        return jsonify({"error": "Missing coordinates."}), 400

    if (r, c) in GAME.revealed:
        return jsonify({"status": "already"})

    if (r, c) in GAME.flags:
        return jsonify({"status": "blocked", "message": "Cell is flagged."})

    guess = bool(data.get("allow_guess"))
    safe, _ = prove_safe(GAME, r, c)
    if not safe and not guess:
        return jsonify(
            {
                "status": "blocked",
                "reason": "not_provable",
                "message": "✨ Logic cannot prove this is safe yet.",
            }
        )

    if (r, c) in GAME.mines:
        GAME.mark_loss()
        return jsonify(
            {
                "status": "boom",
                "message": "Mine hit.",
                "game_over": True,
                "outcome": GAME.outcome,
                "mines": _pack_mines(GAME),
            }
        )

    clue = GAME.reveal(r, c)
    won = GAME.check_win()
    return jsonify(
        {
            "status": "safe",
            "r": r,
            "c": c,
            "clue": clue,
            "game_over": won,
            "outcome": GAME.outcome,
        }
    )


@app.route("/api/flag", methods=["POST"])
def toggle_flag():
    if GAME is None:
        return _require_game()
    over = _stop_if_over(GAME)
    if over:
        return over

    data = request.get_json(silent=True) or {}
    r = data.get("r")
    c = data.get("c")

    if r is None or c is None:
        return jsonify({"error": "Missing coordinates."}), 400

    flagged = GAME.toggle_flag(r, c)
    return jsonify({"r": r, "c": c, "flagged": flagged})


@app.route("/api/hint", methods=["POST"])
def hint():
    if GAME is None:
        return _require_game()
    over = _stop_if_over(GAME)
    if over:
        return over

    safe_cells = []
    for r in range(GAME.rows):
        for c in range(GAME.cols):
            if (r, c) in GAME.revealed or (r, c) in GAME.flags:
                continue
            safe, _ = prove_safe(GAME, r, c)
            if safe:
                safe_cells.append({"r": r, "c": c})

    if safe_cells:
        return jsonify({"type": "safe", "cells": safe_cells})

    return jsonify({"type": "none", "message": "No provably safe cells."})


@app.route("/api/check", methods=["POST"])
def consistency_check():
    if GAME is None:
        return _require_game()
    over = _stop_if_over(GAME)
    if over:
        return over

    consistent, info = check_consistency(GAME)
    if consistent is None:
        return jsonify({"consistent": None, "error": info})
    return jsonify({"consistent": consistent})


if __name__ == "__main__":
    app.run(debug=True)
