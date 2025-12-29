from flask import Flask, render_template, jsonify, request
from game.state import GameState
from game.generator import generate_game
from game.hints import find_hint
from logic.runner import prove_safe, mace_consistent

app = Flask(__name__)

current_game: GameState | None = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/new_game', methods=['POST'])
def new_game():
    global current_game
    data = request.json
    difficulty = data.get('difficulty', 'easy')

    if difficulty == 'hard':
        rows, cols, mines = 7, 7, 12  # Slightly adjusted for balance
    elif difficulty == 'medium':
        rows, cols, mines = 6, 6, 6
    else:  # easy
        rows, cols, mines = 5, 5, 3

    current_game = generate_game(rows, cols, mines)

    # Convert revealed set to list for JSON
    revealed_list = []
    for (r, c) in current_game.revealed:
        revealed_list.append({
            "r": r,
            "c": c,
            "clue": current_game.clue_number(r, c)
        })

    return jsonify({
        "status": "ok",
        "rows": rows,
        "cols": cols,
        "mines_total": mines,
        "revealed": revealed_list
    })


@app.route('/api/click', methods=['POST'])
def click_cell():
    global current_game
    if not current_game:
        return jsonify({"error": "No game started"}), 400

    data = request.json
    r, c = int(data.get('r')), int(data.get('c'))

    if (r, c) in current_game.revealed:
        return jsonify({"status": "already_revealed"})

    # LOGIC CHECK: Can we prove it is Safe?
    # We ignore the logic check if the game is somehow in an invalid state,
    # but strictly per requirements: "cannot go in cells for which Prover9 fails"
    is_safe_proven, output = prove_safe(current_game, r, c)

    if is_safe_proven:
        clue = current_game.reveal(r, c)
        return jsonify({
            "status": "safe",
            "clue": clue,
            "r": r, "c": c
        })
    else:
        # Check if it was actually safe (ground truth) just for debugging/message
        # But we MUST block the move.
        return jsonify({
            "status": "blocked",
            "message": "Move blocked! Prover9 could not prove this cell is safe."
        })


@app.route('/api/hint', methods=['POST'])
def get_hint():
    global current_game
    if not current_game:
        return jsonify({"error": "No game started"}), 400

    # Logic-based hint
    hint = find_hint(current_game)
    return jsonify(hint)


@app.route('/api/check', methods=['POST'])
def check_consistency():
    global current_game
    if not current_game:
        return jsonify({"error": "No game started"}), 400

    is_consistent, _ = mace_consistent(current_game)
    return jsonify({"consistent": is_consistent})


if __name__ == '__main__':
    app.run(debug=True, port=5000)