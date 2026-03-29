# kigo/fx_quick.py
from __future__ import annotations
from kigo.qt import QtWidgets

def make_quick_widget(qml_source: str):
    """
    qml_source: QML text string
    Returns: QQuickWidget if available
    """
    from qtpy import QtCore, QtQuickWidgets

    w = QtQuickWidgets.QQuickWidget()
    w.setResizeMode(QtQuickWidgets.QQuickWidget.ResizeMode.SizeRootObjectToView)

    # load QML from data
    component = QtCore.QUrl("data:text/plain," + qml_source)
    w.setSource(component)
    return w