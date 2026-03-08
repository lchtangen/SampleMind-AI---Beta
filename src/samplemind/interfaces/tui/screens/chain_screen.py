"""Chain Screen for SampleMind TUI v3.0"""

from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    RichLog,
    Select,
)

_EFFECTS = [
    ("reverb", "Reverb"),
    ("compressor", "Compressor"),
    ("eq_low_shelf", "EQ Low Shelf"),
    ("eq_high_shelf", "EQ High Shelf"),
    ("limiter", "Limiter"),
    ("normalize", "Normalize"),
    ("noise_gate", "Noise Gate"),
    ("chorus", "Chorus"),
    ("distortion", "Distortion"),
]


class ChainScreen(Screen):
    """Build and apply audio effects chains (pedalboard integration)."""

    BINDINGS = [
        Binding("escape", "action_back", "Back"),
        Binding("ctrl+p", "process_audio", "Process"),
        Binding("ctrl+d", "clear_chain", "Clear chain"),
    ]

    DEFAULT_CSS = """
    ChainScreen { layout: vertical; }
    #chain_body { height: 1fr; padding: 1 2; }
    .screen-title { color: $primary; text-style: bold; height: 1; margin-bottom: 1; }
    .row { height: auto; margin-bottom: 1; }
    .row Label { min-width: 15; content-align: center middle; height: 1; }
    .row Input { width: 1fr; }
    .row Button { min-width: 12; margin-left: 1; }
    #chain_table { height: 8; }
    #log_area { height: 1fr; }
    #btn_row { height: 3; margin-top: 1; }
    #btn_row Button { margin-right: 1; }
    """

    def __init__(self) -> None:
        super().__init__()
        self._chain: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="chain_body"):
            yield Label("Effects Chain Builder", classes="screen-title")
            with Horizontal(classes="row"):
                yield Label("Input file:")
                yield Input(placeholder="Path to audio file...", id="file_input")
                yield Button("Browse", id="btn_browse", variant="primary")
            with Horizontal(classes="row"):
                yield Label("Output file:")
                yield Input(
                    placeholder="Output path (leave blank = auto)...", id="out_input"
                )
            with Horizontal(classes="row"):
                yield Label("Add effect:")
                yield Select(
                    [(lbl, v) for v, lbl in _EFFECTS],
                    id="effect_select",
                    value="reverb",
                )
                yield Button("Add", id="btn_add", variant="success")
                yield Button("Remove Last", id="btn_remove", variant="error")
            yield Label("Effects chain (0 effects):", id="chain_label")
            yield DataTable(zebra_stripes=True, id="chain_table")
            yield RichLog(highlight=True, id="log_area", wrap=True)
            with Horizontal(id="btn_row"):
                yield Button("Process", id="btn_process", variant="success")
                yield Button("Clear", id="btn_clear", variant="warning")
                yield Button("Back", id="btn_back", variant="default")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#chain_table", DataTable)
        table.add_columns("#", "Effect", "Parameters")
        self.query_one("#file_input", Input).focus()

    @on(Button.Pressed, "#btn_browse")
    def on_browse(self, _: Button.Pressed) -> None:
        try:
            from samplemind.utils.file_picker import CrossPlatformFilePicker

            picker = CrossPlatformFilePicker()
            selected = picker.choose_file(
                file_types=["wav", "mp3", "flac"],
            )
            if selected:
                self.query_one("#file_input", Input).value = str(selected)
        except Exception as exc:
            self.notify(f"File picker unavailable: {exc}", severity="warning")

    @on(Button.Pressed, "#btn_add")
    def on_add_effect(self, _: Button.Pressed) -> None:
        effect = str(self.query_one("#effect_select", Select).value)
        self._chain.append(effect)
        self._refresh_chain_table()

    @on(Button.Pressed, "#btn_remove")
    def on_remove_last(self, _: Button.Pressed) -> None:
        if self._chain:
            self._chain.pop()
            self._refresh_chain_table()

    @on(Button.Pressed, "#btn_process")
    def on_process_btn(self, _: Button.Pressed) -> None:
        self.action_process_audio()

    @on(Button.Pressed, "#btn_clear")
    def on_clear_btn(self, _: Button.Pressed) -> None:
        self.action_clear_chain()

    @on(Button.Pressed, "#btn_back")
    def on_back(self, _: Button.Pressed) -> None:
        self.app.pop_screen()

    def _refresh_chain_table(self) -> None:
        table = self.query_one("#chain_table", DataTable)
        table.clear()
        for i, effect in enumerate(self._chain, 1):
            table.add_row(str(i), effect.replace("_", " ").title(), "default params")
        count = len(self._chain)
        self.query_one("#chain_label", Label).update(
            f"Effects chain ({count} effect{'s' if count != 1 else ''}):"
        )

    @work(exclusive=True, thread=True)
    def _apply_chain(self, in_path: str, out_path: str, chain: list[str]) -> None:
        try:
            import asyncio

            from samplemind.services.effects_service import (  # type: ignore[import]
                apply_effects_chain,
            )

            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(
                apply_effects_chain(in_path, out_path, chain)
            )
            loop.close()
            self.app.call_from_thread(
                self._log, f"[green]Processed! Output: {result}[/]"
            )
            self.app.call_from_thread(lambda: self.notify(f"Effects applied: {result}"))
        except Exception as exc:
            self.app.call_from_thread(self._log, f"[red]Processing error: {exc}[/]")

    def _log(self, msg: str) -> None:
        try:
            self.query_one("#log_area", RichLog).write(msg)
        except Exception:
            pass

    def action_process_audio(self) -> None:
        in_path = self.query_one("#file_input", Input).value.strip()
        if not in_path:
            self.notify("Enter an input file path first", severity="warning")
            return
        if not self._chain:
            self.notify("Add at least one effect first", severity="warning")
            return
        out_path = self.query_one("#out_input", Input).value.strip() or ""
        self._log(f"[cyan]Applying {len(self._chain)} effects to {in_path}...[/]")
        self._apply_chain(in_path, out_path, list(self._chain))

    def action_clear_chain(self) -> None:
        self._chain.clear()
        self._refresh_chain_table()

    def action_back(self) -> None:
        self.app.pop_screen()
