# SPDX-License-Identifier: Zlib
# kigo/app.py — Core Kigo App with Studio (Esc), HUD (F2), and Python/WASM modes.

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

from kigo.qt import QtWidgets, QtCore, QtGui


# =====================================================
# Runtime state
# =====================================================

class Runtime:
    def __init__(self, mode: str = "python"):
        if mode is None:
            mode = "python"
        mode = str(mode).strip().lower()

        if mode not in ("python", "wasm"):
            raise ValueError("mode must be 'python' or 'wasm'")

        self.mode = mode

        # Counters for HUD
        self.python_calls = 0
        self.wasm_calls = 0
        self.wasm_hits = 0
        self.wasm_fallbacks = 0

        # Capability flags
        self.wasm_available = False
        self.wasm_reason = ""

    def is_wasm(self) -> bool:
        return self.mode == "wasm"


# =====================================================
# Hot-path marker
# =====================================================

def hot(*, wasm: Optional[str] = None, module: str = "default"):
    """
    Marks a function as eligible for WASM acceleration.

    Example:
        @hot(wasm="mul42", module="math")
        def heavy(x: int) -> int:
            return x * 42
    """
    def decorate(fn):
        fn.__kigo_hot__ = True
        fn.__kigo_wasm_export__ = wasm or fn.__name__
        fn.__kigo_wasm_module__ = module
        return fn
    return decorate


# =====================================================
# WASM Executor (Wasmtime)
# =====================================================

@dataclass
class _WasmHandle:
    store: Any
    exports: Dict[str, Any]


class WasmExecutor:
    """
    Loads WASM modules from a registry and calls exported functions.

    Supports:
      - WAT source (string starting with "(module")
      - file path to .wasm
    """

    def __init__(self, runtime: Runtime):
        self.runtime = runtime
        self._mods: Dict[str, _WasmHandle] = {}
        self._enabled = False

        try:
            from wasmtime import Store, Module, Instance
            self._Store = Store
            self._Module = Module
            self._Instance = Instance
            self._enabled = True
            self.runtime.wasm_available = True
        except Exception as e:
            # Honest fallback: no wasmtime, no wasm mode.
            self.runtime.wasm_available = False
            self.runtime.wasm_reason = f"wasmtime not available: {e}"
            self._enabled = False

    def enabled(self) -> bool:
        return self._enabled

    def load_registry(self, registry: Dict[str, Any]) -> None:
        if not self._enabled:
            return

        for name, spec in (registry or {}).items():
            try:
                self._load_one(name, spec)
            except Exception as e:
                # Don’t crash app: just mark wasm as partially available
                self.runtime.wasm_reason = f"module '{name}' failed: {e}"

    def _load_one(self, name: str, spec: Any) -> None:
        store = self._Store()

        # Allow either raw WAT string or a dict {"wat": "..."} / {"file": "..."}
        wat_src = None
        file_path = None

        if isinstance(spec, str):
            s = spec.lstrip()
            if s.startswith("(module"):
                wat_src = spec
            else:
                file_path = spec
        elif isinstance(spec, dict):
            if "wat" in spec:
                wat_src = spec["wat"]
            elif "file" in spec:
                file_path = spec["file"]
            else:
                raise ValueError("invalid module spec dict; use {'wat': ...} or {'file': ...}")
        else:
            raise ValueError("invalid module spec; use WAT string, wasm file path, or dict spec")

        if wat_src is not None:
            module = self._Module(store.engine, wat_src)
        else:
            module = self._Module.from_file(store.engine, file_path)

        instance = self._Instance(store, module, [])
        exports = instance.exports(store)

        self._mods[str(name)] = _WasmHandle(store=store, exports=exports)

    def has_export(self, module: str, export: str) -> bool:
        if not self._enabled:
            return False
        h = self._mods.get(module)
        return bool(h and export in h.exports)

    def call(self, module: str, export: str, *args):
        self.runtime.wasm_calls += 1
        h = self._mods[module]
        fn = h.exports[export]
        return fn(h.store, *args)


# =====================================================
# Live HUD (F2 toggled, top-right)
# =====================================================

class LiveHUD(QtWidgets.QWidget):
    def __init__(self, runtime: Runtime, parent=None):
        super().__init__(parent)
        self.runtime = runtime

        self.setFixedSize(240, 130)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.setStyleSheet("""
            background: rgba(0, 0, 0, 160);
            color: #00ffcc;
            font-family: Consolas;
            font-size: 11px;
            border-radius: 6px;
        """)

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(10, 8, 220, 114)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(250)

        self.hide()

    def attach_to(self, window: QtWidgets.QWidget):
        self.setParent(window)
        self.reposition()
        window.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.Resize:
            self.reposition()
        return False

    def reposition(self):
        if not self.parent():
            return
        r = self.parent().rect()
        self.move(r.width() - self.width() - 10, 10)

    def refresh(self):
        total = self.runtime.wasm_hits + self.runtime.wasm_fallbacks
        hit_pct = (self.runtime.wasm_hits * 100.0 / total) if total else 0.0

        wasm_state = "OK" if self.runtime.wasm_available else "OFF"
        if self.runtime.is_wasm() and not self.runtime.wasm_available:
            wasm_state = "FALLBACK"

        self.label.setText(
            "KIGO HUD\n"
            "────────────\n"
            f"Mode: {self.runtime.mode.upper()}\n"
            f"WASM: {wasm_state}\n"
            f"WASM hits: {self.runtime.wasm_hits} ({hit_pct:.0f}%)\n"
            f"WASM fallbacks: {self.runtime.wasm_fallbacks}\n"
            f"Python calls: {self.runtime.python_calls}\n"
            f"WASM calls: {self.runtime.wasm_calls}"
        )


# =====================================================
# Studio overlay (Esc toggled) — dev only
# =====================================================

class StudioOverlay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            QtCore.Qt.WindowType.Tool |
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 15, 15, 215);
                color: #e0e0e0;
                font-family: Consolas, monospace;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("Kigo Studio")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        hint = QtWidgets.QLabel(
            "Esc — toggle Studio\n"
            "F2 — toggle HUD\n"
            "Inspector panels coming soon"
        )

        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addStretch(1)

    def showEvent(self, e):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().showEvent(e)


class StudioController(QtCore.QObject):
    def __init__(self, app: QtWidgets.QApplication, overlay: StudioOverlay):
        super().__init__()
        self.overlay = overlay
        app.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_Escape:
                self.toggle()
                return True
        return False

    def toggle(self):
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show()
            self.overlay.raise_()


# =====================================================
# Core App
# =====================================================

class App:
    """
    Core Kigo application.

    - mode: "python" (default) or "wasm"
    - F2 toggles HUD
    - Esc toggles Studio (only if studio=True)
    """

    def __init__(self, *, mode: str = "python", dev: bool = False, studio: bool = False):
        self.runtime = Runtime(mode)
        self.dev = bool(dev)
        self.studio = bool(studio)

        self.qt_app = QtWidgets.QApplication(sys.argv)

        self.main_window: Optional[QtWidgets.QWidget] = None

        # WASM executor (real if wasmtime present)
        self.wasm = WasmExecutor(self.runtime) if self.runtime.is_wasm() else None

        # If wasm mode requested but not available -> honest fallback
        if self.runtime.is_wasm() and (not self.wasm or not self.wasm.enabled()):
            self.runtime.mode = "python"

        # Load wasm module registry if in wasm mode and runtime available
        if self.runtime.is_wasm() and self.wasm and self.wasm.enabled():
            try:
                from kigo.wasm.module import WASM_MODULES
            except Exception:
                WASM_MODULES = {}
                self.runtime.wasm_reason = "WASM registry not found"
            self.wasm.load_registry(WASM_MODULES)

        self.hud: Optional[LiveHUD] = None
        self._hud_shortcut = None

        self._studio_overlay: Optional[StudioOverlay] = None
        self._studio_controller: Optional[StudioController] = None

    # -----------------------------
    # Unified execution path
    # -----------------------------
    def call(self, fn, *args):
        # Try WASM only for hot functions
        if getattr(fn, "__kigo_hot__", False) and self.runtime.is_wasm() and self.wasm:
            mod = getattr(fn, "__kigo_wasm_module__", "default")
            exp = getattr(fn, "__kigo_wasm_export__", fn.__name__)

            if self.wasm.has_export(mod, exp):
                self.runtime.wasm_hits += 1
                return self.wasm.call(mod, exp, *args)

            # wasm mode but export missing => fallback
            self.runtime.wasm_fallbacks += 1
            self.runtime.python_calls += 1
            return fn(*args)

        # Normal python path
        self.runtime.python_calls += 1
        return fn(*args)

    # -----------------------------
    # App lifecycle
    # -----------------------------
    def run(self):
        self.on_start()

        if self.dev:
            self._attach_hud()

        if self.dev and self.studio:
            self._attach_studio()

        sys.exit(self.qt_app.exec())

    def on_start(self):
        """
        Override in user app. Must set self.main_window and show it.
        """
        raise NotImplementedError("on_start() not implemented")

    # -----------------------------
    # HUD wiring (F2 toggle)
    # -----------------------------
    def _attach_hud(self):
        if not self.main_window:
            raise RuntimeError("main_window not set")

        self.hud = LiveHUD(self.runtime, parent=self.main_window)
        self.hud.attach_to(self.main_window)

        self._hud_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("F2"), self.main_window)
        self._hud_shortcut.setContext(QtCore.Qt.ShortcutContext.ApplicationShortcut)
        self._hud_shortcut.activated.connect(self._toggle_hud)

    def _toggle_hud(self):
        if not self.hud:
            return
        if self.hud.isVisible():
            self.hud.hide()
        else:
            self.hud.show()
            self.hud.raise_()

    # -----------------------------
    # Studio wiring (Esc toggle)
    # -----------------------------
    def _attach_studio(self):
        if not self.main_window:
            raise RuntimeError("main_window not set")

        self._studio_overlay = StudioOverlay(parent=self.main_window)
        self._studio_controller = StudioController(self.qt_app, self._studio_overlay)
