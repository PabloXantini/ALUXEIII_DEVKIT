#version 330 core
out vec4 FragColor;
in vec3 FragPos;
in vec3 Normal;
in vec3 vPos;

uniform vec4 color;
uniform int isCircle;

uniform vec3 lightPos;
uniform float ambient;
uniform float diffuseIntensity;

void main() {
    if (isCircle == 1) {
        float d = length(vPos.xy);
        if (d > 0.5) discard;
    }

    // Dynamic lighting
    vec3 lightDir = normalize(lightPos - FragPos); 
    vec3 norm = normalize(Normal);
    
    if (isCircle == 1) {
        float z = sqrt(max(0.0, 0.25 - vPos.x*vPos.x - vPos.y*vPos.y));
        norm = normalize(vec3(vPos.x, vPos.y, z));
    }
    
    float diff = max(dot(norm, lightDir), 0.0) * diffuseIntensity; 
    
    vec3 result = color.rgb * (ambient + diff);
    FragColor = vec4(result, color.a);
}
