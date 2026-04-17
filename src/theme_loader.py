import json
from pathlib import Path


class ThemeLoader:
    def __init__(self):
        self.has_user_theme = False
        self.default_theme = {
            "surface": "#f8f9ff",
            "surface_container_low": "#eff4ff",
            "surface_container_lowest": "#ffffff",
            "surface_dim": "#cbdbf5",
            "on_surface": "#0b1c30",
            "on_surface_muted": "#5d7088",
            "primary": "#006c49",
            "primary_container": "#10b981",
            "on_primary": "#ffffff",
            "on_primary_container": "#0b1c30",
            "secondary_container": "#b7ebce",
            "outline_variant": "#9fb1c8",
            "danger": "#a43a3a",
            "danger_container": "#f4d5d5",
            "font_display": "Manrope",
            "font_body": "Inter",
            "radius_sm": 6,
            "radius_md": 12,
            "radius_lg": 16,
            "space_xs": 6,
            "space_sm": 10,
            "space_md": 16,
            "space_lg": 24,
        }

        self.theme = dict(self.default_theme)
        style_file = Path(__file__).resolve().parents[1] / "ui_style.json"
        if style_file.exists():
            self.has_user_theme = True
            self._load_user_theme(style_file)

    def _load_user_theme(self, path: Path):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for key, value in data.items():
                    if key in self.default_theme:
                        self.theme[key] = value
        except Exception:
            # Keep defaults if local style file is malformed.
            self.theme = dict(self.default_theme)

    def get(self, key: str):
        return self.theme[key]
