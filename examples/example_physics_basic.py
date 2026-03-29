
from PyQt6.QtWidgets import QApplication
from kigo.physics import PhysicsEngine

app = QApplication([])

engine = PhysicsEngine(use_gui=True, fps=120)
engine.setup_scene()

cube = engine.spawn_object("cube", position=(0, 0, 2), size=0.3)
sphere = engine.spawn_object("sphere", position=(1, 0, 2), size=0.2)

engine.toggle_simulation(True)

def on_frame():
    print("Cube height:", engine.get_pos(cube)[2])

engine.frame_updated.connect(on_frame)

app.exec()
