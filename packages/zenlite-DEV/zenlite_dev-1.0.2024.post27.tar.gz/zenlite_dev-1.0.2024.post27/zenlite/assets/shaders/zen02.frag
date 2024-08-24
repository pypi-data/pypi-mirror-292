#version 430 core

layout (location=0) out vec4 fragColor;

in vec2 uv;
in vec3 zvx_color;

uniform sampler2D u_texture_0;

// gamma color correction for linear colorspace texture actions
const vec3 gamma = vec3(2.2);
const vec3 inverse_gamma = 1.0f / gamma;

void main() {
    vec3 texture_frag = texture(u_texture_0, uv).rgb;
    
    texture_frag = pow(texture_frag, gamma);
    
    texture_frag.rgb *= zvx_color;
    
    texture_frag = pow(texture_frag, inverse_gamma);
    
    fragColor = vec4(texture_frag, 1.0f);
}