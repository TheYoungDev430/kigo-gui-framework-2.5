# examples/skins_demo.py

from kigo.app import App
from kigo.widgets import SkinManager, Card, TreeView, QPushButton
from kigo.qt import QtWidgets


def main():
    app = App(
        title="Kigo v1.8 – Skins Demo",
        size=(1100, 650),
        physics="No",
    )

    # Start with Neon
    SkinManager.apply("neon", window=app.root)

    root = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout(root)
    layout.setSpacing(16)

    # ---------------------------------------
    # Left: Tree (shows skin styling clearly)
    # ---------------------------------------
    tree_card = Card("Project Tree")
    tree = TreeView()
    tree.set_data({
        "Kigo": {
            "v1.8": ["Neon", "Retro", "Glass"],
            "Widgets": ["Tree", "Media", "Cards"],
            "Styling": ["CSS", "Skins", "Tokens"],
        }
    })
    tree_card.add_widget(tree)
    layout.addWidget(tree_card, 2)

    # ---------------------------------------
    # Right: Skin Switcher
    # ---------------------------------------
    skin_card = Card("Skins")

    btn_neon = QPushButton("Neon")
    btn_retro = QPushButton("Retro")
    btn_glass = QPushButton("Glass")

    btn_neon.clicked.connect(lambda: SkinManager.apply("neon", window=app.root))
    btn_retro.clicked.connect(lambda: SkinManager.apply("retro", window=app.root))
    btn_glass.clicked.connect(lambda: SkinManager.apply("glass", window=app.root))

    skin_card.add_widget(btn_neon)
    skin_card.add_widget(btn_retro)
    skin_card.add_widget(btn_glass)

    layout.addWidget(skin_card, 1)

    app.add_widget(root)
    app.run()


if __name__ == "__main__":
    main()