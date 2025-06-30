import glm

import math
import random

class Simulation:
    def __init__(self, particleNumber, particleSize, boundSize, frictionCoefficient, particleSpacing, gravity):
        # Ensure boundSize is always a glm.vec3
        if not isinstance(boundSize, glm.vec3):
            boundSize = glm.vec3(*boundSize)
        self._bound_size = boundSize
        self._particle_number = int(particleNumber)
        self._particle_size = particleSize

        self._friction_coefficient = frictionCoefficient
        self._gravity = gravity
        if particleSpacing is None:
            self._particle_spacing = self._particle_size / 2
        else:
            self._particle_spacing = particleSpacing

        self._smoothing_radius = 1.2
        self.SetOptimalSmoothingRadius()
        self._mass = 1

        self._target_density = 2.75
        self._pressure_multiplier = 2

        self.CreateParticles()

    def SetOptimalSmoothingRadius(self,
                                  useParticleSize: float = None,
                                  AC_ratio: float = 64.0):
        """
        Convenience: set self.smoothingRadius = h_opt based on given particleSize.
        If useParticleSize is None, uses self.particleSize.
        """
        if useParticleSize is None:
            useParticleSize = self._particle_size
        self._smoothing_radius = (AC_ratio ** (1.0 / 6.0)) * useParticleSize

    def ConvertDensityToPressure(self, density):
        densityError = density - self._target_density
        pressure = densityError * self._pressure_multiplier
        return pressure

    def CreateParticles(self):
        # Distribute in a 3D grid within the bounding box
        self._positions = []
        self._velocities = []
        self._properties = []
        self._densities = []

        # determine grid counts per axis (approx. cube root)
        count = self._particle_number
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
        offset = glm.vec3(self._particle_spacing)
        start = glm.vec3(- (nx-1) * self._particle_spacing / 2,
                         - (ny-1) * self._particle_spacing / 2,
                         - (nz-1) * self._particle_spacing / 2)
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if idx >= count:
                        break
                    pos = start + glm.vec3(i * self._particle_spacing,
                                             j * self._particle_spacing,
                                             k * self._particle_spacing)
                    self._positions.append(pos)
                    self._velocities.append(glm.vec3(0.0))
                    self._properties.append(0.0)
                    self._densities.append(0.0)
                    idx += 1
                if idx >= count:
                    break
            if idx >= count:
                break

    def Collisions(self, i):
        halfBoundSize = glm.vec3(self._bound_size / 2 - glm.vec3(1) * self._particle_size)
       
        if abs(self._positions[i].x) > halfBoundSize.x:
            self._positions[i].x = halfBoundSize.x * glm.sign(self._positions[i].x)
            self._velocities[i].x *= -1 * self._friction_coefficient
        if abs(self._positions[i].y) > halfBoundSize.y:
            self._positions[i].y = halfBoundSize.y * glm.sign(self._positions[i].y)
            self._velocities[i].y *= -1 * self._friction_coefficient
        if abs(self._positions[i].z) > halfBoundSize.z:
            self._positions[i].z = halfBoundSize.z * glm.sign(self._positions[i].z)
            self._velocities[i].z *= -1 * self._friction_coefficient
   
    def OnUpdate(self, dt: float):
        self.BuildSpatialMap()
        for i in range(len(self._positions)):
            # apply gravity
            self._velocities[i] += self._gravity * dt
            self._densities[i] = self.CalculateDensity(i)

            # pressure force
            pressureForce = self.CalculatePressureForce(i)
            # Prevent division by zero
            denom = self._densities[i] if abs(self._densities[i]) > 1e-8 else 1.0
            acceleration = pressureForce / denom
            self._velocities[i] += acceleration * dt

            # integrate
            self._positions[i] += self._velocities[i] * dt
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
        point = self._positions[index]
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
                        dist = glm.length(self._positions[j] - point)
                        influence = self.SmoothingKernel(self._smoothing_radius, dist)
                        density += self._mass * influence
        return density

    def CalculateProperty(self, point: glm.vec3):
        prop = 0.0
        for i in range(self._particle_number):
            dist = glm.length(self._positions[i] - point)
            influence = self.SmoothingKernel(self._smoothing_radius, dist)
            prop += self._properties[i] * influence * self._mass / self._densities[i]
        return prop

    def CalculatePressureForce(self, i: int):
        """ Inspired from Sebastian Lague's """
        force = glm.vec3(0)
        pi = self._positions[i]
        rho_i = self._densities[i]
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
                        pj = self._positions[j]
                        rho_j = self._densities[j]
                        if rho_j == 0:
                            continue
                        r = pj - pi
                        dist = glm.length(r)
                        if dist == 0:
                            continue
                        dir = r / dist
                        slope = self.SmoothingKernelDerivative(self._smoothing_radius, dist)
                        shared_pressure = self.CalculateAveragePressure(rho_j, rho_i)
                        force += shared_pressure * dir * slope * self._mass / rho_j
        return force

    def CalculateAveragePressure(self, dA, dB):
        pressureA = self.ConvertDensityToPressure(dA)
        pressureB = self.ConvertDensityToPressure(dB)
        return (pressureA + pressureB) / 2

    def UpdateDensities(self):
        for i in range(self._particle_number):
            self._densities[i] = self.CalculateDensity(i)

    def BuildSpatialMap(self):
        self.cellSize = self._smoothing_radius * 2
        # Fix: ensure cellSize is always positive and not NaN
        if not isinstance(self.cellSize, float) or self.cellSize <= 0 or math.isnan(self.cellSize):
            self.cellSize = 1e-6
        # compute grid dims
        nx = int(self._bound_size.x // self.cellSize) + 1
        ny = int(self._bound_size.y // self.cellSize) + 1
        nz = int(self._bound_size.z // self.cellSize) + 1
        # initialise 3D list
        self.grid = [
            [ [ [] for _ in range(nz) ] for _ in range(ny) ]
            for _ in range(nx)
        ]
        # populate
        for idx, pos in enumerate(self._positions):
            cx, cy, cz = self.GetCellIndex(pos)
            # Clamp indices to grid bounds
            cx = max(0, min(cx, nx-1))
            cy = max(0, min(cy, ny-1))
            cz = max(0, min(cz, nz-1))
            self.grid[cx][cy][cz].append(idx)

    def GetCellIndex(self, position):
        # Defensive: avoid NaN/zero cellSize
        if not hasattr(self, 'cellSize') or self.cellSize == 0 or math.isnan(self.cellSize):
            return (0, 0, 0)
        cell_x = int((position.x + self._bound_size.x / 2) // self.cellSize)
        cell_y = int((position.y + self._bound_size.y / 2) // self.cellSize)
        cell_z = int((position.z + self._bound_size.z / 2) // self.cellSize)
        return (cell_x, cell_y, cell_z)


    ## ACCESSED OUT OF CLASS

    def GetPoints(self) -> list[glm.vec3]:
        return self._positions

    def GetColors(self) -> list[glm.vec3]:
        colors = [glm.vec3(1)] * len(self._positions)
        return colors

    def SetParticleSize(self, size: float):
        self._particle_size = size

    def SetGravity(self, gravity: glm.vec3):
        self._gravity = gravity

    def SetBoundSize(self, boundSize):
        if not isinstance(boundSize, glm.vec3):
            boundSize = glm.vec3(*boundSize)
        self._bound_size = boundSize

    def SetFrictionCoefficient(self, m: float):
        self._friction_coefficient = m

    def SetPressureMultiplier(self, multiplier: float):
        self._pressure_multiplier = multiplier

    def SetGravity(self, gravity: glm.vec3):
        self._gravity = gravity
