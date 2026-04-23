# Test Fixtures

Synthetic `trace-eval diagnose` payloads used by the test suite. None are real user data.

| File | Purpose |
|------|---------|
| `diagnose_vercel_missing.json` | Single blocker → one-capability Plan |
| `diagnose_multi.json` | Three blockers → multi-capability Plan (dedup, order stable) |
| `diagnose_clean.json` | No errors → empty Plan |
