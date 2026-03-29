# kigo/ui/shader.py
class ShaderWidget:
    def __init__(self, fragment, size=(300, 200)):
        self.fragment = fragment
        self.size = size
        self.uniforms = {}

    def set_uniform(self, name, value):
        self.uniforms[name] = value