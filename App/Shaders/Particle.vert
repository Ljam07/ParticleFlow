#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aInstancePoint;
layout (location = 2) in vec3 aInstanceColor;

uniform mat4 uView;
uniform mat4 uProj;
uniform float uParticleRadii;

out vec3 vPosView;
out vec3 vColor;

void main()
{
    // scale unit sphere then offset positions
    vec3 worldPos = (aPos * uParticleRadii) + aInstancePoint;
    vec4 posView4 = uView * vec4(worldPos, 1.0);
    vPosView = posView4.xyz;
    vColor = aInstanceColor;

    gl_Position = uProj * posView4;
}