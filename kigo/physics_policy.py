# kigo/physics_policy.py
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PhysicsAccel:
    render_hw_accel: bool   # OpenGL GUI rendering
    compute_hw_accel: bool  # GPU physics stepping (likely false for PyBullet)

def detect_pybullet_accel(use_gui: bool) -> PhysicsAccel:
    # Rendering: GUI implies OpenGL window rendering (hardware accelerated) [5](https://libraries.io/pypi/pybullet-rendering)[6](https://raw.githubusercontent.com/bulletphysics/bullet3/master/docs/pybullet_quickstartguide.pdf)
    render_hw = bool(use_gui)

    # Compute GPU: not enabled in PyBullet today (policy says: do NOT pretend) [4](https://www.nvidia.com/content/GTC/documents/1077_GTC09.pdf)
    compute_hw = False

    return PhysicsAccel(render_hw_accel=render_hw, compute_hw_accel=compute_hw)