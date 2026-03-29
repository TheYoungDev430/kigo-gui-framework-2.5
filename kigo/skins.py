# kigo/skins.py
#
# Central skin system for Kigo
# Built-in skins live here (no skins/ folder)

from typing import Dict, Optional, Callable

from kigo.style import StyleManager, StyleSheet, KIGO_BASE_CSS
from kigo.qt import QtCore

Qt = QtCore.Qt

# ==========================================================
# Kigo Skin Manager v2.0
# ==========================================================

_SKINS: Dict[str, dict] = {}

REQUIRED_TOKENS = {
    "--bg",
    "--fg",
    "--card",
    "--border",

    "--accent",
    "--accentHover",
    "--accentPressed",
    "--onAccent",

    "--danger",
    "--disabled",
    "--muted",

    "--font",
    "--fontSize",
}


# ==========================================================
# Public API
# ==========================================================

def register_skin(
    *,
    name: str,
    tokens: Dict[str, str],
    extra_css: str = "",
    window_flags: Optional[Callable] = None,
    preview: Optional[dict] = None,
):
    key = name.strip().lower()
    if not key:
        raise ValueError("Skin name cannot be empty")

    if key in _SKINS:
        raise ValueError(f"Skin '{key}' already registered")

    missing = REQUIRED_TOKENS - set(tokens.keys())
    if missing:
        raise ValueError(
            f"Skin '{key}' missing required tokens: {sorted(missing)}"
        )

    _SKINS[key] = {
        "name": key,
        "tokens": dict(tokens),
        "extra_css": extra_css or "",
        "window_flags": window_flags,
        "preview": preview or {},
    }


class SkinManager:
    current: Optional[str] = None

    @staticmethod
    def apply(name: str, *, window=None):
        key = name.strip().lower()
        if key not in _SKINS:
            raise ValueError(
                f"Unknown skin '{key}'. Available: {sorted(_SKINS)}"
            )

        skin = _SKINS[key]

        css = KIGO_BASE_CSS + "\n" + skin["extra_css"]
        StyleManager.apply(
            StyleSheet(css),
            tokens=skin["tokens"],
        )

        if skin["window_flags"] and window is not None:
            w = getattr(window, "qt_widget", window)
            skin["window_flags"](w)

        SkinManager.current = key

    @staticmethod
    def available():
        return sorted(_SKINS.keys())

    @staticmethod
    def info(name: str):
        return dict(_SKINS[name])


# ==========================================================
# Helpers
# ==========================================================

def enable_glass_window(window):
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    window.setAutoFillBackground(False)


# ==========================================================
# Built-in skins
# ==========================================================

# -------------------------
# Neon
# -------------------------
register_skin(
    name="neon",
    tokens={
        "--bg": "#050607",
        "--fg": "#9effc9",
        "--card": "#0b0f0d",
        "--border": "#00ff9c",

        "--accent": "#00ff9c",
        "--accentHover": "#3dffb5",
        "--accentPressed": "#00cc7a",
        "--onAccent": "#000000",

        "--danger": "#ff5555",
        "--disabled": "#2a2a2a",
        "--muted": "#6affb1",

        "--font": "Consolas",
        "--fontSize": "11pt",
    },
    extra_css="""
    QFrame#kigo_card {
      border-radius: 10px;
      border: 1px solid var(--accent);
    }
    """,
    preview={"title": "Neon"},
)

# -------------------------
# Retro (XP-ish)
# -------------------------
register_skin(
    name="retro",
    tokens={
        "--bg": "#cfd8dc",
        "--fg": "#000000",
        "--card": "#e6eef3",
        "--border": "#7a9bb8",

        "--accent": "#316ac5",
        "--accentHover": "#4f83d1",
        "--accentPressed": "#254e9c",
        "--onAccent": "#ffffff",

        "--danger": "#cc0000",
        "--disabled": "#9aa7b0",
        "--muted": "#445560",

        "--font": "Tahoma",
        "--fontSize": "10pt",
    },
    extra_css="""
    QFrame#kigo_card {
      border-radius: 6px;
      border: 1px solid #7a9bb8;
      background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #f4f9fc,
        stop:1 #d6e1ea
      );
    }
    """,
    preview={"title": "Retro"},
)

# -------------------------
# Glass
# -------------------------
register_skin(
    name="glass",
    tokens={
        "--bg": "rgba(30,30,30,180)",
        "--fg": "#ffffff",
        "--card": "rgba(255,255,255,40)",
        "--border": "rgba(255,255,255,80)",

        "--accent": "#4fc3f7",
        "--accentHover": "#81d4fa",
        "--accentPressed": "#039be5",
        "--onAccent": "#000000",

        "--danger": "#ef5350",
        "--disabled": "rgba(255,255,255,80)",
        "--muted": "#cfd8dc",

        "--font": "Segoe UI",
        "--fontSize": "11pt",
    },
    extra_css="""
    QFrame#kigo_card {
      border-radius: 14px;
      background: var(--card);
      border: 1px solid var(--border);
    }
    """,
    window_flags=enable_glass_window,
    preview={"title": "Glass"},
)

# -------------------------
# CyberDark (VS Code style)
# -------------------------
register_skin(
    name="cyberdark",
    tokens={
        "--bg": "#1e1e1e",
        "--fg": "#d4d4d4",
        "--card": "#252526",
        "--border": "#3c3c3c",

        "--accent": "#007acc",
        "--accentHover": "#2899f5",
        "--accentPressed": "#005a9e",
        "--onAccent": "#ffffff",

        "--danger": "#f44747",
        "--disabled": "#555555",
        "--muted": "#9d9d9d",

        "--font": "Segoe UI",
        "--fontSize": "11pt",
    },
    extra_css="""
    QFrame#kigo_card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 6px;
    }

    QTreeView::item:selected {
      background: #094771;
      color: #ffffff;
    }

    QPushButton {
      background: #3c3c3c;
      border: 1px solid #454545;
      border-radius: 4px;
    }

    QPushButton:pressed {
      background: var(--accent);
      color: var(--onAccent);
    }
    """,
    preview={
        "title": "CyberDark",
        "description": "VS Code–style dark theme",
    },
)