# SPDX-License-Identifier: Zlib

from dataclasses import dataclass
from typing import Dict, Any
from wasmtime import Store, Module, Instance


@dataclass
class WasmModuleHandle:
    store: Store
    instance: Instance
    exports: Dict[str, Any]


class WasmExecutor:
    """
    Real WASM executor for Kigo.
    """

    def __init__(self, runtime):
        self.runtime = runtime
        self._modules: Dict[str, WasmModuleHandle] = {}

    def load_wasm_file(self, name: str, path: str):
        store = Store()
        module = Module.from_file(store.engine, path)
        instance = Instance(store, module, [])
        exports = instance.exports(store)
        self._modules[name] = WasmModuleHandle(store, instance, exports)

    def load_wat(self, name: str, wat_source: str):
        store = Store()
        module = Module(store.engine, wat_source)
        instance = Instance(store, module, [])
        exports = instance.exports(store)
        self._modules[name] = WasmModuleHandle(store, instance, exports)

    def has_export(self, module: str, export: str) -> bool:
        return module in self._modules and export in self._modules[module].exports

    def call(self, module: str, export: str, *args):
        self.runtime.wasm_calls += 1
        handle = self._modules[module]
        fn = handle.exports[export]
        return fn(handle.store, *args)
