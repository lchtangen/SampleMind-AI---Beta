"""
TUI Entry Point
Async entry point for the SampleMind Textual application
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .app import SampleMindTUI


async def main():
    """Async entry point for TUI"""
    app = SampleMindTUI()
    await app.run_async()


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
