"""Registry loads, has the Phase 1 set, and every capability has a non-empty plain_english."""

from __future__ import annotations

from agent_ready.registry import by_error_pattern, by_id, load_registry

PHASE_1_IDS = {"vercel_cli", "github_cli", "nodejs", "python", "api_key_config"}


def test_phase_1_capabilities_present():
    registry = load_registry()
    assert PHASE_1_IDS.issubset(set(registry.keys()))


def test_every_capability_has_plain_english():
    for cap in load_registry().values():
        assert cap.plain_english.strip(), f"{cap.id} has empty plain_english"


def test_by_id_roundtrip():
    cap = by_id("vercel_cli")
    assert cap is not None
    assert cap.name == "Vercel CLI"


def test_by_id_unknown_returns_none():
    assert by_id("not_a_real_capability_xyz") is None


def test_by_error_pattern_finds_owners():
    caps = by_error_pattern("cmd_not_found_vercel")
    ids = [c.id for c in caps]
    assert "vercel_cli" in ids
