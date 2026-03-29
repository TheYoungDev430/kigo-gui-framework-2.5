# SPDX-License-Identifier: Zlib

def hot(wasm: str | None = None, module: str = "default"):
    """
    Marks a function as eligible for WASM acceleration.
    """
    def decorate(fn):
        fn.__kigo_hot__ = True
        fn.__kigo_wasm_export__ = wasm or fn.__name__
        fn.__kigo_wasm_module__ = module
        return fn
    return decorate