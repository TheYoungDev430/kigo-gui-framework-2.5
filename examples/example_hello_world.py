
from kigo import App, TouchButton, Card

app = App("Hello Kigo", size=(500, 400))

card = Card("Welcome to Kigo")
btn = TouchButton("Click Me")

app.add_widget(card)
app.add_widget(btn)

app.run()
