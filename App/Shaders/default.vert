#version 330 core

layout (location = 0) in vec3 aPos;

uniform mat4 uView;
uniform mat4 uProj;

out vec3 vPosView;

void main()
{
    vec4 posView4 = uView * vec4(aPos, 1.0);
    vPosView = posView4.xyz;
    gl_Position = uProj * posView4;
}
