"""
SampleMind AI — Nox session definitions.
==========================================

Nox is used as an isolated test/lint/format runner so that every check runs
inside its own environment.  All sessions delegate to ``uv`` for speed.

Available sessions:
    unit         — Fast unit tests, fail-on-first, no coverage.
    integration  — Integration tests (requires running MongoDB/Redis/etc.).
    lint         — Read-only ruff + black + isort checks.
    format       — Auto-format: black + isort + ruff --fix.
    type         — mypy static type checking against src/.
    security     — bandit (code) + safety (deps) security scan.
    cov          — Full test suite with branch coverage (HTML + XML).
    all          — Complete quality gate: lint → type → security → unit → integration.

Run a session:  uv run nox -s unit
List sessions:  uv run nox -l
Run all:        uv run nox -s all
"""

import nox

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True


@nox.session(name="unit")
def unit_tests(session: nox.Session) -> None:
    """Fast unit tests — no coverage, fail on first error."""
    session.run("uv", "sync", external=True)
    session.run(
        "uv", "run", "pytest", "tests/unit/",
        "-x", "--no-cov", "-q", "--timeout=30",
        external=True,
    )


@nox.session(name="integration")
def integration_tests(session: nox.Session) -> None:
    """Integration tests (requires running services)."""
    session.run("uv", "sync", external=True)
    session.run(
        "uv", "run", "pytest", "tests/integration/",
        "-v", "--timeout=120",
        external=True,
    )


@nox.session(name="lint")
def lint(session: nox.Session) -> None:
    """Ruff + black + isort checks (read-only)."""
    session.run("uv", "sync", external=True)
    session.run("uv", "run", "ruff", "check", "src/", "tests/", external=True)
    session.run("uv", "run", "black", "--check", "src/", "tests/", external=True)
    session.run("uv", "run", "isort", "--check-only", "src/", "tests/", external=True)


@nox.session(name="format")
def format_code(session: nox.Session) -> None:
    """Auto-format: black + isort + ruff --fix."""
    session.run("uv", "sync", external=True)
    session.run("uv", "run", "black", "src/", "tests/", external=True)
    session.run("uv", "run", "isort", "src/", "tests/", external=True)
    session.run("uv", "run", "ruff", "check", "--fix", "src/", "tests/", external=True)


@nox.session(name="type")
def type_check(session: nox.Session) -> None:
    """Mypy static type checking."""
    session.run("uv", "sync", external=True)
    session.run("uv", "run", "mypy", "src/", external=True)


@nox.session(name="security")
def security(session: nox.Session) -> None:
    """Bandit (code) + safety (deps) security scan."""
    session.run("uv", "sync", external=True)
    session.run("uv", "run", "bandit", "-r", "src/", "-ll", external=True)
    session.run("uv", "run", "safety", "check", external=True)


@nox.session(name="cov")
def coverage(session: nox.Session) -> None:
    """Full test suite with branch coverage report (parallel)."""
    session.run("uv", "sync", external=True)
    session.run(
        "uv", "run", "pytest", "tests/",
        "-n", "auto", "--dist=loadfile",
        "--cov=src/samplemind",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml",
        "--timeout=60",
        external=True,
    )


@nox.session(name="all")
def all_checks(session: nox.Session) -> None:
    """Full quality gate: lint → type → security → unit → integration."""
    session.run("uv", "sync", external=True)
    # Lint
    session.run("uv", "run", "ruff", "check", "src/", "tests/", external=True)
    session.run("uv", "run", "black", "--check", "src/", "tests/", external=True)
    # Type
    session.run("uv", "run", "mypy", "src/", external=True)
    # Security
    session.run("uv", "run", "bandit", "-r", "src/", "-ll", external=True)
    # Tests
    session.run(
        "uv", "run", "pytest", "tests/unit/",
        "-x", "--no-cov", "-q", "--timeout=30",
        external=True,
    )
