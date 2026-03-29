# SPDX-License-Identifier: Zlib
# kigo/gpu.py

from __future__ import annotations
from typing import Any, Dict, Optional

from kigo.qt import QtCore, QtWidgets

# QtPy provides these modules when OpenGL is available
try:
    from qtpy import QtOpenGLWidgets, QtOpenGL, QtGui
except Exception:
    QtOpenGLWidgets = None
    QtOpenGL = None
    QtGui = None


_VERTEX_GLSL_120 = r"""
#version 120
attribute vec2 a_pos;
attribute vec2 a_uv;
varying vec2 v_uv;

void main() {
    v_uv = a_uv;
    gl_Position = vec4(a_pos.xy, 0.0, 1.0);
}
"""


def _wrap_fragment_glsl_120(user_fragment: str) -> str:
    """
    Accepts your preset fragments (that use varying v_uv and gl_FragColor),
    ensures they compile with GLSL 120 by NOT rewriting your code.
    Requirement: user fragment must declare:
        varying highp vec2 v_uv;  (or varying vec2 v_uv;)
    and must write gl_FragColor.
    """
    s = (user_fragment or "").strip()
    if not s:
        # fallback shader (solid magenta)
        return r"""
        #version 120
        varying vec2 v_uv;
        uniform float time;
        void main() { gl_FragColor = vec4(1.0, 0.0, 1.0, 1.0); }
        """
    if not s.startswith("#version"):
        s = "#version 120\n" + s
    return s


class _GLShaderWidget(QtOpenGLWidgets.QOpenGLWidget):  # type: ignore
    """
    Internal OpenGL widget that renders a fullscreen quad using VBO+VAO.
    """

    def __init__(self, fragment_shader: str, parent=None):
        super().__init__(parent)

        # Prefer compatibility-style GLSL 120 so your existing presets compile
        fmt = self.format()
        fmt.setVersion(2, 1)
        fmt.setProfile(fmt.OpenGLContextProfile.NoProfile)
        self.setFormat(fmt)  # QOpenGLWidget supports setFormat [2](https://doc.qt.io/qtforpython-6.5/PySide6/QtOpenGLWidgets/QOpenGLWidget.html)

        self._frag_src_user = fragment_shader
        self._uniforms: Dict[str, Any] = {}

        self._program = None
        self._vao = None
        self._vbo = None
        self._gl = None

        # attribute locations (cached)
        self._loc_pos = -1
        self._loc_uv = -1

    def set_uniform(self, name: str, value: Any):
        self._uniforms[name] = value
        self.update()

    def initializeGL(self):
        # QOpenGLWidget makes the context current here [2](https://doc.qt.io/qtforpython-6.5/PySide6/QtOpenGLWidgets/QOpenGLWidget.html)[3](https://doc.qt.io/qt-6/qopenglwidget.html)
        self._gl = self.context().functions()

        # Create program
        self._program = QtOpenGL.QOpenGLShaderProgram(self)  # [4](https://doc.qt.io/qt-6/qopenglshaderprogram.html)
        ok_v = self._program.addShaderFromSourceCode(
            QtOpenGL.QOpenGLShader.ShaderTypeBit.Vertex, _VERTEX_GLSL_120
        )
        frag_src = _wrap_fragment_glsl_120(self._frag_src_user)
        ok_f = self._program.addShaderFromSourceCode(
            QtOpenGL.QOpenGLShader.ShaderTypeBit.Fragment, frag_src
        )

        if not ok_v or not ok_f or not self._program.link():
            # If shader fails, draw clear color only; keep app running
            self._program = None
            self._gl.glClearColor(0.2, 0.0, 0.2, 1.0)
            return

        self._program.bind()

        # Attribute locations
        self._loc_pos = self._program.attributeLocation("a_pos")
        self._loc_uv = self._program.attributeLocation("a_uv")

        # Fullscreen quad (triangle strip): 4 vertices
        # a_pos(x,y), a_uv(u,v)
        data = [
            -1.0, -1.0,  0.0, 0.0,
             1.0, -1.0,  1.0, 0.0,
            -1.0,  1.0,  0.0, 1.0,
             1.0,  1.0,  1.0, 1.0,
        ]

        # VAO (remembers VBO + attribute bindings) [5](https://wikis.khronos.org/opengl/Tutorial2:_VAOs,_VBOs,_Vertex_and_Fragment_Shaders_%28C_/_SDL%29)
        self._vao = QtOpenGL.QOpenGLVertexArrayObject(self)
        self._vao.create()
        self._vao.bind()

        # VBO (stores vertex data on GPU) [5](https://wikis.khronos.org/opengl/Tutorial2:_VAOs,_VBOs,_Vertex_and_Fragment_Shaders_%28C_/_SDL%29)
        self._vbo = QtOpenGL.QOpenGLBuffer(QtOpenGL.QOpenGLBuffer.Type.VertexBuffer)
        self._vbo.create()
        self._vbo.bind()
        self._vbo.setUsagePattern(QtOpenGL.QOpenGLBuffer.UsagePattern.StaticDraw)
        self._vbo.allocate(bytes(bytearray(float(x).hex().encode() for x in [])))  # placeholder

        # Qt buffer allocate wants bytes; easiest is to use QByteArray
        arr = QtCore.QByteArray()
        arr.resize(4 * 4 * 4)  # 4 vertices * 4 floats * 4 bytes
        # write float32 into QByteArray
        import struct
        packed = struct.pack("<16f", *data)
        for i, b in enumerate(packed):
            arr[i] = b
        self._vbo.allocate(arr)

        stride = 4 * 4  # 4 floats per vertex

        # Position attribute
        self._program.enableAttributeArray(self._loc_pos)
        self._program.setAttributeBuffer(self._loc_pos, QtOpenGL.GL_FLOAT, 0, 2, stride)

        # UV attribute
        self._program.enableAttributeArray(self._loc_uv)
        self._program.setAttributeBuffer(self._loc_uv, QtOpenGL.GL_FLOAT, 2 * 4, 2, stride)

        self._vbo.release()
        self._vao.release()
        self._program.release()

        self._gl.glClearColor(0.0, 0.0, 0.0, 1.0)

    def resizeGL(self, w: int, h: int):
        if self._gl:
            self._gl.glViewport(0, 0, w, h)

    def paintGL(self):
        if not self._gl:
            return

        self._gl.glClear(self._gl.GL_COLOR_BUFFER_BIT)

        if not self._program or not self._vao:
            return

        self._program.bind()
        self._vao.bind()

        # Push uniforms
        # (Only sets float/int; extend later if needed)
        for k, v in self._uniforms.items():
            try:
                if isinstance(v, (int,)):
                    self._program.setUniformValue(k, int(v))
                else:
                    self._program.setUniformValue(k, float(v))
            except Exception:
                pass

        # Draw triangle strip quad
        self._gl.glDrawArrays(self._gl.GL_TRIANGLE_STRIP, 0, 4)

        self._vao.release()
        self._program.release()


class ShaderView:
    """
    Kigo-facing widget wrapper.
    User code stays Kigo-style:
        view = ShaderView(fragment_shader=shader)
        view.set_uniform("time", t)
    """

    def __init__(self, fragment_shader: str):
        if QtOpenGLWidgets is None or QtOpenGL is None:
            raise RuntimeError("OpenGL backend not available")

        self.qt_widget = _GLShaderWidget(fragment_shader)

    def set_uniform(self, name: str, value: Any):
        self.qt_widget.set_uniform(name, value)

