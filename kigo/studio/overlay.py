# SPDX-License-Identifier: Zlib

from kigo.qt import QtWidgets, QtCore, QtGui

Qt = QtCore.Qt


class StudioOverlay(QtWidgets.QWidget):
    """
    Semi-transparent dev overlay for Kigo Studio.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        self.setStyleSheet("""
            background: rgba(20, 20, 20, 0.85);
            color: #ddd;
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QtWidgets.QLabel("Kigo Studio")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        info = QtWidgets.QLabel(
            "Esc: toggle studio\n"
            "Click widgets to inspect (coming soon)\n"
            "Performance panel (coming soon)"
        )

        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(info)

    def show(self):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().show()
        self.raise_()
