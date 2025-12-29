import subprocess
import time
from logic.encoder import state_axioms, cell_const
from logic.parser import prover9_proved, mace4_model_found
from logic.paths import (
    PROVER9_BIN, MACE4_BIN, GENERATED_DIR,
    SAFE_TEMPLATE, MINE_TEMPLATE, MACE_TEMPLATE
)


def _ensure_generated_dir():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def _fill_template(template_path, state_text, goal_text=""):
    # Read template fresh every time to avoid caching issues during dev
    with open(template_path, 'r', encoding='utf-8') as f:
        tpl = f.read()
    return tpl.replace("%%STATE_AXIOMS%%", state_text).replace("%%GOAL%%", goal_text)


def _run_tool(binary_path, input_text, timeout=5):
    """
    Runs the binary by piping input_text to stdin.
    """
    try:
        p = subprocess.run(
            [binary_path],
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout
        )
        return p.stdout + "\n" + p.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except FileNotFoundError:
        return f"Error: Binary not found at {binary_path}"


def prove_safe(game, r, c) -> tuple[bool, str]:
    _ensure_generated_dir()
    state = state_axioms(game)
    goal = f"-Mine({cell_const(r, c)})."  # Goal: Prove it is NOT a mine

    in_content = _fill_template(SAFE_TEMPLATE, state, goal)

    # Save file for debugging/logging
    fname = GENERATED_DIR / f"prove_safe_{r}_{c}_{int(time.time())}.in"
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(in_content)

    output = _run_tool(PROVER9_BIN, in_content, timeout=3)  # Short timeout for interactivity
    return prover9_proved(output), output


def prove_mine(game, r, c) -> tuple[bool, str]:
    _ensure_generated_dir()
    state = state_axioms(game)
    goal = f"Mine({cell_const(r, c)})."  # Goal: Prove it IS a mine

    in_content = _fill_template(MINE_TEMPLATE, state, goal)

    fname = GENERATED_DIR / f"prove_mine_{r}_{c}_{int(time.time())}.in"
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(in_content)

    output = _run_tool(PROVER9_BIN, in_content, timeout=3)
    return prover9_proved(output), output


def mace_consistent(game) -> tuple[bool, str]:
    _ensure_generated_dir()
    state = state_axioms(game)

    in_content = _fill_template(MACE_TEMPLATE, state, "")

    fname = GENERATED_DIR / f"mace_check_{int(time.time())}.in"
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(in_content)

    output = _run_tool(MACE4_BIN, in_content, timeout=5)
    return mace4_model_found(output), output