#version 330 core

in  vec3 vPosView;
out vec4 FragColor;

void main()
{
    // approximate face‐normal from derivatives of view‐space position
    vec3 dx = dFdx(vPosView);
    vec3 dy = dFdy(vPosView);
    vec3 N  = normalize(cross(dx, dy));

    vec3 lightDir = normalize(vec3(-0.5, -0.5, -1.0));
    float diff    = max(dot(N, -lightDir), 0.0);

    vec3 baseCol = vec3(1.0, 0.4, 0.2);
    vec3 amb     = 0.2 * baseCol;
    vec3 diffC   = diff * baseCol;

    FragColor = vec4(amb + diffC, 1.0);
}
