import glm

import math
import random

class Simulation:
    def __init__(self, particle_number, particle_size, boundSize, friction_coefficient, particle_spacing, gravity):
        # Ensure boundSize is always a glm.vec3
        if not isinstance(boundSize, glm.vec3):
            boundSize = glm.vec3(*boundSize)
        self.boundSize = boundSize
        self.isFirst = True
        self.particleNumber = int(particle_number)
        self.particleSize = particle_size

        self.frictionCoefficient = friction_coefficient
        self.gravity = gravity
        if particle_spacing is None:
            self.particleSpacing = self.particleSize / 2
        else:
            self.particleSpacing = particle_spacing

        self.smoothingRadius = 1.2
        self.SetOptimalSmoothingRadius()
        self.mass = 1

        self.targetDensity = 2.75
        self.pressureMultiplier = 2

        self.CreateParticles()

    def SetOptimalSmoothingRadius(self,
                                  useParticleSize: float = None,
                                  AC_ratio: float = 64.0):
        """
        Convenience: set self.smoothingRadius = h_opt based on given particleSize.
        If useParticleSize is None, uses self.particleSize.
        """
        if useParticleSize is None:
            useParticleSize = self.particleSize
        self.smoothingRadius = (AC_ratio ** (1.0 / 6.0)) * useParticleSize

    def ConvertDensityToPressure(self, density):
        densityError = density - self.targetDensity
        pressure = densityError * self.pressureMultiplier
        return pressure

    def CreateParticles(self):
        # Distribute in a 3D grid within the bounding box
        self.positions = []
        self.velocities = []
        self.properties = []
        self.densities = []

        # determine grid counts per axis (approx. cube root)
        count = self.particleNumber
        nx = int(round(count ** (1/3)))
        ny = nx
        nz = nx
        # adjust if too few
        while nx * ny * nz < count:
            nx += 1
            if nx * ny * nz >= count:
                break
            ny += 1
            if nx * ny * nz >= count:
                break
            nz += 1

        idx = 0
        offset = glm.vec3(self.particleSpacing)
        start = glm.vec3(- (nx-1) * self.particleSpacing / 2,
                         - (ny-1) * self.particleSpacing / 2,
                         - (nz-1) * self.particleSpacing / 2)
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if idx >= count:
                        break
                    pos = start + glm.vec3(i * self.particleSpacing,
                                             j * self.particleSpacing,
                                             k * self.particleSpacing)
                    self.positions.append(pos)
                    self.velocities.append(glm.vec3(0.0))
                    self.properties.append(0.0)
                    self.densities.append(0.0)
                    idx += 1
                if idx >= count:
                    break
            if idx >= count:
                break

    def Collisions(self, i):
        halfBoundSize = glm.vec3(self.boundSize / 2 - glm.vec3(1) * self.particleSize)
       
        if abs(self.positions[i].x) > halfBoundSize.x:
            self.positions[i].x = halfBoundSize.x * glm.sign(self.positions[i].x)
            self.velocities[i].x *= -1 * self.frictionCoefficient
        if abs(self.positions[i].y) > halfBoundSize.y:
            self.positions[i].y = halfBoundSize.y * glm.sign(self.positions[i].y)
            self.velocities[i].y *= -1 * self.frictionCoefficient
        if abs(self.positions[i].z) > halfBoundSize.z:
            self.positions[i].z = halfBoundSize.z * glm.sign(self.positions[i].z)
            self.velocities[i].z *= -1 * self.frictionCoefficient
   
    def OnUpdate(self, dt: float):
        self.BuildSpatialMap()

        for i in range(len(self.positions)):
            # apply gravity
            self.velocities[i] += self.gravity * dt
            self.densities[i] = self.CalculateDensity(i)

            # pressure force
            pressureForce = self.CalculatePressureForce(i)
            acceleration = pressureForce / self.densities[i]
            self.velocities[i] += acceleration * dt

            # integrate
            self.positions[i] += self.velocities[i] * dt
            self.Collisions(i)

    def SmoothingKernel(self, radius, dist: float):
        if dist >= radius:
            return 0.0
        volume = (math.pi * pow(radius, 4)) / 6
        return (radius - dist) * (radius - dist) / volume

    def SmoothingKernelDerivative(self, radius, dist):
        if dist >= radius:
            return 0
        scale = 12 / (pow(radius, 4) * math.pi)
        return (dist - radius) * scale

    def CalculateDensity(self, index: int):
        density = 0.0
        point = self.positions[index]
        cx, cy, cz = self.GetCellIndex(point)

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    nx = cx + dx
                    ny = cy + dy
                    nz = cz + dz
                    if not (0 <= nx < len(self.grid)
                            and 0 <= ny < len(self.grid[0])
                            and 0 <= nz < len(self.grid[0][0])):
                        continue
                    for j in self.grid[nx][ny][nz]:
                        dist = glm.length(self.positions[j] - point)
                        influence = self.SmoothingKernel(self.smoothingRadius, dist)
                        density += self.mass * influence
        return density

    def CalculateProperty(self, point: glm.vec3):
        prop = 0.0
        for i in range(self.particleNumber):
            dist = glm.length(self.positions[i] - point)
            influence = self.SmoothingKernel(self.smoothingRadius, dist)
            prop += self.properties[i] * influence * self.mass / self.densities[i]
        return prop

    def CalculatePressureForce(self, i: int):
        force = glm.vec3(0)
        pi = self.positions[i]
        rho_i = self.densities[i]
        cx, cy, cz = self.GetCellIndex(pi)

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    nx = cx + dx
                    ny = cy + dy
                    nz = cz + dz
                    if not (0 <= nx < len(self.grid)
                            and 0 <= ny < len(self.grid[0])
                            and 0 <= nz < len(self.grid[0][0])):
                        continue
                    for j in self.grid[nx][ny][nz]:
                        if j == i:
                            continue
                        pj = self.positions[j]
                        rho_j = self.densities[j]
                        if rho_j == 0:
                            continue
                        r = pj - pi
                        dist = glm.length(r)
                        if dist == 0:
                            continue
                        dir = r / dist
                        slope = self.SmoothingKernelDerivative(self.smoothingRadius, dist)
                        shared_pressure = self.CalculateAveragePressure(rho_j, rho_i)
                        force += shared_pressure * dir * slope * self.mass / rho_j
        return force

    def CalculateAveragePressure(self, dA, dB):
        pressureA = self.ConvertDensityToPressure(dA)
        pressureB = self.ConvertDensityToPressure(dB)
        return (pressureA + pressureB) / 2

    def UpdateDensities(self):
        for i in range(self.particleNumber):
            self.densities[i] = self.CalculateDensity(i)

    def BuildSpatialMap(self):
        self.cellSize = self.smoothingRadius * 2
        # compute grid dims
        nx = int(self.boundSize.x // self.cellSize) + 1
        ny = int(self.boundSize.y // self.cellSize) + 1
        nz = int(self.boundSize.z // self.cellSize) + 1
        # initialise 3D list
        self.grid = [
            [ [ [] for _ in range(nz) ] for _ in range(ny) ]
            for _ in range(nx)
        ]
        # populate
        for idx, pos in enumerate(self.positions):
            cx, cy, cz = self.GetCellIndex(pos)
            cx = max(0, min(cx, nx-1))
            cy = max(0, min(cy, ny-1))
            cz = max(0, min(cz, nz-1))
            self.grid[cx][cy][cz].append(idx)

    def GetCellIndex(self, position):
        cell_x = int((position.x + self.boundSize.x / 2) // self.cellSize)
        cell_y = int((position.y + self.boundSize.y / 2) // self.cellSize)
        cell_z = int((position.z + self.boundSize.z / 2) // self.cellSize)
        return (cell_x, cell_y, cell_z)

    ## ACCESSED OUT OF CLASS

    def GetPoints(self) -> list[glm.vec3]:
        return self.positions

    def GetColors(self) -> list[glm.vec3]:
        colors = [glm.vec3(1)] * len(self.positions)
        return colors

    def SetParticleSize(self, size: float):
        self.particleSize = size

    def SetGravity(self, gravity: glm.vec3):
        self.gravity = gravity

    def SetBoundSize(self, boundSize):
        if not isinstance(boundSize, glm.vec3):
            boundSize = glm.vec3(*boundSize)
        self.boundSize = boundSize

    def SetFrictionCoefficient(self, m: float):
        self.frictionCoefficient = m

    def SetPressureMultiplier(self, multiplier: float):
        self.pressureMultiplier = multiplier

    def SetGravity(self, gravity: glm.vec3):
        self.gravity = gravity
