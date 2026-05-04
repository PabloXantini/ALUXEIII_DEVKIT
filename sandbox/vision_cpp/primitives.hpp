#pragma once
#define _USE_MATH_DEFINES
#include <vector>
#include <cmath>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace vision {

class Primitives {
public:
    static std::vector<float> createCube() {
        return {
            -0.5f,-0.5f,-0.5f, 0,0,-1,  0.5f,0.5f,-0.5f, 0,0,-1,  0.5f,-0.5f,-0.5f, 0,0,-1,
             0.5f,0.5f,-0.5f, 0,0,-1, -0.5f,-0.5f,-0.5f, 0,0,-1, -0.5f,0.5f,-0.5f, 0,0,-1,

            -0.5f,-0.5f, 0.5f, 0,0, 1,  0.5f,-0.5f, 0.5f, 0,0, 1,  0.5f,0.5f, 0.5f, 0,0, 1,
             0.5f,0.5f, 0.5f, 0,0, 1, -0.5f,0.5f, 0.5f, 0,0, 1, -0.5f,-0.5f, 0.5f, 0,0, 1,

            -0.5f, 0.5f, 0.5f,-1,0, 0, -0.5f, 0.5f,-0.5f,-1,0, 0, -0.5f,-0.5f,-0.5f,-1,0, 0,
            -0.5f,-0.5f,-0.5f,-1,0, 0, -0.5f,-0.5f, 0.5f,-1,0, 0, -0.5f, 0.5f, 0.5f,-1,0, 0,

             0.5f, 0.5f, 0.5f, 1,0, 0,  0.5f,-0.5f,-0.5f, 1,0, 0,  0.5f, 0.5f,-0.5f, 1,0, 0,
             0.5f,-0.5f,-0.5f, 1,0, 0,  0.5f, 0.5f, 0.5f, 1,0, 0,  0.5f,-0.5f, 0.5f, 1,0, 0,

            -0.5f,-0.5f,-0.5f, 0,-1,0,  0.5f,-0.5f,-0.5f, 0,-1,0,  0.5f,-0.5f, 0.5f, 0,-1,0,
             0.5f,-0.5f, 0.5f, 0,-1,0, -0.5f,-0.5f, 0.5f, 0,-1,0, -0.5f,-0.5f,-0.5f, 0,-1,0,

            -0.5f, 0.5f,-0.5f, 0, 1,0,  0.5f, 0.5f, 0.5f, 0, 1,0,  0.5f, 0.5f,-0.5f, 0, 1,0,
             0.5f, 0.5f, 0.5f, 0, 1,0, -0.5f, 0.5f,-0.5f, 0, 1,0, -0.5f, 0.5f, 0.5f, 0, 1,0
        };
    }

    static std::vector<float> createCylinder(int segments = 24) {
        std::vector<float> data;

        for (int i = 0; i < segments; ++i) {
            float theta1 = (float)i / segments * 2.0f * (float)M_PI;
            float theta2 = (float)(i + 1) / segments * 2.0f * (float)M_PI;

            float x1 = 0.5f * cosf(theta1);
            float y1 = 0.5f * sinf(theta1);
            float x2 = 0.5f * cosf(theta2);
            float y2 = 0.5f * sinf(theta2);

            // Side quad (2 triangles)
            // Triangle 1
            data.insert(data.end(), { x1, y1, -0.5f, cosf(theta1), sinf(theta1), 0 });
            data.insert(data.end(), { x2, y2, -0.5f, cosf(theta2), sinf(theta2), 0 });
            data.insert(data.end(), { x2, y2,  0.5f, cosf(theta2), sinf(theta2), 0 });
            // Triangle 2
            data.insert(data.end(), { x1, y1, -0.5f, cosf(theta1), sinf(theta1), 0 });
            data.insert(data.end(), { x2, y2,  0.5f, cosf(theta2), sinf(theta2), 0 });
            data.insert(data.end(), { x1, y1,  0.5f, cosf(theta1), sinf(theta1), 0 });

            // Bottom cap triangle
            data.insert(data.end(), { 0, 0, -0.5f, 0, 0, -1 });
            data.insert(data.end(), { x2, y2, -0.5f, 0, 0, -1 });
            data.insert(data.end(), { x1, y1, -0.5f, 0, 0, -1 });

            // Top cap triangle
            data.insert(data.end(), { 0, 0,  0.5f, 0, 0, 1 });
            data.insert(data.end(), { x1, y1,  0.5f, 0, 0, 1 });
            data.insert(data.end(), { x2, y2,  0.5f, 0, 0, 1 });
        }
        return data;
    }
};

}
