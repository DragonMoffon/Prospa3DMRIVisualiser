#version 430

const float inf = 1.0 / 0.0;

uniform mat4 inv_view;
uniform vec3 camera_data;

uniform sampler2D gradient;

uniform float density_scalar;
uniform float emission_brightness;

readonly buffer density_data {
    int i_width;
    int i_height;
    int i_depth;
    float width;
    float height;
    float depth;
    float density[];
};

in vec3 ray_pos;
in vec3 direction;

out vec4 colour_fs;

int get_idx(int x, int y, int z){

    return (min(z, i_depth-1) * i_width * i_height) + (min(y, i_height-1) * i_width) + min(x, i_width-1);
}

bool in_bounds(vec3 point){
    return (0 <= point.x && point.x <= width) && (0 <= point.y && point.y <= height) && (0 <= point.z && point.z <= depth);
}

float intersect_plane(vec3 R0, vec3 Rd, vec3 Pn, float D){
    float Vd = dot(Pn, Rd);
    if (Vd <= 0.0) return inf;

    float V0 = -(dot(Pn, R0) + D);
    float t = V0 / Vd;

    if (t < 0.0) return inf;

    return t;
}


// Get the pixel brightness at this point
vec4 dda(in vec3 enter_pos, in vec3 direction){
    vec3 cell_size = vec3(width, height, depth) / vec3(i_width, i_height, i_depth);

    ivec3 i = ivec3(trunc(enter_pos / cell_size));

    vec3 dt = cell_size / abs(direction);
    vec3 t = vec3(
         (direction.x >= 0.0? cell_size.x * (trunc(enter_pos.x / cell_size.x) + 1.0) - enter_pos.x : enter_pos.x - trunc(enter_pos.x / cell_size.x) * cell_size.x) / abs(direction.x),
         (direction.y >= 0.0? cell_size.y * (trunc(enter_pos.y / cell_size.y) + 1.0) - enter_pos.y : enter_pos.y - trunc(enter_pos.y / cell_size.y) * cell_size.y) / abs(direction.y),
         (direction.z >= 0.0? cell_size.z * (trunc(enter_pos.z / cell_size.z) + 1.0) - enter_pos.z : enter_pos.z - trunc(enter_pos.z / cell_size.z) * cell_size.z) / abs(direction.z)
    );

    ivec3 s = ivec3(
        direction.x >= 0 ? 1: -1,
        direction.y >= 0 ? 1: -1,
        direction.z >= 0 ? 1: -1
    );

    vec3 emission = vec3(0.0);
    float transmission = 1.0;
    float t_c = 0.0;
    float t_o = 0.0;
    ivec3 n = i;
    ivec3 l = i;
    while (true){
        if (t.x < min(t.y, t.z)) {
            t_c = t.x;
            t.x = t.x + dt.x;
            n.x = n.x + s.x;
        }
        else if (t.y < t.z) {
            t_c = t.y;
            t.y = t.y + dt.y;
            n.y = n.y + s.y;
        }
        else {
            t_c = t.z;
            t.z = t.z + dt.z;
            n.z = n.z + s.z;
        }

        int idx = get_idx(l.x, l.y, l.z);

        vec4 colour = texture(gradient, vec2(density[idx], 0.5));
        float voxel_density = density[idx] * colour.a * density_scalar;
        float voxel_transmition = exp(-voxel_density * (t_c - t_o));
        emission = emission + colour.rgb * transmission * (1 - voxel_transmition) * emission_brightness;
        transmission *= voxel_transmition;

        if (!(0 <= n.x && n.x < i_width && 0 <= n.y && n.y < i_height && 0 <= n.z && n.z < i_depth)){
            return vec4(emission, 1.0);  // colour based on density and transmission
            // return vec4(transmission);  // Darken based on transmission
            // return vec4(1 - transmission);  // Lighten based on transmission
        }

        l = n;
        t_o = t_c;
    }
}

void main() {
    vec3 size = vec3(width, height, depth);
    vec3 cell_size = size / vec3(i_width, i_height, i_depth);
    vec3 ray_dir = normalize(direction);

    float z_intersect = min(
        intersect_plane(ray_pos, ray_dir, vec3(0.0, 0.0, 1.0), 0.0),
        intersect_plane(ray_pos, ray_dir, vec3(0.0, 0.0, -1.0), depth)
    );
    vec3 z_point = ray_pos + ray_dir * z_intersect;
    z_point.z = trunc(z_point.z);

    float y_intersect = min(
        intersect_plane(ray_pos, ray_dir, vec3(0.0, 1.0, 0.0), 0.0),
        intersect_plane(ray_pos, ray_dir, vec3(0.0, -1.0, 0.0), height)
    );
    vec3 y_point = ray_pos + ray_dir * y_intersect;
    y_point.y = trunc(y_point.y);

    float x_intersect = min(
        intersect_plane(ray_pos, ray_dir, vec3(1.0, 0.0, 0.0), 0.0),
        intersect_plane(ray_pos, ray_dir, vec3(-1.0, 0.0, 0.0), width)
    );
    vec3 x_point = ray_pos + ray_dir * x_intersect;
    x_point.x = trunc(x_point.x);

    vec3 dda_start;
    if (in_bounds(ray_pos)){
        dda_start = ray_pos;
    }
    else if (isinf(x_intersect) && isinf(y_intersect) && isinf(z_intersect)){
        colour_fs = vec4(0.0);
        return;
    }
    else if (in_bounds(x_point)){
        dda_start = x_point;
    }
    else if (in_bounds(y_point)){
        dda_start = y_point;
    }
    else if (in_bounds(z_point)){
        dda_start = z_point;
    }
    else{
        colour_fs = vec4(0.0);
        return;
    }
    
    colour_fs = dda(dda_start, ray_dir);
    // colour_fs = vec4(mod(dda_start/cell_size, 1.0), 1.0) + 0.001 * dda(dda_start, ray_dir);
}
