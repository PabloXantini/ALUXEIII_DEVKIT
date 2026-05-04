#version 330 core
out vec4 FragColor;
in vec2 TexCoords;
uniform sampler2D screenTexture;
uniform float k; // Factor de distorsión
uniform float zoom;

void main() {
    vec2 uv = TexCoords - 0.5;
    float r2 = dot(uv, uv);
    vec2 distortedUV = uv * (1.0 + k * r2) / zoom + 0.5;
    
    if (distortedUV.x < 0.0 || distortedUV.x > 1.0 || distortedUV.y < 0.0 || distortedUV.y > 1.0) {
        FragColor = vec4(0.0, 0.0, 0.0, 1.0);
    } else {
        FragColor = texture(screenTexture, distortedUV);
    }
}
