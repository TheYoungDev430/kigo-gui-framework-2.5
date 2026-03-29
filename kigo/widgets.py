# kigo/widgets.py
from __future__ import annotations

import os
import sys

# ✅ Kigo Qt shim (QtPy underneath, PySide-first then PyQt)
from kigo.qt import QtCore, QtGui, QtWidgets

# ---------------------------------------------------------
# QtWidgets aliases (common) 
# ---------------------------------------------------------
QLabel = QtWidgets.QLabel
QPushButton = QtWidgets.QPushButton
QLineEdit = QtWidgets.QLineEdit
QComboBox = QtWidgets.QComboBox
QWidget = QtWidgets.QWidget
QCheckBox = QtWidgets.QCheckBox
QProgressBar = QtWidgets.QProgressBar
QScrollBar = QtWidgets.QScrollBar
QSlider = QtWidgets.QSlider
QVBoxLayout = QtWidgets.QVBoxLayout
QHBoxLayout = QtWidgets.QHBoxLayout
QTabWidget = QtWidgets.QTabWidget
QGraphicsBlurEffect = QtWidgets.QGraphicsBlurEffect
QGraphicsOpacityEffect = QtWidgets.QGraphicsOpacityEffect
QFrame = QtWidgets.QFrame
QTableWidget = QtWidgets.QTableWidget
QTableWidgetItem = QtWidgets.QTableWidgetItem
QHeaderView = QtWidgets.QHeaderView
QFileDialog = QtWidgets.QFileDialog
QToolBar = QtWidgets.QToolBar
QSystemTrayIcon = QtWidgets.QSystemTrayIcon
QMenu = QtWidgets.QMenu
QApplication = QtWidgets.QApplication

# Optional / platform-dependent widgets
QScroller = getattr(QtWidgets, "QScroller", None)
QGestureEvent = getattr(QtWidgets, "QGestureEvent", None)
QPinchGesture = getattr(QtWidgets, "QPinchGesture", None)
QPanGesture = getattr(QtWidgets, "QPanGesture", None)

# ---------------------------------------------------------
# QtGui aliases
# ---------------------------------------------------------
QAction = QtGui.QAction
QIcon = QtGui.QIcon
QCursor = QtGui.QCursor
QPalette = QtGui.QPalette
QColor = QtGui.QColor
QPainter = QtGui.QPainter
QBrush = QtGui.QBrush

# ---------------------------------------------------------
# QtCore aliases
# ---------------------------------------------------------
QUrl = QtCore.QUrl
Qt = QtCore.Qt
QPropertyAnimation = QtCore.QPropertyAnimation
QEasingCurve = QtCore.QEasingCurve
QPoint = QtCore.QPoint
QTimer = QtCore.QTimer
QRect = QtCore.QRect
QEvent = QtCore.QEvent


# =========================================================
# Touch & Mobile Optimization
# =========================================================

class TouchScrollArea:
    """A container that enables mobile-style kinetic scrolling (swipe to scroll)."""
    def __init__(self, widget):
        self.qt_widget = widget

        # Enable kinetic scrolling if available
        if QScroller is not None:
            QScroller.grabGesture(
                self.qt_widget,
                QScroller.ScrollerGestureType.LeftMouseButtonGesture
            )

        # Slim scrollbars for touch UI
        if hasattr(self.qt_widget, "verticalScrollBar"):
            self.qt_widget.verticalScrollBar().setStyleSheet(
                "width: 5px; background: transparent;"
            )
        if hasattr(self.qt_widget, "horizontalScrollBar"):
            self.qt_widget.horizontalScrollBar().setStyleSheet(
                "height: 5px; background: transparent;"
            )


class TouchButton(QPushButton):
    """A button optimized for fingers: larger hit area and press feedback."""
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.qt_widget = self
        self.setMinimumHeight(50)
        self.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border-radius: 10px;
                font-size: 14pt;
                padding: 10px;
                border: none;
            }
            QPushButton:pressed {
                background-color: #0051A8;
            }
        """)

    def mousePressEvent(self, event):
        eff = QGraphicsOpacityEffect(self)
        eff.setOpacity(0.7)
        self.setGraphicsEffect(eff)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setGraphicsEffect(None)
        super().mouseReleaseEvent(event)


class GestureWidget(QWidget):
    """A base widget that detects Pinches and Pans (Swipes) for tablets."""
    def __init__(self):
        super().__init__()
        self.qt_widget = self
        self.grabGesture(Qt.GestureType.PinchGesture)
        self.grabGesture(Qt.GestureType.PanGesture)
        self.grabGesture(Qt.GestureType.SwipeGesture)

    def event(self, event):
        if event.type() == QEvent.Type.Gesture:
            return self.gestureEvent(event)
        return super().event(event)

    def gestureEvent(self, event):
        pinch = event.gesture(Qt.GestureType.PinchGesture)
        pan = event.gesture(Qt.GestureType.PanGesture)

        if pinch:
            _scale_factor = pinch.scaleFactor()
            # Hook for zoom logic (override in subclasses)

        if pan:
            _delta = pan.delta()
            # Hook for swipe logic (override in subclasses)

        return True


# =========================================================
# UI Containers & Visuals
# =========================================================

class Card(QFrame):
    """Rounded container for dashboard layouts (styled by QSS via #kigo_card)."""
    def __init__(self, title: str = "Card"):
        super().__init__()
        self.qt_widget = self
        self.setObjectName("kigo_card")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self.layout = QVBoxLayout(self)
        label = QLabel(title)
        label.setStyleSheet("font-weight: bold; border: none; font-size: 14pt; color: inherit;")
        self.layout.addWidget(label)

    def add_widget(self, widget):
        w = widget.qt_widget if hasattr(widget, "qt_widget") else widget
        self.layout.addWidget(w)


# =========================================================
# Palette Theme (basic)
# =========================================================

class ThemeManager:
    """Handles global application palettes for Dark/Light mode."""
    @staticmethod
    def set_dark_mode():
        app = QApplication.instance()
        if not app:
            return

        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        p.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        p.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
        p.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        p.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
        p.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        app.setPalette(p)

    @staticmethod
    def set_light_mode():
        app = QApplication.instance()
        if app:
            app.setPalette(app.style().standardPalette())


class DarkModeToggle:
    """A ready-to-use toggle for palette switching."""
    def __init__(self, text: str = "Dark Mode"):
        self.qt_widget = QCheckBox(text)
        self.qt_widget.toggled.connect(
            lambda c: ThemeManager.set_dark_mode() if c else ThemeManager.set_light_mode()
        )


# =========================================================
# Animator utility
# =========================================================

class Animator:
    @staticmethod
    def fade_in(widget, duration: int = 500):
        target = widget.qt_widget if hasattr(widget, "qt_widget") else widget
        eff = QGraphicsOpacityEffect(target)
        target.setGraphicsEffect(eff)

        anim = QPropertyAnimation(eff, b"opacity")
        anim.setDuration(int(duration))
        anim.setStartValue(0)
        anim.setEndValue(1)

        # Prevent GC stopping the animation
        store = getattr(target, "_kigo_anims", None)
        if store is None:
            store = []
            setattr(target, "_kigo_anims", store)
        store.append(anim)
        anim.finished.connect(lambda: store.remove(anim) if anim in store else None)

        anim.start()
        return anim


# =========================================================
# Import: CSS engine + default themes (style.py)
# Import: skins (skins.py)
# Import: tree + media modules
# =========================================================

from .style import (
    StyleSheet, StyleManager,
    KIGO_BASE_CSS, KIGO_TOKENS_LIGHT, KIGO_TOKENS_DARK,
)

from .skins import (
    SkinManager, KIGO_SKINS,
    apply_neon, apply_retro, apply_glass,
)

from .tree import TreeModel, TreeView
from .media import AudioPlayerWidget, VideoPlayerWidget


# =========================================================
# Exports
# =========================================================

__all__ = [
    # touch / gestures
    "TouchScrollArea", "TouchButton", "GestureWidget",

    # containers
    "Card",

    # palette theme
    "ThemeManager", "DarkModeToggle",

    # styling engine + defaults
    "StyleSheet", "StyleManager",
    "KIGO_BASE_CSS", "KIGO_TOKENS_LIGHT", "KIGO_TOKENS_DARK",

    # skins (v1.8)
    "SkinManager", "KIGO_SKINS",
    "apply_neon", "apply_retro", "apply_glass",

    # tree / hierarchy
    "TreeModel", "TreeView",

    # media
    "AudioPlayerWidget", "VideoPlayerWidget",

    # utility
    "Animator",

    # commonly re-exported Qt classes
    "QLabel", "QPushButton", "QLineEdit", "QComboBox", "QWidget", "QCheckBox",
    "QProgressBar", "QScrollBar", "QSlider", "QVBoxLayout", "QHBoxLayout",
    "QTabWidget", "QFrame", "QTableWidget", "QTableWidgetItem", "QHeaderView",
    "QFileDialog", "QToolBar", "QSystemTrayIcon", "QMenu", "QApplication",
    "QAction", "QIcon", "QCursor", "QPalette", "QColor", "QPainter", "QBrush",
    "QUrl", "Qt", "QPropertyAnimation", "QEasingCurve", "QPoint", "QTimer", "QRect", "QEvent",
]