

from __future__ import annotations

import importlib.util
import os

def _has(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


# ------------------------------------------------------------
# Binding selection (PySide-first)
# ------------------------------------------------------------
# QtPy uses QT_API to decide which binding to load. [1](https://pypi.org/project/QtPy/)
# Values: pyqt5, pyside2, pyqt6, pyside6. [1](https://pypi.org/project/QtPy/)

if _has("PySide6"):
    os.environ["QT_API"] = "pyside6"
elif _has("PyQt6"):
    os.environ["QT_API"] = "pyqt6"
elif _has("PySide2"):
    os.environ["QT_API"] = "pyside2"
elif _has("PyQt5"):
    os.environ["QT_API"] = "pyqt5"
else:
    raise ImportError(
        "Kigo could not find a Qt binding.\n"
        "Install ONE of the following:\n"
        "  pip install PySide6   (recommended)\n"
        "  pip install PyQt6\n"
        "Optional (older Qt5 bindings):\n"
        "  pip install PySide2\n"
        "  pip install PyQt5\n"
        "Also install the shim:\n"
        "  pip install QtPy\n"
    )

# ------------------------------------------------------------
# Unified imports (binding-independent)
# ------------------------------------------------------------
from qtpy import QtCore, QtGui, QtWidgets  # QtPy abstraction [1](https://pypi.org/project/QtPy/)
from qtpy import API_NAME, QT_VERSION, PYQT_VERSION, PYSIDE_VERSION  # version helpers [1](https://pypi.org/project/QtPy/)

# Commonly used aliases
Signal = QtCore.Signal
Slot = QtCore.Slot
Property = QtCore.Property

# Optional: convenience re-exports (common classes used in Kigo)
QApplication = QtWidgets.QApplication
QWidget = QtWidgets.QWidget
QFrame = QtWidgets.QFrame
QVBoxLayout = QtWidgets.QVBoxLayout
QTimer = QtCore.QTimer
QObject = QtCore.QObject
Qt = QtCore.Qt

def qt_info() -> dict:
    """
    Useful for debug logs:
    - API_NAME tells which binding is active (e.g., 'PySide6' or 'PyQt6').
    - QT_VERSION is the underlying Qt version.
    - PYQT_VERSION/PYSIDE_VERSION show the binding versions (one will be None).
    """
    return {
        "api": API_NAME,
        "qt": QT_VERSION,
        "pyqt": PYQT_VERSION,
        "pyside": PYSIDE_VERSION,
        "qt_api_env": os.environ.get("QT_API"),
    }