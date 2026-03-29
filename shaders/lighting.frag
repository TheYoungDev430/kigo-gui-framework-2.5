#version 330

in vec2 uv;
out vec4 fragColor;

uniform vec3 lightColor;
uniform float intensity;

void main() {
    vec3 base = vec3(uv, 1.0);
    fragColor = vec4(base * lightColor * intensity, 1.0);
}