---
name: dependency-management
description: Guide for managing Python and Node.js dependencies. Use when adding, updating, or auditing project dependencies.
---

## Dependency Management

### Python (pyproject.toml)
```bash
# Install all deps (dev)
pip install -e '.[dev]'

# Or with uv
uv sync

# Add new dependency
# Edit pyproject.toml, then: pip install -e '.[dev]'

# Lock deps
uv lock
```

### Node.js (apps/web/package.json)
```bash
cd apps/web

# Install
npm install --legacy-peer-deps

# Add dependency
npm install <package> --legacy-peer-deps

# Update
npm update --legacy-peer-deps
```

### Known Constraints
- Python >=3.12 required
- Node >=22 recommended
- `npm install --legacy-peer-deps` required (peer dep conflicts)
- next-auth: use `5.0.0-beta.31` (not `^5.0.0`)
- next: `15.3.0` has a security advisory — update when patched

### Security
- Run `pip audit` before adding Python deps
- Run `npm audit` before adding Node deps
- Check GitHub Advisory Database for vulnerabilities
- Pin major versions in pyproject.toml
