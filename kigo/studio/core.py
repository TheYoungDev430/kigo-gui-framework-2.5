# SPDX-License-Identifier: Zlib

from kigo.qt import QtCore

Qt = QtCore.Qt
QObject = QtCore.QObject
QEvent = QtCore.QEvent


class StudioController(QObject):
    """
    Global controller for Kigo Studio.
    Toggles Studio with Esc key.
    """

    def __init__(self, app, overlay):
        super().__init__()
        self.app = app
        self.overlay = overlay
        self.enabled = True

        # Install global event filter
        app.installEventFilter(self)

    def eventFilter(self, obj, event):
        if not self.enabled:
            return False

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.toggle()
                return True  # consume Esc

        return False

    def toggle(self):
        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.show()
