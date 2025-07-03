import unittest
import math
import glm
from App.Simulation import Simulation

Simulation = Simulation.Simulation

class TestSimulation(unittest.TestCase):
    def setUp(self):
        # Use a small bound size to simplify tests
        self.bound_size = glm.vec3(10.0, 10.0, 10.0)
        self.gravity = glm.vec3(0.0, -9.81, 0.0)
        self.sim = Simulation(
            particleNumber=8,
            particleSize=2.0,
            boundSize=self.bound_size,
            frictionCoefficient=0.5,
            particleSpacing=None,
            gravity=self.gravity
        )
        self.sim.BuildSpatialMap()


    def testConvertDensityToPressure(self):
        # target_density is 2.75, multiplier is 2
        self.assertEqual(self.sim.ConvertDensityToPressure(4.75), (4.75 - 2.75) * 2)

    def testSmoothingKernel(self):
        r = 3.0
        # outside radius
        self.assertEqual(self.sim.SmoothingKernel(r, 3.0), 0.0)
        # inside radius
        d = 1.0
        volume = math.pi * (r**4) / 6
        expected = (r - d)**2 / volume
        self.assertAlmostEqual(self.sim.SmoothingKernel(r, d), expected)

    def testSmoothingKernelDerivative(self):
        r = 2.0
        # outside radius
        self.assertEqual(self.sim.SmoothingKernelDerivative(r, 2.0), 0)
        # inside radius
        d = 0.5
        scale = 12 / (r**4 * math.pi)
        expected = (d - r) * scale
        self.assertAlmostEqual(self.sim.SmoothingKernelDerivative(r, d), expected)

    def testCalculateAveragePressure(self):
        # average of pressures for dA=3.75 and dB=1.75
        pA = (3.75 - self.sim._target_density) * self.sim._pressure_multiplier
        pB = (1.75 - self.sim._target_density) * self.sim._pressure_multiplier
        self.assertAlmostEqual(self.sim.CalculateAveragePressure(3.75, 1.75), (pA + pB) / 2)

    def testGetCellIndex(self):
        # origin in a 2×2×2 box with cellSize > 0
        cx, cy, cz = self.sim.GetCellIndex(glm.vec3(0.0, 0.0, 0.0))
        # must be within grid bounds
        dims = (len(self.sim.grid), len(self.sim.grid[0]), len(self.sim.grid[0][0]))
        self.assertTrue(0 <= cx < dims[0])
        self.assertTrue(0 <= cy < dims[1])
        self.assertTrue(0 <= cz < dims[2])

    def testGetPointsAndGetColors(self):
        pts = self.sim.GetPoints()
        cols = self.sim.GetColors()
        self.assertEqual(len(pts), 8)
        self.assertTrue(all(isinstance(p, glm.vec3) for p in pts))
        self.assertEqual(len(cols), 8)
        # Each colour should be glm.vec3(1.0)
        self.assertTrue(all(c == glm.vec3(1.0) for c in cols))


if __name__ == '__main__':
    unittest.main()
