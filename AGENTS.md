# agent-ready — Agent Rules

> For AI agents working on this repo.

## Repo Hygiene

- **No internal working documents in the repo.** Sprint notes, planning docs, AI assistant notes stay local.
- **Only these `.md` files at root:** README.md, CONTRIBUTING.md, LICENSE.
- **All other docs go in `docs/`.**
- **Never commit:** dist/, build/, __pycache__/, .venv/, .DS_Store, *.egg-info/.
- **Never commit secrets or credentials.**

## Development

- Use `python -m build` to create distributions.
- Use `pip install -e .` for local development.
- Tests: `pytest tests/ -q`
- This repo borrows the pre-commit hook pattern from trace-eval.
