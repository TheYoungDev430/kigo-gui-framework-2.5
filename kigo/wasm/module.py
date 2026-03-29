# SPDX-License-Identifier: Zlib

WASM_MODULES = {
    "math": r"""
    (module
      (func (export "mul42") (param i32) (result i32)
        local.get 0
        i32.const 42
        i32.mul
