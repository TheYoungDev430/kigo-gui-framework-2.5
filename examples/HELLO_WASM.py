from kigo.app import App
from kigo.accelerate import hot
from kigo.ui import Window, VBox, Label, Button

@hot(wasm="mul42", module="math")
def heavy(x: int) -> int:
    return x * 42

class HelloWasm(App):
    def on_start(self):
        self.main_window = Window(
            title="Hello Kigo (WASM)",
            size=(500, 300)
        )

        self.result = Label("0")

        def run():
            value = self.call(heavy, 10)
            self.result.set_text(str(value))

        self.main_window.set_content(
            VBox(
                Label("Running in WASM mode"),
                self.result,
                Button("Run hot function", on_click=run),
                spacing=16
            )
        )

        self.main_window.show()

HelloWasm(mode="wasm", dev=True).run()