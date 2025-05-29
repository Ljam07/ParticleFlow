#version 330 core

in  vec3 vPosView;
in  vec3 vColor;
out vec4 FragColor;

void main()
{
    vec3 dx = dFdx(vPosView);
    vec3 dy = dFdy(vPosView);
    vec3 N  = normalize(cross(dx, dy));

    vec3 lightDir = normalize(vec3(-0.5, -0.5, -1.0));
    float diff    = max(dot(N, -lightDir), 0.0);

    vec3 amb   = 0.2 * vColor;
    vec3 diffC = diff * vColor;

    FragColor = vec4(amb + diffC, 1.0);
}
