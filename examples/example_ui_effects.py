
# examples/example_ui_physics.py

import sys
import time

from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QMouseEvent

from kigo.physics import (
    UIPhysicsWorld,
    UIBody,
    SnapConstraint,
    OrbitConstraint,
)

# ------------------------------------------------------------
# Simple widget wrapper that binds a QLabel to a UIBody
# ------------------------------------------------------------

class PhysicsLabel(QLabel):
    def __init__(self, text: str, body: UIBody, world: UIPhysicsWorld, parent=None):
        super().__init__(text, parent)
        self.body = body
        self.world = world

        self.setStyleSheet("""
            QLabel {
                background: #2d89ef;
                color: white;
                padding: 8px 14px;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        self.adjustSize()
        self.setMouseTracking(True)

    # ---- mouse → physics interaction ----
    def mousePressEvent(self, e: QMouseEvent):
        if e.buttons():
            self.world.drag.pointer_down(self.body, e.globalPosition().x(), e.globalPosition().y())

    def mouseMoveEvent(self, e: QMouseEvent):
        self.world.drag.pointer_move(e.globalPosition().x(), e.globalPosition().y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        self.world.drag.pointer_up()

    def sync_from_body(self):
        self.move(int(self.body.x), int(self.body.y))


# ------------------------------------------------------------
# Main demo window
# ------------------------------------------------------------

class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kigo v1.4 UI Physics Demo")
        self.resize(900, 600)

        # ---- Physics world ----
        self.world = UIPhysicsWorld()
        self.world.set_bounds(0, 0, self.width(), self.height(), bounce=0.2)

        # ---- Draggable floating panel ----
        panel_body = UIBody(
            x=120, y=120,
            w=160, h=48,
            damping=0.94
        )
        self.world.add_body(panel_body)
        self.world.add_constraint(
            panel_body,
            SnapConstraint(grid=16, threshold=12, snap_to_centers=True)
        )

        self.panel = PhysicsLabel("Drag me (snap + throw)", panel_body, self.world, self)

        # ---- Center anchor (static) ----
        anchor_body = UIBody(
            x=420, y=260,
            w=120, h=40,
            mode="static"
        )
        self.world.add_body(anchor_body)
        self.anchor = PhysicsLabel("Anchor", anchor_body, self.world, self)
        self.anchor.setStyleSheet("QLabel { background: #444; color: #eee; padding: 8px; }")

        # ---- Orbiting widget ----
        orbiter_body = UIBody(
            x=500, y=260,
            w=110, h=40,
            damping=0.98
        )
        self.world.add_body(orbiter_body)
        self.world.add_constraint(
            orbiter_body,
            OrbitConstraint(
                target=anchor_body,
                radius=140,
                angular_velocity=1.2,
                soft=True
            )
        )
        self.orbiter = PhysicsLabel("Orbiting", orbiter_body, self.world, self)
        self.orbiter.setStyleSheet("QLabel { background: #00a300; color: white; padding: 8px; }")

        # ---- render timer ----
        self._last = time.perf_counter()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16)  # ~60 FPS

    def tick(self):
        now = time.perf_counter()
        dt = now - self._last
        self._last = now

        self.world.step(dt)

        # sync widgets from physics bodies
        self.panel.sync_from_body()
        self.anchor.sync_from_body()
        self.orbiter.sync_from_body()


# ------------------------------------------------------------
# Run
# ------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Demo()
    win.show()
    sys.exit(app.exec())
