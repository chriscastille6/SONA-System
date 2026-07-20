"""Synthetic-data tests for the CANDIDATE linking protocol."""

from __future__ import annotations

import pytest

from apps.compliance.candidate.protocol import (
    generate_candidate_id,
    is_valid_candidate_id,
    merge_waves_by_candidate_id,
    normalize_answer,
)


def test_normalize_strips_and_lowercases():
    assert normalize_answer("  Mj ") == "mj"
    assert normalize_answer("Oak St.") == "oakst"


def test_generate_candidate_id_is_16_hex_and_stable():
    a = generate_candidate_id("MJ", 14, "OA")
    b = generate_candidate_id("mj", "14", "oa")
    c = generate_candidate_id("MJ", "07", "OA")
    d = generate_candidate_id("MJ", 7, "OA")
    assert a == b
    assert c == d
    assert is_valid_candidate_id(a)
    assert len(a) == 16
    assert a != c


def test_birth_day_bounds():
    with pytest.raises(ValueError):
        generate_candidate_id("MJ", 0, "OA")
    with pytest.raises(ValueError):
        generate_candidate_id("MJ", 32, "OA")


def test_merge_waves_links_on_candidate_id_only():
    cid = generate_candidate_id("AB", 3, "CD")
    w1 = [{"candidate_id": cid, "wave": 1, "responses": {"focus_1": 4}}]
    w2 = [{"candidate_id": cid, "wave": 2, "responses": {"focus_1": 5}}]
    merged = merge_waves_by_candidate_id(w1, w2)
    assert len(merged) == 1
    assert merged[0]["linked"] is True
    assert merged[0]["wave1"]["responses"]["focus_1"] == 4
    assert merged[0]["wave2"]["responses"]["focus_1"] == 5


def test_merge_rejects_email_bridge():
    cid = generate_candidate_id("XY", 11, "ZZ")
    w1 = [{"candidate_id": cid, "email": "participant.demo@example.edu"}]
    with pytest.raises(ValueError, match="re-identification"):
        merge_waves_by_candidate_id(w1, [])


def test_merge_rejects_survey_code_bridge():
    cid = generate_candidate_id("XY", 11, "ZZ")
    w1 = [{"candidate_id": cid, "survey_code": "SYNTHETIC123"}]
    with pytest.raises(ValueError, match="re-identification"):
        merge_waves_by_candidate_id(w1, [])
