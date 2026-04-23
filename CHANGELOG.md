# Changelog

## 0.2.0 (2026-04-23)

### Added

- **Phase 2.A input adapters** in `agent_ready/adapters/`:
  - `text.plan_from_text(raw)` — scan any raw log / JSONL / JSON for missing-capability signals.
  - `trace_eval.plan_from_trace_eval_json(scorecard)` — consume real trace-eval v0.5.0 scorecard JSON output.
  - `trace_eval.plan_from_trace_eval_with_trace(scorecard, trace_path)` — higher precision: scorecard + raw trace combined.
  - `patterns.load_patterns()` / `match_patterns(text)` — shared regex catalog scanner.
- **CLI auto-detection** on `agent-ready detect --from <path>` / stdin — recognizes trace-eval scorecard vs synthetic diagnose vs raw text.
- `mapper.plan_from_pattern_hits(hits)` — single capability-resolution path shared across every adapter.
- `docs/INTEGRATION.md` — honest accounting of how agent-ready relates to trace-eval v0.5.0, including known recall limits of the scorecard adapter.
- 13 new tests covering the adapters and auto-detection.

### Changed

- `agent_ready.__init__` now re-exports adapter and public API symbols.
- `schema/trace.v1.json` and `schema/error-patterns.v1.json` description text corrected — neither is "mirrored from trace-eval"; `error-patterns.v1.json` is canonical in agent-ready, `trace.v1.json` is a simplified internal input shape (distinct from trace-eval's real scorecard format).
- `schema/README.md` rewritten to reflect the actual ownership of each file.
- CI schema-mirror check replaced with schema-invariant check (unique pattern IDs, non-empty capability `plain_english`).

### Fixed

- The fictional "mirrored from trace-eval" banners that misrepresented the real integration relationship with trace-eval v0.5.0.

## 0.1.0 (2026-04-22)

### Added

- Phase 1 scaffold: docs reorganized under `docs/`, capability registry (5 capabilities), mapper (`plan_from_diagnose`, `plan_from_task`), plan rendering (human + JSON), dataclass models.
- `detect` CLI with `--task` / `--from` modes; `fix` / `verify` / `undo` intentionally stubbed pending security review.
- Schema contracts: `capability.v1.json` (JSON-Schema), `capabilities.v1.json` (registry data), `error-patterns.v1.json` (catalog), `trace.v1.json` (internal input shape — draft).
- Hygiene: `CONTRIBUTING.md` with mandatory safety-review block, `LICENSE` (MIT), `NOW.md`, expanded `AGENTS.md`, `EXAMPLES.md`, `ROADMAP.md`, `AGENT_INTERFACE.md`.
- `.github/` hygiene: CI (ruff + pytest + schema + build), bug & capability-gap issue templates, PR template, `CODEOWNERS`.
- `.git-hooks/pre-commit` blocking internal docs, secrets, and registry quality checks.
- 28 tests.
