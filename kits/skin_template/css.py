# kits/skin_template/css.py

EXTRA_CSS = r"""
/* Override or extend base Kigo styles */

QFrame#kigo_card {
  border-radius: 16px;
}

QTreeView::item:selected {
  background: var(--accent);
  color: var(--onAccent);
}
"""