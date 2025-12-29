def prover9_proved(output: str) -> bool:
    """Check if Prover9 output contains 'THEOREM PROVED'."""
    return "THEOREM PROVED" in output

def mace4_model_found(output: str) -> bool:
    """Check if Mace4 found a model (consistent)."""
    # Mace4 output varies by version; accept common success markers.
    markers = (
        "Model 1",
        "MODEL 1",
        "MODEL",
        "Exiting with 1 model",
        "Exiting with 1 models",
        "exiting with 1 model",
        "exiting with 1 models",
        "Satisfiable",
        "satisfiable",
    )
    return any(marker in output for marker in markers)
