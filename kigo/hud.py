# SPDX-License-Identifier: Zlib

from kigo.qt import QtWidgets, QtCore

class LiveHUD(QtWidgets.QWidget):
    def __init__(self, runtime, parent=None):
        super().__init__(parent)
        self.runtime = runtime

        self.setFixedSize(220, 110)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.setStyleSheet("""
            background: rgba(0,0,0,160);
            color: #00ffcc;
            font-family: Consolas;
            font-size: 11px;
            border-radius: 6px;
        """)

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(8, 8, 204, 94)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(250)

        self.hide()

    def attach_to(self, window):
        """Dock HUD to top-right corner of the window."""
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
        p = self.parent().rect()
        self.move(p.width() - self.width() - 10, 10)

    def refresh(self):
        self.label.setText(
            "KIGO HUD\n"
            "────────────\n"
            f"Mode: {self.runtime.mode.upper()}\n"
            f"Runtime: {'Hybrid' if self.runtime.is_wasm() else 'Python'}\n"
            f"WASM calls: {self.runtime.wasm_calls}\n"
            f"Python calls: {self.runtime.python_calls}"
        )
