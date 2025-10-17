"""
Placeholder Bayesian analysis plugin.

This module provides a default compute_bf function that returns a dummy value.
Replace this with your actual Bayesian analysis when ready.
"""
from typing import Dict, Any, Sequence


def compute_bf(responses: Sequence[Dict[str, Any]], params: Dict[str, Any]) -> float:
    """
    Compute Bayes Factor BF10 for the current dataset.
    
    Args:
        responses: List of response payloads (dicts from Response.payload)
        params: Optional parameters (priors, hypothesis identifiers, etc.)
    
    Returns:
        Bayes Factor BF10 (evidence for H1 vs H0)
    
    Example:
        When you replace this placeholder:
        - responses will contain all Response.payload dicts for the study
        - params can be configured in Study admin or passed by the monitoring task
        - Return a float representing BF10
    """
    # TODO: Replace with real Bayesian model
    # For now, simulate increasing BF as sample size grows
    n = len(responses)
    if n < 20:
        return 0.5  # Weak evidence for H0
    elif n < 30:
        return 3.0  # Anecdotal evidence for H1
    elif n < 40:
        return 8.0  # Moderate evidence for H1
    else:
        return 12.0  # Strong evidence for H1 (exceeds threshold)


