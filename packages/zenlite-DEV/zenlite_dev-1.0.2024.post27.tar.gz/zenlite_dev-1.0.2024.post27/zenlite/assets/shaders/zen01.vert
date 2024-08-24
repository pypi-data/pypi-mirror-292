#version 430 core

layout(location=0) in vec3 position;
layout(location=1) in vec3 color;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec4 vertex_color;

void main() {
    gl_Position = m_proj * m_view * m_model * vec4(position, 1.0f);
    vertex_color = vec4(color, 1.0f);
}
