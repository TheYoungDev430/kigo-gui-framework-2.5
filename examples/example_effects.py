
# examples/example_effects.py
from kigo import App
from kigo.widgets import TouchButton, Card

physics = "Yes"  # global toggle

app = App(
    title="Kigo Effects (Bullet-driven)",
    physics=physics,
    physics_fps=120,
    pad_x_px=28,
    pad_y_px=28,
    pixels_per_meter=90.0,
    bullet_gui=False
)

# SPRING
spring_card = Card("spring (k=50, c=5)")
spring_card.add_widget(TouchButton("Springy"))
app.add_widget(spring_card, effect="spring", k=50.0, c=5.0)

# BOUNCE
bounce_card = Card("bounce (freq=1.0, force=14)")
bounce_card.add_widget(TouchButton("Bouncy"))
app.add_widget(bounce_card, effect="bounce", freq=1.0, force=14.0)

# FALL
fall_card = Card("fall (drops once)")
fall_card.add_widget(TouchButton("Falling"))
app.add_widget(fall_card, effect="fall")

# GRAVITY
gravity_card = Card("gravity (just gravity)")
gravity_card.add_widget(TouchButton("Gravity"))
app.add_widget(gravity_card, effect="gravity")

# MOVE (lateral)
move_card = Card("move (axis=x, freq=0.7, force=8)")
move_card.add_widget(TouchButton("Mover"))
app.add_widget(move_card, effect="move", axis="x", freq=0.7, force=8.0)

app.run()
