---
applyTo: "pyproject.toml,uv.lock,package.json,pnpm-workspace.yaml"
---

# Dependency Management Instructions

- Python deps: `pyproject.toml` (v0.3.0, Python >=3.12)
- Python lockfile: `uv.lock`
- Python install: `pip install -e '.[dev]'` or `uv sync`
- Frontend deps: `apps/web/package.json`
- Frontend install: `cd apps/web && npm install --legacy-peer-deps`
- Monorepo: pnpm workspaces (`pnpm-workspace.yaml`)
- Never add deps without checking for security advisories
- Pin major versions in pyproject.toml for stability
- Use `uv` for reproducible Python environments
