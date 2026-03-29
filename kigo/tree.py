# kigo/tree.py
from __future__ import annotations
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

from kigo.qt import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt

Nested = Union[Dict[str, Any], List[Any], Tuple[Any, ...], str]

def _as_children(node: Any):
    # Normalize: dict => children, list/tuple => children, else => leaf
    if isinstance(node, dict):
        return list(node.items())
    if isinstance(node, (list, tuple)):
        return list(enumerate(node))
    return None


class TreeModel(QtGui.QStandardItemModel):
    """Hierarchical model (Name + optional Value columns)."""
    def __init__(self, headers: Sequence[str] = ("Name", "Value")):
        super().__init__()
        self.setHorizontalHeaderLabels(list(headers))

    def clear_and_set(self, data: Nested):
        self.removeRows(0, self.rowCount())
        root = self.invisibleRootItem()
        self._build(root, data)

    def _build(self, parent: QtGui.QStandardItem, data: Any):
        ch = _as_children(data)
        if ch is None:
            # leaf: store as value on parent second column if possible
            return

        if isinstance(data, dict):
            for k, v in data.items():
                name_item = QtGui.QStandardItem(str(k))
                val_item = QtGui.QStandardItem("" if _as_children(v) else str(v))
                parent.appendRow([name_item, val_item])
                if _as_children(v):
                    self._build(name_item, v)
        else:
            for _, v in ch:
                name_item = QtGui.QStandardItem(str(v) if _as_children(v) is None else "item")
                val_item = QtGui.QStandardItem("" if _as_children(v) else str(v))
                parent.appendRow([name_item, val_item])
                if _as_children(v):
                    self._build(name_item, v)


class TreeView(QtWidgets.QTreeView):
    """Tree/hierarchy view with convenient helpers."""
    def __init__(self, headers: Sequence[str] = ("Name", "Value")):
        super().__init__()
        self.qt_widget = self
        self.model_obj = TreeModel(headers=headers)
        self.setModel(self.model_obj)
        self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        self.header().setStretchLastSection(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

    def set_data(self, data: Nested):
        self.model_obj.clear_and_set(data)
        self.expandToDepth(1)

    def add_path(self, path: Sequence[str], value: Optional[str] = None):
        """
        Ensure nodes for path exist, create if missing.
        Example: add_path(["Animals","Mammals","Dog"], "Canis lupus familiaris")
        """
        parent = self.model_obj.invisibleRootItem()
        for i, name in enumerate(path):
            row = self._find_child_row(parent, name)
            if row is None:
                name_item = QtGui.QStandardItem(str(name))
                val_item = QtGui.QStandardItem("" if i < len(path) - 1 else (value or ""))
                parent.appendRow([name_item, val_item])
                parent = name_item
            else:
                parent = parent.child(row, 0)
                if i == len(path) - 1 and value is not None:
                    parent.parent().child(row, 1).setText(str(value))

    @staticmethod
    def _find_child_row(parent: QtGui.QStandardItem, name: str) -> Optional[int]:
        for r in range(parent.rowCount()):
            if parent.child(r, 0).text() == name:
                return r
        return None
