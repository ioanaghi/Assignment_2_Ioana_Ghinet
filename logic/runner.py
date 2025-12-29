import subprocess
from typing import List, Tuple

from logic.encoder import encode_board
from logic.parser import prover9_proved, mace4_model_found
from logic.paths import GENERATED_DIR, PROVER9_BIN, MACE4_BIN


def _write_in(filename: str, content: str) -> str:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    path = GENERATED_DIR / filename
    path.write_text(content)
    return str(path)


def _run_bin(binary: str, input_path: str, timeout: int = 5) -> str:
    result = subprocess.run(
        [binary, "-f", input_path],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return (result.stdout or "") + "\n" + (result.stderr or "")


def _p9_input(clauses: List[str], goal: str) -> str:
    lines = ["formulas(sos)."]
    lines.extend(clauses)
    lines.append("end_of_list.")
    lines.append("")
    lines.append("formulas(goals).")
    lines.append(f"{goal}.")
    lines.append("end_of_list.")
    return "\n".join(lines)


def _m4_input(clauses: List[str]) -> str:
    lines = ["formulas(assumptions)."]
    lines.extend(clauses)
    lines.append("end_of_list.")
    return "\n".join(lines)


def prove_safe(game, r: int, c: int) -> Tuple[bool, str]:
    clauses = encode_board(game)
    content = _p9_input(clauses, f"-Mine({r},{c})")
    input_path = _write_in(f"safe_{r}_{c}.in", content)

    try:
        output = _run_bin(PROVER9_BIN, input_path)
        return prover9_proved(output), output
    except Exception as exc:
        return False, str(exc)


def prove_mine(game, r: int, c: int) -> Tuple[bool, str]:
    clauses = encode_board(game)
    content = _p9_input(clauses, f"Mine({r},{c})")
    input_path = _write_in(f"mine_{r}_{c}.in", content)

    try:
        output = _run_bin(PROVER9_BIN, input_path)
        return prover9_proved(output), output
    except Exception as exc:
        return False, str(exc)


def check_consistency(game) -> Tuple[bool, str]:
    clauses = encode_board(game)
    content = _m4_input(clauses)
    input_path = _write_in("consistency.in", content)

    try:
        output = _run_bin(MACE4_BIN, input_path)
        return mace4_model_found(output), output
    except FileNotFoundError as exc:
        return None, str(exc)
    except Exception as exc:
        return False, str(exc)
