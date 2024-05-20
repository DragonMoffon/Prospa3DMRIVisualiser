#version 430

in vec2 in_pos;

out vec2 vs_pos;

void main() {
    gl_Position = vec4(in_pos, 0.0, 1.0);
    vs_pos = in_pos;
}
