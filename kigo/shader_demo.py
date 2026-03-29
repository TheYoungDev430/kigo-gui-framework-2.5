from kigo.app import App
from kigo.ui import Window
from kigo.gpu import ShaderView

# choose ONE shader (fire/water presets from your page)
shader = fire
# shader = water

class Demo(App):
    def on_start(self):
        self.main_window = Window(title="Kigo VBO Shader Demo", size=(600, 400))
        self.view = ShaderView(fragment_shader=shader)
        self.main_window.set_content(self.view)
        self.main_window.show()

        self.t = 0.0
        self.schedule(self.update)

    def update(self, dt):
        self.t += dt
        self.view.set_uniform("time", self.t)

Demo(dev=True).run()