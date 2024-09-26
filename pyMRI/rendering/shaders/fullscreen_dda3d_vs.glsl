#version 430

uniform WindowBlock {
    mat4 projection;
    mat4 view;
} window;

in vec2 in_pos;

out vec3 ray_pos;
out vec3 direction;

void main() {
    mat4 inv_view = inverse(window.view);

    float near_plane = window.projection[2][3] / (window.projection[2][2] - 1.0);
    float aspect = window.projection[1][1] / window.projection[0][0];
    float height = 1 / window.projection[1][1];
    float width = 1 / window.projection[0][0];

    ray_pos = (inv_view * vec4(vec2(width, height) * in_pos, -near_plane, 1.0)).xyz;
    direction = (inv_view * vec4(vec2(width, height) * in_pos, -near_plane, 0.0)).xyz;

    gl_Position = vec4(in_pos, 0.0, 1.0);
}
