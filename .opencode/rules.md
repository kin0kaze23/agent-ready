# Repo Hygiene Rules — agent-ready

> This is a public repository. Everything committed is visible to the world.

## Rules (same as trace-eval)

1. **No internal working documents** — sprint notes, planning docs, AI assistant notes stay local
2. **Never commit build artifacts** — dist/, build/, __pycache__/, .venv/, .DS_Store
3. **Never commit secrets** — API keys, tokens, passwords
4. **Only README, CONTRIBUTING, LICENSE at root** — all other docs in docs/
5. **Documentation belongs in docs/** — user-facing docs only

## Enforcement

A pre-commit hook (copied from trace-eval) will block internal files.
Install: `cp .git-hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`
