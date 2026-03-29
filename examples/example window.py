# examples/example_build_test.py

from kigo.app import App
from kigo.widgets import TouchButton, Card
from kigo.qt import qt_info

# Print which Qt backend is active
print("Qt backend info:", qt_info())

app = App(
    title="Kigo Build Test",
    physics="No"
)

card = Card("Kigo Build OK ✅")
btn = TouchButton("Hello from Kigo")

card.add_widget(btn)
app.add_widget(card)

app.run()