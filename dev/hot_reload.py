# SPDX-License-Identifier: Zlib
import os
import sys
from PyQt6.QtCore import QObject, QFileSystemWatcher, QTimer


class AppHotReloader(QObject):
    """
    Dev-only Python hot reload.
    Watches .py files and restarts the app process on change.
    """

    def __init__(self, watch_dirs, debounce_ms=200):
        super().__init__()

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(debounce_ms)
        self._timer.timeout.connect(self._restart)

        self._watcher = QFileSystemWatcher(self)

        for d in watch_dirs:
            self._watcher.addPath(d)

        self._watcher.directoryChanged.connect(self._on_change)
        self._watcher.fileChanged.connect(self._on_change)

    def _on_change(self, path):
        if path.endswith(".py"):
            self._timer.start()

    def _restart(self):
        print("[Kigo] Hot reload: restarting app")
        python = sys