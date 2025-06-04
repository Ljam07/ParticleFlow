import glm

import math

class Simulation:
    def __init__(self, particleNum: int = 5, particleSize = 1, boundSize = glm.vec3(3), fCoefficient = 0.7, particleSpacing = None):
        self.particleNumber = int(particleNum)
        self.particleSize = particleSize
        self.boundSize = boundSize
        self.frictionCoefficient = fCoefficient
        self.gravity = glm.vec3(0)#glm.vec3(0, -9.8, 0)
        if particleSpacing == None:
            self.particleSpacing = self.particleSize/2
        else:
            self.particleSpacing = particleSpacing
            
        self.smoothingRadius = 1.2
        self.mass = 1

        self.targetDensity = 2.75
        self.pressureMultiplier = 5

        self.CreateParticles()

            
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
        ppcol = (self.particleNumber - 1) / pprow + 1
        
        for i in range(self.particleNumber):
            x = (i % pprow - pprow / 2 + 0.5) * self.particleSpacing
            y = (i / pprow - ppcol / 2 + 0.5) * self.particleSpacing
            self.positions[i] = glm.vec3(x, y, 0)

                
    def Collisions(self, i):
        halfBoundSize = glm.vec3(self.boundSize / 2 - glm.vec3(1) * self.particleSize)
        
        if abs(self.positions[i].x) > halfBoundSize.x:
            self.positions[i].x = halfBoundSize.x * glm.sign(self.positions[i].x)
            self.velocities[i].x *= -1 * self.frictionCoefficient
        if abs(self.positions[i].y) > halfBoundSize.y:
            self.positions[i].y = halfBoundSize.y * glm.sign(self.positions[i].y)
            self.velocities[i].y *= -1 * self.frictionCoefficient
    
    def OnUpdate(self, dt: float):
        for i in range(len(self.positions)):
            #
            self.velocities[i] += self.gravity * dt
            self.densities[i] = self.CalculateDensity(self.positions[i])
            
            #
            pressureForce = self.CalculatePressureForce(self.positions[i])
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
    
    def CalculateDensity(self, point: glm.vec3):
        density = 0
        
        for position in self.positions:
            dist = glm.length(position - point)
            influence = self.SmoothingKernel(self.smoothingRadius, dist)
            density += self.mass * influence
        return density
    
    def CalculateProperty(self, point: glm.vec3):
        property = 0
        
        for i in range(self.particleNumber):
            dist = glm.length(self.positions[i] - point)
            influence = self.SmoothingKernel(self.smoothingRadius, dist)
            density = self.densities[i]
            property += self.properties[i] * influence * self.mass / density
        return property
            
    def CalculatePressureForce(self, point: glm.vec3):
        pressureForce = glm.vec3(0)
        
        for i in range(self.particleNumber):
            dist = glm.length(self.positions[i] - point)
            if dist == 0:
                continue
            direction = (self.positions[i] - point) / dist
            slope = self.SmoothingKernelDerivative(self.smoothingRadius, dist)
            density = self.densities[i]
            if density == 0.0 or dist == 0.0:
                continue
            pressureForce += self.ConvertDensityToPressure(density) * direction * slope * self.mass / density
            
        return pressureForce
    
    def UpdateDensities(self):
        for i in range(self.particleNumber):
            self.densities[i] = self.CalculateDensity(self.positions[i])
    
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
    
    def SetBoundSize(self, bounds: glm.vec3):
        self.boundSize = bounds
        
    def SetFrictionCoefficient(self, m: float):
        self.frictionCoefficient = m
