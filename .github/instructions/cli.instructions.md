---
applyTo: "src/samplemind/interfaces/cli/**/*.py"
---

# CLI Instructions

- Framework: Typer + Rich for beautiful terminal output
- Main CLI: `interfaces/cli/menu.py` (~2255 lines)
- FAISS search CLI: `interfaces/cli/commands/search.py`
- Use `typer.Option()` with help text for all parameters
- Use Rich panels, tables, and progress bars for output
- Use `Console()` from Rich for styled output
- Group related commands with `typer.Typer()` sub-apps
- Handle Ctrl+C gracefully with `try/except KeyboardInterrupt`
