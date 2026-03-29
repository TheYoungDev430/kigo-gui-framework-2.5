
from PyQt6.QtWidgets import QTextEdit
from kigo import App, TouchButton, Card, TouchScrollArea

app = App("Touch UI Demo")

editor = QTextEdit("Swipe to scroll...\n" * 50)
TouchScrollArea(editor)

card = Card("Touch Components Demo")
button = TouchButton("Tap Here")

card.add_widget(editor)
card.add_widget(button)

app.add_widget(card)
app.run()
