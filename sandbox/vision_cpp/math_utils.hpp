#pragma once

#include <cmath>

namespace glm {

struct vec3 {
    float x, y, z;
    vec3(float _x = 0, float _y = 0, float _z = 0) : x(_x), y(_y), z(_z) {}
    vec3 operator+(const vec3& other) const { return vec3(x + other.x, y + other.y, z + other.z); }
    vec3 operator-(const vec3& other) const { return vec3(x - other.x, y - other.y, z - other.z); }
};

struct mat4 {
    float m[16];
    mat4() { for(int i=0; i<16; i++) m[i] = 0; m[0]=m[5]=m[10]=m[15]=1; }
    const float* ptr() const { return m; }
};

inline mat4 perspective(float fov, float aspect, float zNear, float zFar) {
    mat4 res;
    float f = 1.0f / tan(fov / 2.0f);
    res.m[0] = f / aspect;
    res.m[5] = f;
    res.m[10] = (zFar + zNear) / (zNear - zFar);
    res.m[11] = -1.0f;
    res.m[14] = (2.0f * zFar * zNear) / (zNear - zFar);
    res.m[15] = 0;
    return res;
}

inline mat4 translate(const mat4& m, const vec3& v) {
    mat4 res = m;
    res.m[12] = m.m[0] * v.x + m.m[4] * v.y + m.m[8] * v.z + m.m[12];
    res.m[13] = m.m[1] * v.x + m.m[5] * v.y + m.m[9] * v.z + m.m[13];
    res.m[14] = m.m[2] * v.x + m.m[6] * v.y + m.m[10] * v.z + m.m[14];
    res.m[15] = m.m[3] * v.x + m.m[7] * v.y + m.m[11] * v.z + m.m[15];
    return res;
}

inline mat4 scale(const mat4& m, const vec3& v) {
    mat4 res = m;
    res.m[0] *= v.x; res.m[1] *= v.x; res.m[2] *= v.x; res.m[3] *= v.x;
    res.m[4] *= v.y; res.m[5] *= v.y; res.m[6] *= v.y; res.m[7] *= v.y;
    res.m[8] *= v.z; res.m[9] *= v.z; res.m[10] *= v.z; res.m[11] *= v.z;
    return res;
}

inline mat4 rotate_y(const mat4& m, float angle) {
    mat4 res = m;
    float c = cos(angle);
    float s = sin(angle);
    float m0 = m.m[0], m1 = m.m[1], m2 = m.m[2], m3 = m.m[3];
    float m8 = m.m[8], m9 = m.m[9], m10 = m.m[10], m11 = m.m[11];
    res.m[0] = m0 * c - m8 * s; res.m[1] = m1 * c - m9 * s; res.m[2] = m2 * c - m10 * s; res.m[3] = m3 * c - m11 * s;
    res.m[8] = m0 * s + m8 * c; res.m[9] = m1 * s + m9 * c; res.m[10] = m2 * s + m10 * c; res.m[11] = m3 * s + m11 * c;
    return res;
}

inline mat4 rotate_x(const mat4& m, float angle) {
    mat4 res = m;
    float c = cos(angle);
    float s = sin(angle);
    float m4 = m.m[4], m5 = m.m[5], m6 = m.m[6], m7 = m.m[7];
    float m8 = m.m[8], m9 = m.m[9], m10 = m.m[10], m11 = m.m[11];
    res.m[4] = m4 * c + m8 * s; res.m[5] = m5 * c + m9 * s; res.m[6] = m6 * c + m10 * s; res.m[7] = m7 * c + m11 * s;
    res.m[8] = -m4 * s + m8 * c; res.m[9] = -m5 * s + m9 * c; res.m[10] = -m6 * s + m10 * c; res.m[11] = -m7 * s + m11 * c;
    return res;
}

inline vec3 normalize(vec3 v) {
    float len = sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    if (len > 0) return vec3(v.x / len, v.y / len, v.z / len);
    return v;
}

inline vec3 cross(vec3 a, vec3 b) {
    return vec3(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x);
}

inline float dot(vec3 a, vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

inline mat4 lookAt(vec3 eye, vec3 center, vec3 up) {
    vec3 f = normalize(vec3(center.x - eye.x, center.y - eye.y, center.z - eye.z));
    vec3 s = normalize(cross(f, up));
    vec3 u = cross(s, f);

    mat4 res;
    res.m[0] = s.x;
    res.m[4] = s.y;
    res.m[8] = s.z;
    res.m[1] = u.x;
    res.m[5] = u.y;
    res.m[9] = u.z;
    res.m[2] = -f.x;
    res.m[6] = -f.y;
    res.m[10] = -f.z;
    res.m[12] = -dot(s, eye);
    res.m[13] = -dot(u, eye);
    res.m[14] = dot(f, eye);
    return res;
}

inline mat4 operator*(const mat4& a, const mat4& b) {
    mat4 res;
    for (int r = 0; r < 4; r++) {
        for (int c = 0; c < 4; c++) {
            res.m[c * 4 + r] = 0;
            for (int k = 0; k < 4; k++) {
                res.m[c * 4 + r] += a.m[k * 4 + r] * b.m[c * 4 + k];
            }
        }
    }
    return res;
}

}
