"""
Chain Recommender Screen (Phase 14 Integration)
"""

import asyncio
from pathlib import Path

from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from samplemind.core.generation.chain_recommender import ChainRecommender
from samplemind.interfaces.tui.widgets.dialogs import ErrorDialog


class ChainScreen(Screen):
    """Screen for Intelligent Chain Generation"""

    DEFAULT_CSS = """
    ChainScreen {
        layout: vertical;
    }

    #controls {
        height: auto;
        padding: 1;
        border-bottom: solid $accent;
    }

    #results_area {
        height: 1fr;
        padding: 1;
    }

    .node-card {
        padding: 1;
        margin: 1;
        border: solid $primary;
        height: auto;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
    ]

    def __init__(self, recommender: ChainRecommender | None = None) -> None:
        super().__init__()
        # If no recommender provided, create one with no explicit library path (will need manual path)
        self.recommender = recommender or ChainRecommender(library_path=None)
        self.seed_path: Path | None = None
        self.chain_result = None

    def compose(self):
        yield Header(show_clock=True)

        with Vertical(id="controls"):
            yield Label("Seed Sample:")
            with Horizontal():
                yield Input(placeholder="Path to seed sample...", id="seed_input")
                yield Button("Browse", id="browse_btn")

            yield Button("🔗 Generate Chain", id="generate_btn", variant="success")

        with ScrollableContainer(id="results_area"):
            yield Static("Select a seed sample and click Generate to build a kit.", id="status_msg")
            yield Vertical(id="chain_display")

        with Horizontal(classes="footer-actions"):
            yield Button("💾 Export Kit", id="export_btn", disabled=True)
            yield Button("⬅️ Back", id="back_btn", variant="error")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_btn":
            self.app.pop_screen()
        elif event.button.id == "generate_btn":
            asyncio.create_task(self._generate_chain())
        elif event.button.id == "browse_btn":
             self.notify("File browser not implemented in this mock", severity="warning")
             # In real impl, push FilePickerScreen
        elif event.button.id == "export_btn":
            self._export_kit()

    async def _generate_chain(self):
        input_val = self.query_one("#seed_input", Input).value
        if not input_val:
             self.notify("Please enter a seed path", severity="error")
             return

        path = Path(input_val)
        if not path.exists():
             self.notify("File does not exist", severity="error")
             return

        self.seed_path = path
        self.query_one("#status_msg").update("Generating chain... (This may take a moment)")

        try:
            # We assume library path is parent of seed for now if not set
            search_paths = [path.parent]

            # Using thread for blocking IO/ML
            # Note: In real app, run in executor
            ctx = self.recommender.build_chain(path, template_name="standard_kit", search_paths=search_paths)
            self.chain_result = ctx

            self._render_results(ctx)
            self.query_one("#export_btn").disabled = False
            self.query_one("#status_msg").update("Chain Generated Successfully!")

        except Exception as e:
            self.app.push_screen(ErrorDialog("Generation Failed", str(e)))

    def _render_results(self, ctx):
        display = self.query_one("#chain_display", Vertical)
        display.remove_children()

        for node in ctx.nodes:
            # Simple card
            card_text = f"[{node.slot_name}] {node.file_path.name}\nScore: {node.compatibility_score:.2f}"
            display.mount(Static(card_text, classes="node-card"))

    def _export_kit(self):
        if not self.chain_result:
            return
        # Mock export
        self.notify("Kit exported (Mock)", severity="success")
