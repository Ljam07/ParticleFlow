import glm

import math
import random

import copy

class Cell:
    def __init__(self):
        # contains a list of particle IDs
        self.particles: list[int] = []
    
    def AddParticle(self, particleId):
        self.particles.append(particleId)
    
    def RemoveParticle(self, particleId):
        self.particles.remove(particleId)
    
    def Clear(self):
        self.particles.clear()
        
    def IsEmpty(self):
        if len(self.particles) == 0:
            return True
        return False
    
    def GetParticles(self):
        return self.particles

class Simulation:
    def __init__(self, particleNumber, particleSize, boundSize, frictionCoefficient):
        # Ensure boundSize is always a glm.vec3
        if not isinstance(boundSize, glm.vec3):
            boundSize = glm.vec3(*boundSize)
        self._bound_size = boundSize
        self._particle_number = int(particleNumber)
        self._particle_radius = particleSize / 2

        self._friction_coefficient = frictionCoefficient
        self._velocity_damping = 40.0
        self._gravity = glm.vec3(0, -2.8, 0)
        
        self._positions: list[glm.vec3] = []
        self._velocities: list[glm.vec3] = []
        self._colors:     list[glm.vec3] = []


        self._initial_particle_velocity = glm.vec3(0.2, 2, 0)
        self._emitter_position = glm.vec3(0, 0, 0)
        self._emission_rate = 10
        self._emission_interval = 1 / self._emission_rate  # particles per second
        
        self.ttl_particles = 0.0

        self._cell_size = self._particle_radius * 12 # self.CalculateOptimalCellSize() # self._particle_radius * 6
        self._cell_count = glm.vec3(
            int(math.ceil(self._bound_size.x // self._cell_size)),
            int(math.ceil(self._bound_size.y // self._cell_size)),
            int(math.ceil(self._bound_size.z // self._cell_size))
        )
        
        self._grid_template = [
            [
                [Cell() for _ in range(int(self._cell_count.z))]
                for _ in range(int(self._cell_count.y))
            ]
            for _ in range(int(self._cell_count.x))
        ]

        # initialise grid and particle‐cell list correctly
        self._grid = copy.deepcopy(self._grid_template)
        self._has_particles: list[glm.vec3] = []
        
        self._neighbour_offsets = [
            glm.vec3(dx, dy, dz)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            for dz in (-1, 0, 1)
            if not (dx == 0 and dy == 0 and dz == 0)
        ]

    def CalculateOptimalCellSize(self, scale: float = 1.5) -> float:
        """
        Calculate an optimal cell size for spatial hashing based on particle radius.
        The scale factor adjusts how much larger the cell is than the particle collision range.
        """
        return 2.0 * self._particle_radius * scale

        
    def OnUpdate(self, dt: float):
        """
        Update the simulation state for a single timestep.
        This method should be called at a fixed interval.
        """
        # if len(self._positions) > 0:
        #    print(self._positions[0])
        
        if len(self._positions) < self._particle_number and self.ttl_particles > self._emission_interval:
            self.AddParticle(self._emitter_position)
            self.ttl_particles = 0
        else:
            self.ttl_particles += dt
                
        # Update particle positions, velocities, etc. here
        substep = 2
        substep_size = dt / substep
        for _ in range(substep):
            self.OnUpdateSubstep(substep_size)
            
    def AddParticle(self, position: glm.vec3, velocity: glm.vec3 = None):
        """
        Add a new particle to the simulation at the specified position.
        If no velocity is provided, it defaults to the initial particle velocity.
        """

        v = glm.vec3(self._initial_particle_velocity.x, self._initial_particle_velocity.y, self._initial_particle_velocity.z)
            
        spawn_pos = glm.vec3(position.x, position.y, position.z)
        
        self._positions.append(spawn_pos)
        self._velocities.append(v)
        col = glm.vec3(
            random.uniform(0.0, 1.0),
            random.uniform(0.0, 1.0),
            random.uniform(0.0, 1.0)
            )
        self._colors.append(col)
    
    def OnUpdateSubstep(self, dt: float):
        for i in range(len(self._positions)):
            self._velocities[i] += self._gravity * dt
        
        # Update positions
        for i in range(len(self._positions)):
            self._positions[i] += self._velocities[i] * dt
        
        # Handle collisions
        for i in range(len(self._positions)):
            self.CheckWallCollisions(i)
        
        # self.FindCollisions()
        self.CreateGrid()
        


    def FindCollisions(self):
        """
        Find and resolve collisions between particles.
        This method should be called after updating particle positions.
        """
        
        for i in range(len(self._positions)):
            for j in range(i+1, len(self._positions)):
                if self.IsColliding(i, j):
                    self.ResolveCollision(i, j)
            self.CheckWallCollisions(i)
                
    def CheckWallCollisions(self, i: int):
        """
        Check if a particle is colliding with the walls of the simulation bounds.
        If it is, adjust its position to keep it within bounds.
        """
       
        half    = self._bound_size * 0.5
        limit_x = half.x - self._particle_radius
        limit_y = half.y - self._particle_radius
        limit_z = half.z - self._particle_radius

        # X axis
        if   self._positions[i].x >  limit_x:
            self._positions[i].x  =  limit_x
            self._velocities[i].x *= -self._friction_coefficient
        elif self._positions[i].x < -limit_x:
            self._positions[i].x  = -limit_x
            self._velocities[i].x *= -self._friction_coefficient

        # Y axis
        if   self._positions[i].y >  limit_y:
            self._positions[i].y  =  limit_y
            self._velocities[i].y *= -self._friction_coefficient
        elif self._positions[i].y < -limit_y:
            self._positions[i].y  = -limit_y
            self._velocities[i].y *= -0.8

        # Z axis
        if   self._positions[i].z >  limit_z:
            self._positions[i].z  =  limit_z
            self._velocities[i].z *= -self._friction_coefficient
        elif self._positions[i].z < -limit_z:
            self._positions[i].z  = -limit_z
            self._velocities[i].z *= -self._friction_coefficient


    def IsColliding(self, p1: int, p2: int) -> bool:
        """
        Check if two particles are colliding based on their positions.
        """
        distance = glm.distance(self._positions[p1], self._positions[p2])
        #print(f"Distance between particles {p1} and {p2}: {distance}")
        return distance < 2 * self._particle_radius
    
    def ResolveCollision(self, p1: int, p2: int):
        """
        Resolve a collision between two particles by adjusting their positions.
        This is a simple elastic collision resolution.
        """
        point1 = self._positions[p1]
        point2 = self._positions[p2]
        mass = 1.0

        impact_vector = point2 - point1
        d = glm.length(impact_vector)

        if d < 1e-5:
            return

        if d < self._particle_radius * 2:
            overlap = d - (self._particle_radius * 2)
            dir = glm.normalize(impact_vector) * (overlap * 0.5)
            self._positions[p1] += dir
            self._positions[p2] -= dir
            d = self._particle_radius * 2
            impact_vector = glm.normalize(impact_vector) * d  # Correct impact vector

        mSum = mass + mass
        vDiff = self._velocities[p2] - self._velocities[p1]

        num = glm.dot(vDiff, impact_vector)
        den = mSum * d * d

        dVa = impact_vector * (2 * mass * num / den)
        self._velocities[p1] += dVa

        dVb = impact_vector * (-2 * mass * num / den)
        self._velocities[p2] += dVb

    def CreateGrid(self):
        self._grid = copy.deepcopy(self._grid_template)

        for idx, pos in enumerate(self._positions):
            cx, cy, cz = self.GetCellIndex(pos)
            if not (0 <= cx < self._cell_count.x and
                    0 <= cy < self._cell_count.y and
                    0 <= cz < self._cell_count.z):
                continue
            self._grid[cx][cy][cz].AddParticle(idx)

        # no _has_particles, so loop over all cells instead
        for x in range(int(self._cell_count.x)):
            for y in range(int(self._cell_count.y)):
                for z in range(int(self._cell_count.z)):
                    if not self._grid[x][y][z].IsEmpty():
                        self.CheckNeighboringCells(x, y, z)

        
    def CheckNeighboringCells(self, cx: int, cy: int, cz: int):
        particles = self._grid[cx][cy][cz].GetParticles()
        cellListSize = len(particles)

        for i in range(cellListSize):
            p1 = particles[i]
            for j in range(i + 1, cellListSize):
                p2 = particles[j]
                if self.IsColliding(p1, p2):
                    self.ResolveCollision(p1, p2)
            self.CheckWallCollisions(p1)

        for offset in self._neighbour_offsets:
            nx, ny, nz = cx + int(offset.x), cy + int(offset.y), cz + int(offset.z)
            if not (0 <= nx < self._cell_count.x and
                    0 <= ny < self._cell_count.y and
                    0 <= nz < self._cell_count.z):
                continue

            for p1 in particles:
                for p2 in self._grid[nx][ny][nz].GetParticles():
                    if self.IsColliding(p1, p2):
                        self.ResolveCollision(p1, p2)
 
                           
    def GetCellIndex(self, position: glm.vec3) -> glm.vec3:
        """
        Get the grid cell index for a given position.
        """
        cell_x = int((position.x + self._bound_size.x * 0.5) / self._cell_size)
        cell_y = int((position.y + self._bound_size.y * 0.5) / self._cell_size)
        cell_z = int((position.z + self._bound_size.z * 0.5) / self._cell_size)
        
        return cell_x, cell_y, cell_z
        
                    
                    
    ## ACCESSED OUT OF CLASS    
    def GetPoints(self) -> list[glm.vec3]:
        return self._positions

    def GetColors(self) -> list[glm.vec3]:
        return self._colors

    def SetParticleSize(self, size: float):
        self._particle_radius = size

    def SetBoundSize(self, boundSize):
        if not isinstance(boundSize, glm.vec3):
            boundSize = glm.vec3(*boundSize)
        self._bound_size = boundSize

    def SetFrictionCoefficient(self, m: float):
        self._friction_coefficient = m

    def GetParticleCount(self) -> int:
        return len(self._positions)