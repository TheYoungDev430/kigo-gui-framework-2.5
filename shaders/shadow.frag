#version 330

in vec2 uv;
out vec4 fragColor;

uniform float softness;

void main() {
    float dist = length(uv - 0.5);
    float alpha = smoothstep(0.5, softness, dist);
    fragColor = vec4(0.0, 0.0, 0.0, 1.0 - alpha);
}