#version 330

in vec2 uv;
out vec4 fragColor;

uniform float time;

void main() {
    float wave = sin((uv.x + time) * 10.0) * 0.05;
    vec3 color = vec3(0.0, 0.4, 0.7) + wave;
    fragColor = vec4(color, 1.0);
}