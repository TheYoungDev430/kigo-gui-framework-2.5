# kigo/style.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Union

from kigo.qt import QtWidgets


@dataclass
class StyleSheet:
    """
    Lightweight CSS-like styling layer for Kigo (Qt StyleSheet underneath).

    Supports token variables like:
        var(--bg), var(--accent)

    Notes:
    - Qt StyleSheets support Type selectors, #objectName, [property="value"], and :states.
    - "var(--token)" is implemented by simple string replacement here.
    """
    text: str

    def render(self, tokens: Optional[Dict[str, str]] = None) -> str:
        out = self.text
        tokens = tokens or {}
        for k, v in tokens.items():
            kk = k if k.startswith("--") else f"--{k}"
            out = out.replace(f"var({kk})", str(v))
        return out


class StyleManager:
    """
    Applies the stylesheet to the QApplication.
    You can update tokens at runtime to switch themes/skins.
    """
    _current: Optional[StyleSheet] = None
    _tokens: Dict[str, str] = {}

    @staticmethod
    def set_tokens(tokens: Dict[str, str]):
        StyleManager._tokens = dict(tokens)

    @staticmethod
    def apply(stylesheet: Union[str, StyleSheet], *, tokens: Optional[Dict[str, str]] = None):
        app = QtWidgets.QApplication.instance()
        if not app:
            return

        if isinstance(stylesheet, str):
            stylesheet = StyleSheet(stylesheet)

        StyleManager._current = stylesheet
        if tokens is not None:
            StyleManager.set_tokens(tokens)

        app.setStyleSheet(stylesheet.render(StyleManager._tokens))

    @staticmethod
    def refresh():
        """Re-apply the last stylesheet (useful after token changes)."""
        if StyleManager._current is None:
            return
        StyleManager.apply(StyleManager._current)

    @staticmethod
    def refresh_widget(widget):
        """
        Re-polish a widget after changing properties used in QSS selectors,
        e.g. widget.setProperty("kigoClass","primary")
        """
        w = getattr(widget, "qt_widget", widget)
        w.style().unpolish(w)
        w.style().polish(w)
        w.update()


# ---- default Kigo base CSS (token-driven) ----
KIGO_BASE_CSS = r"""
QWidget {
  background: var(--bg);
  color: var(--fg);
  font-family: var(--font);
  font-size: var(--fontSize);
}

QFrame#kigo_card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox, QDateEdit, QTimeEdit {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 6px 8px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {
  border: 1px solid var(--accent);
}

/* Buttons */
QPushButton {
  background: var(--accent);
  color: var(--onAccent);
  border: none;
  border-radius: 10px;
  padding: 8px 12px;
}

QPushButton:hover { background: var(--accentHover); }
QPushButton:pressed { background: var(--accentPressed); }
QPushButton:disabled { background: var(--disabled); color: var(--muted); }

/* “class” selector: widget.setProperty("kigoClass","primary") */
QPushButton[kigoClass="primary"] { background: var(--accent); }
QPushButton[kigoClass="danger"] { background: var(--danger); }

/* Tree / hierarchy */
QTreeView {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
}
QTreeView::item:selected {
  background: var(--accent);
  color: var(--onAccent);
}
"""

# Default token packs (optional — skins can override completely)
KIGO_TOKENS_LIGHT = {
    "--bg": "#ffffff",
    "--fg": "#111111",
    "--card": "#ffffff",
    "--border": "#d0d0d0",
    "--accent": "#007AFF",
    "--accentHover": "#178BFF",
    "--accentPressed": "#0051A8",
    "--danger": "#D92D20",
    "--disabled": "#e6e6e6",
    "--muted": "#666666",
    "--font": "Segoe UI",
    "--fontSize": "12pt",
    "--onAccent": "#ffffff",
}

KIGO_TOKENS_DARK = {
    "--bg": "#1e1e1e",
    "--fg": "#f2f2f2",
    "--card": "#252526",
    "--border": "#3a3a3a",
    "--accent": "#0A84FF",
    "--accentHover": "#2B95FF",
    "--accentPressed": "#0060DF",
    "--danger": "#F04438",
    "--disabled": "#3a3a3a",
    "--muted": "#a8a8a8",
    "--font": "Segoe UI",
    "--fontSize": "12pt",
    "--onAccent": "#ffffff",
}