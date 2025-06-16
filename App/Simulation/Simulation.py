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
        if particle_spacing == None:
            self.particleSpacing = self.particleSize/2
        else:
            self.particleSpacing = particle_spacing
           
        self.smoothingRadius = 1.2
        self.SetOptimalSmoothingRadius()
        self.mass = 1

        self.targetDensity = 2.75
        self.pressureMultiplier = .2

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
        self.positions   = [glm.vec3(0.0) for _ in range(self.particleNumber)]
        self.velocities  = [glm.vec3(0.0) for _ in range(self.particleNumber)]
        self.properties = [0.0 for _ in range(self.particleNumber)]
        self.densities  = [0.0 for _ in range(self.particleNumber)]
       
        pprow = int(glm.sqrt(self.particleNumber))
        ppcol = (self.particleNumber - 1) // pprow + 1
       
        for i in range(self.particleNumber):
            x = (i % pprow - pprow // 2 + 0.5) * self.particleSpacing
            y = (i // pprow - ppcol // 2 + 0.5) * self.particleSpacing
            self.positions[i] = glm.vec3(x, y, 0)

               
    def Collisions(self, i):
        halfBoundSize = glm.vec3(self.boundSize / 2 - glm.vec3(1) * self.particleSize)
       
        if abs(self.positions[i].x) > halfBoundSize.x:
            self.positions[i].x = halfBoundSize.x * glm.sign(self.positions[i].x)
            self.velocities[i].x *= -1 * self.frictionCoefficient
        if abs(self.positions[i].y) > halfBoundSize.y:
            self.positions[i].y = halfBoundSize.y * glm.sign(self.positions[i].y)
            self.velocities[i].y *= -1 * self.frictionCoefficient
        # if abs(self.positions[i].z) > halfBoundSize.z:
        #     self.positions[i].z = halfBoundSize.z * glm.sign(self.positions[i].z)
        #     self.velocities[i].z *= -1 * self.frictionCoefficient
   
    def OnUpdate(self, dt: float):
        self.BuildSpatialMap()
        
        for i in range(len(self.positions)):
            #
            self.velocities[i] += self.gravity * dt
            self.densities[i] = self.CalculateDensity(i)
           
            #
            pressureForce = self.CalculatePressureForce(i)
            acceleration = pressureForce / self.densities[i]
            self.velocities[i] += acceleration * dt
           
            #
            self.positions[i] += self.velocities[i] * dt
            self.Collisions(i)
           
    def SmoothingKernel(self, radius, dist: float):
        if dist >= radius:
            return 0.0
        volume     = (math.pi * pow(radius, 4)) / 6
        return (radius - dist) * (radius - dist) / volume
   
    def SmoothingKernelDerivative(self, radius, dist):
        if dist >= radius:
            return 0
        scale = 12 / (pow(radius, 4) * math.pi)
        return (dist - radius) * scale
   
    def CalculateDensity(self, index: int):
        density = 0
        point = self.positions[index]
        cell = self.GetCellIndex(point)
    
        dx = -1
        while dx <= 1:
            dy = -1
            while dy <= 1:
                dz = -1
                while dz <= 1:
                    neighbour_cell = (cell[0] + dx, cell[1] + dy, cell[2] + dz)
                    if neighbour_cell in self.grid:
                        cell_indices = self.grid[neighbour_cell]
                        for j in range(len(cell_indices)):
                            other_index = cell_indices[j]
                            dist = glm.length(self.positions[other_index] - point)
                            influence = self.SmoothingKernel(self.smoothingRadius, dist)
                            density += self.mass * influence
                    dz += 1
                dy += 1
            dx += 1
    
        return density

   
    def CalculateProperty(self, point: glm.vec3):
        property = 0
       
        for i in range(self.particleNumber):
            dist = glm.length(self.positions[i] - point)
            influence = self.SmoothingKernel(self.smoothingRadius, dist)
            density = self.densities[i]
            property += self.properties[i] * influence * self.mass / density
        return property
           
    def CalculatePressureForce(self, i: int):
        force = glm.vec3(0)
        pi = self.positions[i]
        rho_i = self.densities[i]
        cell = self.GetCellIndex(pi)

        dx = -1
        while dx <= 1:
            dy = -1
            while dy <= 1:
                dz = -1
                while dz <= 1:
                    neighbour_cell = (cell[0] + dx, cell[1] + dy, cell[2] + dz)
                    if neighbour_cell in self.grid:
                        cell_indices = self.grid[neighbour_cell]
                        for j in range(len(cell_indices)):
                            other_index = cell_indices[j]
                            if other_index == i:
                                continue
                            pj = self.positions[other_index]
                            rho_j = self.densities[other_index]
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
                    dz += 1
                dy += 1
            dx += 1

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
        self.grid = {}
        
        for i, pos in enumerate(self.positions):
            cell = self.GetCellIndex(pos)
            if cell not in self.grid:
                self.grid[cell] = []
            self.grid[cell].append(i)
            
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