# TUI v3.0 Upgrade Notes

**Migration:** Textual ^0.44.0 → ^0.87.0
**Phase:** 15 — v3.0 Migration
**Last Updated:** 2026-03-07

---

## Breaking Changes: Textual ^0.44 → ^0.87

### CSS Variable Syntax

Old (^0.44):
```css
$primary: blue;
```

New (^0.87):
```css
--primary: blue;
```

### Screen Lifecycle

Old: `on_mount()` for initialization
New: Use `on_mount()` still, but `compose()` must be pure/synchronous. Async initialization
belongs in `on_mount()`.

### Widget Composition

Old:
```python
def compose(self) -> ComposeResult:
    yield from super().compose()
```

New:
```python
def compose(self) -> ComposeResult:
    yield from self.COMPONENT_CLASSES
```

### Reactive Declarations

Old:
```python
count = reactive(0)
```

New — works the same, but `watch_*` methods are now preferred over `compute_*` for side effects:
```python
count: reactive[int] = reactive(0)

def watch_count(self, value: int) -> None:
    self.update_display(value)
```

---

## Phase 15 New Screens (to implement)

| Screen | File | Status |
|--------|------|--------|
| AgentChatScreen | `screens/agent_chat_screen.py` | Not started |
| WaveformScreen | `screens/waveform_screen.py` | Not started |
| MixingBoardScreen | `screens/mixing_board_screen.py` | Not started |

### AgentChatScreen — Requirements
- Multi-agent conversation UI
- Uses OpenAI Agents SDK (gpt-4o)
- Streaming responses with `on_message` events
- Message history scrollable

### WaveformScreen — Requirements
- Interactive waveform viewer
- Uses librosa for audio data
- Static/Canvas widget for rendering
- Playback position indicator

### MixingBoardScreen — Requirements
- Real-time effects and EQ sliders
- Uses pedalboard for processing
- Knob/slider widgets
- Live audio I/O via pyaudio

---

## Files to Update for v0.87

- `src/samplemind/interfaces/tui/app.py` — main app class
- `src/samplemind/interfaces/tui/screens/*.py` — all screen files
- `src/samplemind/interfaces/tui/styles/*.tcss` — CSS files (variable syntax)
- `src/samplemind/interfaces/tui/widgets/*.py` — widget files

---

## Testing TUI After Upgrade

```bash
source .venv/bin/activate
python -m samplemind.interfaces.tui.app   # smoke test
make test tests/unit/interfaces/          # unit tests
```
