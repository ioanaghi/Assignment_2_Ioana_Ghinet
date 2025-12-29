def prover9_proved(output: str) -> bool:
    """Check if Prover9 output contains 'THEOREM PROVED'."""
    return "THEOREM PROVED" in output

def mace4_model_found(output: str) -> bool:
    """Check if Mace4 found a model (consistent)."""
    # Mace4 usually outputs "Process ... exit (max_models)" or prints models
    # We look for "Model 1" or explicit exit codes indicating success finding model
    # Simpler check: logic engines usually print "Model 1" when found.
    return "Model 1" in output