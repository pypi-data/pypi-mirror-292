#version 430 core

layout (location=0) in vec3 position;
layout (location=1) in int zvx_id;
layout (location=2) in int face_id;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec2 uv;
out vec3 zvx_color;

const vec2 uv_coords[4] = vec2[4](
    vec2(0, 0), vec2(0, 1),
    vec2(1, 0), vec2(1, 1)
);

const int uv_indices[12] = int[12](
    1, 0, 2, 1, 2, 3,   // tex coords for vertices of even face_ids
    3, 0, 2, 3, 1, 0    // tex coords for vertices of odd face_ids
);

vec3 colorhash(float zvx_id) {
    vec3 p3 = fract(vec3(zvx_id*21.2) * vec3(0.1031, 0.103, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xxy + p3.yzz) * p3.zyx) + 0.05;
}

void main() {
    int ord_vertex = gl_VertexID % 6;
    int uv_index = ord_vertex + (face_id & 1) * 6;
    uv = uv_coords[uv_indices[uv_index]];
    zvx_color = colorhash(zvx_id);
    gl_Position = m_proj * m_view * m_model * vec4(position, 1.0f);
}