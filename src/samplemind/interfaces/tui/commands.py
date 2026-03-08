"""SampleMind CommandPalette Provider for Textual ^0.87"""

from __future__ import annotations

from textual.command import Hit, Hits, Provider


class SampleMindCommands(Provider):
    """CommandPalette provider for all SampleMind TUI actions."""

    COMMANDS: list[tuple[str, str, str]] = [
        # (display_text, help_text, action_name)
        ("📂 Analyze File", "Analyze a single audio file", "goto_analyze"),
        ("📦 Batch Process", "Process a folder of audio files", "goto_batch"),
        ("📚 Library Browser", "Browse the sample library", "goto_library"),
        ("🔍 Search Samples", "Semantic search across samples", "goto_search"),
        ("🤖 AI Chat", "Chat with the AI music assistant", "goto_ai_chat"),
        ("📊 Visualizer", "Interactive audio visualizer", "goto_visualizer"),
        ("⭐ Favorites", "Manage favorite samples", "goto_favorites"),
        ("🏷️ Tag Samples", "Edit tags on samples", "goto_tagging"),
        ("⚖️ Compare Samples", "Side-by-side sample comparison", "goto_comparison"),
        ("🎚️ Effects Chain", "Apply pedalboard effects chain", "goto_chain"),
        ("🏷️ Classify Audio", "AI-powered genre classification", "goto_classification"),
        ("📈 Performance", "View pipeline performance metrics", "goto_performance"),
        ("⚙️ Settings", "Application settings", "goto_settings"),
        # Themes
        (
            "🎨 Theme: SampleMind Dark",
            "Electric Teal + Deep Purple",
            "set_theme_samplemind_dark",
        ),
        ("🎨 Theme: SampleMind Light", "Teal + White", "set_theme_samplemind_light"),
        ("🎨 Theme: Midnight Pro", "Gold + Black", "set_theme_midnight_pro"),
        (
            "🎨 Theme: Neon Synthwave",
            "Hot Pink + Ultra Dark",
            "set_theme_neon_synthwave",
        ),
        ("🎨 Theme: Forest Green", "Lime + Dark Forest", "set_theme_forest_green"),
        (
            "🎨 Theme: High Contrast",
            "WCAG-accessible black/white/yellow",
            "set_theme_high_contrast",
        ),
    ]

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for display, help_text, action in self.COMMANDS:
            score = matcher.match(display)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(display),
                    self._make_callback(action),
                    help=help_text,
                )

    def _make_callback(self, action: str):
        if action.startswith("set_theme_"):
            theme_name = action[len("set_theme_") :].replace("_", "-")
            return lambda: setattr(self.app, "theme", theme_name)
        if action.startswith("goto_"):
            screen_action = action[len("goto_") :]
            return lambda a=screen_action: self._navigate(a)
        return lambda: None

    def _navigate(self, screen_action: str) -> None:
        handler = getattr(self.app, f"action_{screen_action}", None)
        if handler is None:
            # Try going through the active screen
            try:
                screen = self.app.screen
                handler = getattr(screen, f"action_goto_{screen_action}", None)
                if handler is None:
                    handler = getattr(screen, f"action_{screen_action}", None)
            except Exception:
                pass
        if handler:
            handler()
        else:
            screen_map = {
                "analyze": "analyze_screen.AnalyzeScreen",
                "batch": "batch_screen.BatchScreen",
                "library": "library_screen.LibraryScreen",
                "search": "search_screen.SearchScreen",
                "ai_chat": "ai_chat_screen.AIChatScreen",
                "visualizer": "visualizer_screen.VisualizerScreen",
                "favorites": "favorites_screen.FavoritesScreen",
                "tagging": "tagging_screen.TaggingScreen",
                "comparison": "comparison_screen.ComparisonScreen",
                "chain": "chain_screen.ChainScreen",
                "classification": "classification_screen.ClassificationScreen",
                "performance": "performance_screen.PerformanceScreen",
                "settings": "settings_screen.SettingsScreen",
            }
            module_class = screen_map.get(screen_action)
            if module_class:
                mod_name, cls_name = module_class.split(".")
                try:
                    from importlib import import_module

                    mod = import_module(
                        f".screens.{mod_name}", package="samplemind.interfaces.tui"
                    )
                    cls = getattr(mod, cls_name)
                    self.app.push_screen(cls())
                except Exception:
                    pass
