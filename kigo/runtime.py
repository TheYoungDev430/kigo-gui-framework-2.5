# SPDX-License-Identifier: Zlib

class Runtime:
    def __init__(self, mode="python"):
        if mode is None:
            mode = "python"

        if mode not in ("python", "wasm"):
            raise ValueError(" Duck is disappointed. mode must be 'python' or 'wasm'")

       