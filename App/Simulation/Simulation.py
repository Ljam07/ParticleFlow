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
        self._particles = self._CreateParticles()

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

    # TODO properly implement create particles
    def _CreateParticles(self, cube_size = 1.0, cube_pos: glm.vec3 = glm.vec3(0, 1 ,0)):
        # m^3 = 3rt(m)
        m = int(glm.ceil(self._particle_amount ** (1/3)))
        
        # cube / subdivisions
        d = cube_size / m

        # Holds all points in xyz vec3 form
        points = []

        for i in range(m):
            for j in range(m):
                for k in range(m):
                    pos: glm.vec3 = glm.vec3(0, 0, 0)
                    pos.x = (i + 0.5) * d
                    pos.y = (j + 0.5) * d
                    pos.z = (k + 0.5) * d
                    pos += cube_pos
                    points.append(pos)
                    print(pos)

        # Trunicate the list if the particles exceed needed amount
        return points[:self._particle_amount]

    def OnUpdate(self, dt: float):
        pass