# kigo/hwaccel.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from kigo.qt import QtWidgets

@dataclass
class HWCaps:
    has_qtquick: bool
    has_qquickwidget: bool
    has_opengl_viewport: bool
    notes: str = ""

def detect_caps() -> HWCaps:
    # QtQuick availability
    has_qtquick = False
    has_qquickwidget = False
    try:
        from qtpy import QtQuick  # noqa: F401
        has_qtquick = True
    except Exception:
        has_qtquick = False

    try:
        from qtpy import QtQuickWidgets  # noqa: F401
        has_qquickwidget = True
    except Exception:
        has_qquickwidget = False

    # OpenGL viewport availability (QOpenGLWidget)
    has_opengl_viewport = False
    try:
        from qtpy import QtOpenGLWidgets  # noqa: F401
        _ = QtOpenGLWidgets.QOpenGLWidget
        has_opengl_viewport = True
    except Exception:
        # fallback: some bindings expose it differently
        has_opengl_viewport = hasattr(QtWidgets, "QOpenGLWidget")

    return HWCaps(
        has_qtquick=has_qtquick,
        has_qquickwidget=has_qquickwidget,
        has_opengl_viewport=has_opengl_viewport,
        notes="",
    )

class HWPolicy:
    """
    v2.1 policy:
      - prefer Quick if present
      - else prefer OpenGL viewport
      - else fallback to widgets
    """
    def __init__(self, prefer: str = "auto"):
        self.prefer = (prefer or "auto").lower()
        self.caps = detect_caps()

    def pick_ui_backend(self) -> str:
        if self.prefer in ("quick", "qtquick"):
            return "quick" if self.caps.has_qquickwidget else "widgets"
        if self.prefer in ("gl", "opengl", "gl2d"):
            return "gl2d" if self.caps.has_opengl_viewport else "widgets"
        # auto
        if self.caps.has_qquickwidget:
            return "quick"
        if self.caps.has_opengl_viewport:
            return "gl2d"
        return "widgets"