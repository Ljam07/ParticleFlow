import glm
import random

class Particle:
    def __init__(self, position: glm.vec3, radius: float = 0.5, velocity: glm.vec3 = glm.vec3(0)):
        self.Position = position
        self.Radius = radius
        self.Velocity = velocity
    
    def Move(self, deltaTime):
        self.Position += self.Velocity * deltaTime

class Cell:
    def __init__(self, id: int):
        self.ID = id
        self.Particles = []

    def AddParticle(self, particle: Particle):
        self.Particles.append(particle)

    def RemoveParticle(self, particle: Particle):
        if particle in self.Particles:
            self.Particles.remove(particle)
    

class Simulation:
    def __init__(self, domainDimensions: glm.vec3, numParticles: int):
        self._domain_size: glm.vec3 = glm.vec3(domainDimensions)
        self._particle_amount = numParticles
        self._cells = self._CreateCells()
        self._CreateParticles()

    def _CreateCells(self):
        cell_id = 0
        cells = []
        for z in range(int(self._domain_size.z)):
            yz_layer = []
            for y in range(int(self._domain_size.y)):
                x_row = []
                for x in range(int(self._domain_size.x)):
                    x_row.append(Cell(cell_id))
                    cell_id += 1
                yz_layer.append(x_row)
            cells.append(yz_layer)
        return cells

    def _GetCellIndices(self, position: glm.vec3):
        x = int(max(0, min(position.x, self._domain_size.x - 1)))
        y = int(max(0, min(position.y, self._domain_size.y - 1)))
        z = int(max(0, min(position.z, self._domain_size.z - 1)))
        return x, y, z

    def _GetCell(self, position: glm.vec3) -> Cell:
        x, y, z = self._GetCellIndices(position)
        return self._cells[z][y][x]

    def _CreateParticles(self):
        count = int(round(self._particle_amount ** (1/3)))  # Particles per axis for uniform grid
        dx = (self._cube_max.x - self._cube_min.x) / count
        dy = (self._cube_max.y - self._cube_min.y) / count
        dz = (self._cube_max.z - self._cube_min.z) / count

        for i in range(count):
            for j in range(count):
                for k in range(count):
                    if len(self._particles) >= self._particle_amount:
                        return
                    pos = glm.vec3(
                        self._cube_min.x + i * dx + dx / 2,
                        self._cube_min.y + j * dy + dy / 2,
                        self._cube_min.z + k * dz + dz / 2
                    )
                    vel = glm.vec3(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
                    p = Particle(position=pos, velocity=vel)
                    self._particles.append(p)
                    self._GetCell(pos).add_particle(p)

    def OnUpdate(self, dt: float):
        pass