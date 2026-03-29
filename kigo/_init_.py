# SPDX-License-Identifier: Zlib

"""
Kigo GUI Framework
"""

__version__ = "2.2"

# Optional dev utilities (imported lazily by users)
try:
    from kigo.dev import AppHotReloader  # noqa: F401
except Exception:
    AppHotReloader = None

__all__ = [
    "__version__",
    "AppHotReloader",
]