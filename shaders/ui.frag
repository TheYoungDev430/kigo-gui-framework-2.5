#version 330

in vec2 uv;
out vec4 fragColor;

uniform vec3 tint;

void main() {
    float noise = fract(sin(dot(uv, vec2(12.9898,78.233))) * 43758.5453);
    fragColor = vec4(tint + noise * 0.02, 0.9);
}