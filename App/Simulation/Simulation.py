import glm
import math

class Particle:
    def __init__(self, position, particleSize, boundSize, frictionCoeficient):
        self.gravity = glm.vec3(0, -9.8, 0)
        self.position = position
        self.velocity = glm.vec3(0)
        self.ParticleSize = particleSize
        self.boundSize = boundSize
        self.color = glm.vec3(1)
        self.frictionCoefficient = frictionCoeficient
        
    def OnUpdate(self, deltaTime: float):
        self.velocity += self.gravity * deltaTime
        self.position += self.velocity * deltaTime
        self.CheckCollisions()
    
    def CheckCollisions(self):
        halfBoundSize = self.boundSize/2 - glm.vec3(1) * (self.ParticleSize)
        
        if abs(self.position.x) > halfBoundSize.x:
            self.position.x = halfBoundSize.x * glm.sign(self.position.x)
            self.velocity.x *= -1 * self.frictionCoefficient
        if abs(self.position.y) > halfBoundSize.y:
            self.position.y = halfBoundSize.y * glm.sign(self.position.y)
            self.velocity.y *= -1 * self.frictionCoefficient
        
        
class Simulation:
    def __init__(self, particleNum: int = 5, particleSize = 1, boundSize = glm.vec3(3), fCoefficient = 0.9, particleSpacing = None):
        self.particleNumber = int(particleNum)
        self.particleSize = particleSize
        self.boundSize = boundSize
        self.frictionCoefficient = fCoefficient
        if particleSpacing == None:
            self.particleSpacing = self.particleSize/2
        else:
            self.particleSpacing = particleSpacing
        self.particles = self.CreateParticles()

    def CreateParticles(self):
        particles = []
        if self.particleNumber <= 0:
            return particles
        particlesPerRow = max(int(self.particleNumber ** (1/2)), 1)
        particlesPerColumn = (self.particleNumber - 1) / particlesPerRow + 1
        spacing = self.particleSize * 2 + self.particleSpacing
        
        for i in range(self.particleNumber):
            pos = glm.vec3((i % particlesPerRow - particlesPerRow / 2 + 0.5) * spacing, \
                (i / particlesPerRow - particlesPerColumn / 2 + 0.5) * spacing, 0)
            particles.append(Particle(pos, self.particleSize, self.boundSize, self.frictionCoefficient))

        return particles
    
    def SmoothKernel(self, radius, dist) -> float:
        value = max(0, radius * radius - dist * dist)
        return value
    
    def CalculateDensity(self, point: glm.vec3):
        density = 0
        mass = 1
        
        for particle in self.particles:
            dist = glm.length(particle.position - point)
            influence = self.SmoothKernel(0.5, dist)
            density += mass * influence
        
        return density

    def OnUpdate(self, dt: float):
        for particle in self.particles:
            particle.OnUpdate(dt)

    def GetPoints(self) -> list[glm.vec3]:
        positions = [p.position for p in self.particles]
        return positions

    def GetColors(self) -> list[glm.vec3]:
        colors = [p.color for p in self.particles]
        return colors
    
    def SetParticleSize(self, size: float):
        for particle in self.particles:
            particle.particleSize = size
        self.particleSize = size
    
    def SetGravity(self, gravity: glm.vec3):
        for particle in self.particles:
            particle.gravity = gravity
    
    def SetBoundSize(self, bounds: glm.vec3):
        self.boundSize = bounds
        for particle in self.particles:
            particle.boundSize = bounds
        
    def SetFrictionCoefficient(self, m: float):
        self.frictionCoefficient = m
        for particle in self.particles:
            particle.frictionCoefficient = m
