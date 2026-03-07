# Dependency Upgrade Status

**Phase:** 15 — v3.0 Migration
**Last Updated:** 2026-03-07

---

## pyproject.toml Upgrade Tracking

> **Verified against actual pyproject.toml on 2026-03-07.**
> Some entries in earlier versions of this table were incorrect — the table below reflects real file contents.

| Package | Current (real pyproject.toml) | Target v3.0 | Priority | Status |
|---------|-------------------------------|-------------|----------|--------|
| `anthropic` | `^0.7.0` | `^0.40.0` | P0 Critical | ⏳ Pending |
| `openai` | `^1.3.0` | `^1.58.0` | P0 Critical | ⏳ Pending |
| `google-generativeai` | `^0.3.0` | rename → `google-genai ^0.8.0` | P0 Critical | ⏳ Pending |
| `textual` | `^0.44.0` | `^0.87.0` | P0 Critical | ⏳ Pending |
| `torch` | `^2.1.0` | `^2.5.0` | P1 High | ⏳ Pending |
| `torchaudio` | `^2.1.0` | `^2.5.0` | P1 High | ⏳ Pending |
| `transformers` | `^4.35.0` | `^4.47.0` | P1 High | ⏳ Pending |
| `numpy` | `>=1.26,<2.0.0` | `>=2.0.0` | P1 High | ⏳ Pending |
| `scipy` | `^1.11.4` | `^1.14.0` | P1 High | ⏳ Pending |
| `librosa` | `0.10.1` (exact pin) | `^0.11.0` | P1 High | ⏳ Pending |
| `basic-pitch` | commented out | `^0.4.0` | P1 High | ⏳ Pending |
| `demucs` | **NOT in pyproject.toml** | `^4.0.0` (ADD) | P1 High | ⏳ Pending — must ADD |
| `pedalboard` | **NOT in pyproject.toml** | `^0.9.0` (ADD) | P1 High | ⏳ Pending — must ADD |
| `fastapi` | `^0.104.1` | `^0.115.0` | P2 Medium | ⏳ Pending |
| `uvicorn` | `^0.24.0` | `^0.32.0` | P2 Medium | ⏳ Pending |
| `motor` | `^3.3.1` | `^3.6.0` | P2 Medium | ⏳ Pending |
| `ollama` | `^0.1.7` | `^0.3.0` | P2 Medium | ⏳ Pending |
| `sentence-transformers` | `^2.2.2` | `^3.0.0` | P2 Medium | ⏳ Pending |
| `chromadb` | `>=0.5.0` | `^0.6.0` | P2 Medium | ⏳ Pending |
| `ruff` (dev) | `^0.1.6` | `^0.4.0` | P2 Medium | ⏳ Pending |
| `pytest` (dev) | `^7.4.3` | `^8.0.0` | P2 Medium | ⏳ Pending |
| `python-dotenv` | `^1.0.0` | `^1.0.1` | P3 Low | ⏳ Pending |
| `pydantic` | `^2.5.0` | `^2.10.0` | P3 Low | ⏳ Pending |

---

## Upgrade Order (to minimize conflicts)

1. `scipy ^1.14.0` — unblocks the scipy.signal.hann issue
2. `librosa ^0.11.0` — remove exact pin; after this, delete the `__init__.py` scipy monkey-patch
3. `numpy >=2.0.0` — remove `<2.0.0` cap; do this BEFORE upgrading torch
4. `torch ^2.5.0` + `torchaudio ^2.5.0` + `transformers ^4.47.0` — upgrade all three together
5. `anthropic ^0.40.0` — then migrate `ai_manager.py` to new SDK
6. `openai ^1.58.0` — then migrate `ai_manager.py` to new SDK
7. `google-generativeai` → `google-genai ^0.8.0` — rename package + migrate SDK calls
8. `textual ^0.87.0` — then audit all 13 TUI screens for breaking changes
9. `basic-pitch ^0.4.0` — uncomment in pyproject.toml + install
10. ADD `demucs ^4.0.0` — new dependency
11. ADD `pedalboard ^0.9.0` — new dependency
12. `fastapi ^0.115.0` + `uvicorn ^0.32.0` — upgrade together
13. `motor ^3.6.0` — async MongoDB driver upgrade
14. `chromadb ^0.6.0` — vector DB upgrade

---

## Verification After Each Upgrade

```bash
source .venv/bin/activate
python -c "import samplemind"   # no import errors
make test                        # tests still pass
make quality                     # ruff + mypy + bandit clean
```
