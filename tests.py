import unittest
import math
import glm
import copy
from App.Simulation.Simulation import Simulation, Cell


class TestCell(unittest.TestCase):
    def setUp(self):
        self.cell = Cell()

    def test_add_and_get_particles(self):
        self.assertTrue(self.cell.IsEmpty())
        self.cell.AddParticle(5)
        self.assertFalse(self.cell.IsEmpty())
        self.assertIn(5, self.cell.GetParticles())

    def test_remove_particle(self):
        self.cell.AddParticle(1)
        self.cell.AddParticle(2)
        self.cell.RemoveParticle(1)
        self.assertNotIn(1, self.cell.GetParticles())
        self.assertIn(2, self.cell.GetParticles())

    def test_clear(self):
        self.cell.AddParticle(42)
        self.cell.Clear()
        self.assertTrue(self.cell.IsEmpty())

class TestSimulation(unittest.TestCase):
    def setUp(self):
        # small 10×10×10 box, max 2 particles, radius 1, friction 0.5
        self.sim = Simulation(
            particleNumber=2,
            particleSize=2.0,
            boundSize=(10.0, 10.0, 10.0),
            frictionCoefficient=0.5
        )

    def test_calculate_optimal_cell_size(self):
        # default scale=1.5: 2*r*scale = 2*1*1.5 = 3.0
        self.assertAlmostEqual(self.sim.CalculateOptimalCellSize(), 3.0)

        # custom scale
        self.assertAlmostEqual(self.sim.CalculateOptimalCellSize(2.0), 4.0)

    def test_add_particle(self):
        # no particles initially
        self.assertEqual(self.sim.GetParticleCount(), 0)
        self.sim.AddParticle(glm.vec3(1,2,3))
        self.assertEqual(self.sim.GetParticleCount(), 1)
        # position matches emitter
        self.assertEqual(self.sim.GetPoints()[0], glm.vec3(1,2,3))
        # velocity matches initial
        self.assertEqual(self.sim._velocities[0], self.sim._initial_particle_velocity)

    def test_check_wall_collisions(self):
        # manually inject a position beyond +x bound
        # bound half-size is 5, radius=1 => max x=4
        self.sim._positions.append(glm.vec3(10.0, 0.0, 0.0))
        self.sim._velocities.append(glm.vec3(1.0, 0.0, 0.0))
        self.sim.CheckWallCollisions(0)
        # x should be clamped to 4, and velocity flipped & scaled by friction
        self.assertAlmostEqual(self.sim._positions[0].x, 4.0)
        self.assertAlmostEqual(self.sim._velocities[0].x, -1.0 * 0.5)

    def test_create_grid_and_neighbor_collision(self):
        # override cell size to 2*r = 2 so particles within 2 units collide
        self.sim._cell_size = self.sim._particle_radius * 2.0
        # place two overlapping particles in the same cell
        p1 = glm.vec3(0.0, 0.0, 0.0)
        p2 = glm.vec3(1.0, 0.0, 0.0)  # distance=1 < diameter=2
        self.sim._positions = [p1, p2]
        self.sim._velocities = [glm.vec3(0)] * 2
        # grid-template setup
        self.sim._cell_count = glm.vec3(
            int(math.ceil(10.0 / self.sim._cell_size)),
            int(math.ceil(10.0 / self.sim._cell_size)),
            int(math.ceil(10.0 / self.sim._cell_size))
        )
        self.sim._grid_template = [
            [
                [Cell() for _ in range(int(self.sim._cell_count.z))]
                for _ in range(int(self.sim._cell_count.y))
            ]
            for _ in range(int(self.sim._cell_count.x))
        ]
        self.sim._grid = copy.deepcopy(self.sim._grid_template)

        # run CreateGrid to resolve their overlap
        self.sim.CreateGrid()
        # after collision resolution they should be separated by at least diameter
        dist = glm.distance(self.sim._positions[0], self.sim._positions[1])
        self.assertGreaterEqual(dist, 2.0 - 1e-6)

if __name__ == "__main__":
    unittest.main()