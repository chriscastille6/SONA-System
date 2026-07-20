"""CANDIDATE linking helpers for longitudinal surveys (Sandnes 2021 adaptation)."""

from .protocol import (
    generate_candidate_id,
    is_valid_candidate_id,
    merge_waves_by_candidate_id,
    normalize_answer,
)

__all__ = [
    "generate_candidate_id",
    "is_valid_candidate_id",
    "merge_waves_by_candidate_id",
    "normalize_answer",
]
