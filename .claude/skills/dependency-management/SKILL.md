---
name: dependency-management
description: Python (pyproject.toml/uv) and Node.js (npm/--legacy-peer-deps) dependency management
---

## Dependency Management

### Python
- Config: `pyproject.toml` (v0.3.0, Python >=3.12)
- Lockfile: `uv.lock`
- Install: `pip install -e '.[dev]'` or `uv sync`
- Pin major versions for stability
- Check security advisories before adding new deps

### Node.js
- Config: `apps/web/package.json`
- Install: `cd apps/web && npm install --legacy-peer-deps` (required)
- Monorepo: pnpm workspaces (`pnpm-workspace.yaml`)

### Adding Dependencies
```bash
# Python
uv add <package>           # or edit pyproject.toml + uv lock

# Node.js
cd apps/web && npm install <package> --legacy-peer-deps
```

### Security
- Always check for known CVEs before adding new packages
- Keep critical packages updated (fastapi, pydantic, next, react)
- Review transitive dependencies for vulnerabilities
