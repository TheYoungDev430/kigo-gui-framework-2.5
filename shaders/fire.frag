// fire.frag
varying highp vec2 qt_TexCoord0;
uniform highp float time;
uniform lowp float qt_Opacity;

// hash + noise for procedural fire
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);

    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(a, b, u.x)
         + (c - a) * u.y * (1.0 - u.x)
         + (d - b) * u.x * u.y;
}

void main() {
    vec2 uv = qt_TexCoord0;

    // fire moves upward
    uv.y += time * 0.8;

    // stretch vertically
    uv *= vec2(1.0, 2.5);

    float n = noise(uv * 6.0);

    // flame shape
    float intensity = smoothstep(0.2, 1.0, n - uv.y);

    vec3 color = mix(
        vec3(1.0, 0.2, 0.0),   // red/orange
        vec3(1.0, 1.0, 0.0),   // yellow
        intensity
    );

    gl_FragColor = vec4(color * intensity, intensity) * qt_Opacity;
}