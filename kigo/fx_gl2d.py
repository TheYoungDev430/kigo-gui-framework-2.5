# kigo/fx_gl2d.py
from __future__ import annotations
from kigo.qt import QtWidgets, QtGui

def make_gl2d_view(scene: QtWidgets.QGraphicsScene) -> QtWidgets.QGraphicsView:
    view = QtWidgets.QGraphicsView(scene)
    view.setRenderHints(
        QtGui.QPainter.RenderHint.Antialiasing |
        QtGui.QPainter.RenderHint.SmoothPixmapTransform
    )

    # OpenGL viewport if available
    ogl = None
    try:
        from qtpy import QtOpenGLWidgets
        ogl = QtOpenGLWidgets.QOpenGLWidget()
    except Exception:
        ogl_cls = getattr(QtWidgets, "QOpenGLWidget", None)
        ogl = ogl_cls() if ogl_cls else None

    if ogl is not None:
        view.setViewport(ogl)  # hardware-accelerated rendering [2](https://felgo.com/doc/qt/graphicsview/)[3](https://doc.qt.io/qt-6//qgraphicsview.html)
        view.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)

    return view