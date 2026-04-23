# Schema — Internal Contracts

Files in this directory define `agent-ready`'s own data shapes.

## Files

| File | Owner | Purpose |
|------|-------|---------|
| `capability.v1.json` | `agent-ready` | JSON-Schema for entries in the capability registry. |
| `capabilities.v1.json` | `agent-ready` | The actual registry — Phase 1 capability list. |
| `error-patterns.v1.json` | `agent-ready` | Regex catalog for missing-capability detection in raw trace text. |
| `trace.v1.json` | `agent-ready` (draft) | **Simplified input format** the mapper consumes today. NOT the real trace-eval output format — see note below. |

## Important: The trace-eval Integration Gap

The real `trace-eval` (v0.5.0) emits a rich scorecard JSON (`total_score`, `dimension_scores`, `friction_flags`, `adapter_capability_report`) — not the simplified shape our `trace.v1.json` declares. Our mapper currently consumes the synthetic shape.

**Phase 2 task:** add `agent_ready/adapters/trace_eval.py` that translates real trace-eval scorecard JSON into our input shape. See [docs/INTEGRATION.md](../docs/INTEGRATION.md).

## Versioning

- `v1.x` — additive only: new capabilities, new optional fields, new error patterns.
- `v2+` — breaking changes. Requires an RFC.
