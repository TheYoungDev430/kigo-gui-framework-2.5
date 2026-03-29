# examples/demo_css_media_tree.py

from kigo.app import App
from kigo.widgets import (
    StyleManager,
    KIGO_BASE_CSS,
    KIGO_TOKENS_DARK,
    KIGO_TOKENS_LIGHT,
    TreeView,
    VideoPlayerWidget,
    Card,
    QPushButton,
)
from kigo.qt import QtWidgets


def main():
    # --------------------------------------------------
    # Create Kigo app (no physics needed)
    # --------------------------------------------------
    app = App(
        title="Kigo Demo – CSS + Media + Tree",
        size=(1200, 700),
        physics="No",
    )

    # --------------------------------------------------
    # Apply CSS-like styling (dark theme)
    # --------------------------------------------------
    StyleManager.apply(KIGO_BASE_CSS, tokens=KIGO_TOKENS_DARK)

    root = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout(root)
    layout.setSpacing(16)

    # ==================================================
    # LEFT: Tree / Hierarchy
    # ==================================================
    tree_card = Card("Hierarchy / Tree")
    tree = TreeView()

    tree.set_data({
        "Company": {
            "Engineering": {
                "Frontend": ["UI", "Themes"],
                "Backend": ["API", "Database"],
            },
            "Sales": {
                "APAC": ["India", "SEA"],
                "EMEA": ["EU", "MEA"],
            },
            "Support": {
                "Tier 1": ["Tickets", "Chat"],
                "Tier 2": ["Escalations"],
            }
        }
    })

    tree_card.add_widget(tree)
    layout.addWidget(tree_card, 1)

    # ==================================================
    # RIGHT: Media Player
    # ==================================================
    media_card = Card("Video Player")

    # ⚠️ Change this path to an actual video on your machine
    VIDEO_PATH = r"C:\path\to\your\video.mp4"

    try:
        video = VideoPlayerWidget(VIDEO_PATH)
        media_card.add_widget(video)
    except ImportError as e:
        # Graceful fallback if QtMultimedia is missing
        error_label = QtWidgets.QLabel(
            "QtMultimedia not available.\n"
            "Install a Qt build with multimedia support."
        )
        error_label.setWordWrap(True)
        media_card.add_widget(error_label)

    layout.addWidget(media_card, 2)

    # ==================================================
    # TOP-RIGHT: Theme Toggle (CSS demo)
    # ==================================================
    btn_row = QtWidgets.QHBoxLayout()
    btn_wrap = QtWidgets.QWidget()
    btn_wrap.setLayout(btn_row)

    dark_btn = QPushButton("Dark Theme")
    light_btn = QPushButton("Light Theme")

    dark_btn.setProperty("kigoClass", "primary")
    light_btn.setProperty("kigoClass", "danger")

    def set_dark():
        StyleManager.apply(KIGO_BASE_CSS, tokens=KIGO_TOKENS_DARK)
        StyleManager.refresh_widget(dark_btn)
        StyleManager.refresh_widget(light_btn)

    def set_light():
        StyleManager.apply(KIGO_BASE_CSS, tokens=KIGO_TOKENS_LIGHT)
        StyleManager.refresh_widget(dark_btn)
        StyleManager.refresh_widget(light_btn)

    dark_btn.clicked.connect(set_dark)
    light_btn.clicked.connect(set_light)

    btn_row.addWidget(dark_btn)
    btn_row.addWidget(light_btn)

    media_card.add_widget(btn_wrap)

    # --------------------------------------------------
    # Add everything to Kigo App
    # --------------------------------------------------
    app.add_widget(root)
    app.run()


if __name__ == "__main__":
    main()
