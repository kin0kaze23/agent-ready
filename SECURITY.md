# Security Policy

> `agent-ready` installs software, handles authentication flows, and writes configuration on your machine. This document explains how we protect you.

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | ✅ Yes |
| < 0.2   | ❌ No |

---

## Reporting a Vulnerability

If you find a security issue, please report it **privately** by emailing the maintainer or opening a [GitHub Security Advisory](https://github.com/kin0kaze23/agent-ready/security).

Do **not** open a public issue for security vulnerabilities.

You can expect:
- A response within 48 hours.
- An assessment within 7 days.
- A fix or mitigation plan within 30 days for critical issues.

---

## Security Model

`agent-ready fix` runs installers on your machine. Because this is inherently high-risk, we enforce multiple layers of protection:

### 1. Approval Required

- **Per-capability approval.** One "yes" covers all steps for that capability only — never a blanket "yes to everything."
- **Dry-run first.** `agent-ready fix --dry-run` shows you exactly what will happen before anything runs.
- **Plain-English prompts.** You see what the tool will do, not raw commands.

### 2. Credential Safety

- **We never store credentials.** API keys, tokens, and passwords go to the tool's own native store (OS keychain, `.env`, or the tool's config).
- **We never read credentials back.** Once a tool stores its own credential, `agent-ready` has no access to it.
- **Credentials never appear in logs, output, or error messages.**

### 3. Sudo Policy

- **Never automatic sudo.** If a step requires system-level access, we show you the command and you run it yourself.
- **User-scope installs preferred.** Most tools install without elevated permissions (Homebrew, `pip --user`, `npm --prefix`).

### 4. Network Install Safety

- **No `curl | sh` installers.** We never pipe a network URL directly into a shell.
- **Package managers preferred.** Homebrew, npm, pip, apt — all have built-in integrity checks.
- **If a script is unavoidable:** we download it first, show you the contents and source URL, and require explicit approval before running.

### 5. Rollback

- **Every install has an undo.** `agent-ready undo <capability>` reverses what was installed.
- **Verify after install.** We never report success based on a return code alone — we run a verification check.
- **Interruption recovery.** If you stop an install mid-way, we save state so you can resume or undo cleanly.

### 6. Sandboxing

- **Controlled subshell execution.** Installers run in a subprocess with a restricted environment (no inherited secrets) and a timeout.
- **No container (yet).** The tools need to live on your actual machine, not in an isolated environment. We compensate with the safeguards above.

For the full technical review with implementation sketches, see the security review PR (#3). Once merged, the document will live at [docs/SECURITY_REVIEW.md](docs/SECURITY_REVIEW.md).

---

## What We Do NOT Do

- We do not collect telemetry by default. (Opt-in only, Phase 2.)
- We do not send any data to external servers beyond what the installers themselves require.
- We do not modify system files outside the installer's own scope.
- We do not store any state in the repo or in agent-ready's own files beyond a temporary recovery state file.

---

## Dependency Security

`agent-ready` has zero runtime dependencies. There are no third-party packages to audit. The only dependencies are:
- **Python 3.11+** (system requirement)
- **pytest and ruff** (dev-only, not installed for end users)

---

## Code Signing

Releases are not yet code-signed. This is planned for a future release once the package is distributed via PyPI.
