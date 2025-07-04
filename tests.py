import unittest
import math
import glm
import copy
import glfw

from App.Simulation.Simulation import Simulation, Cell
from Engine.Renderer.Camera import Camera
from Engine.Core.DeltaTime import DeltaTime
from Engine.Renderer.Mesh import Mesh

class TestCamera(unittest.TestCase):
    def setUp(self):
        # Initialize camera with known defaults
        self.cam = Camera(
            pivot=glm.vec3(0, 0, 0),
            distance=5.0,
            yaw=-90.0,
            pitch=0.0,
            fov=45.0,
            aspect=4/3,
            near=0.1,
            far=100.0
        )
        # Backup original GLFW functions
        self._orig_get_window_size  = glfw.get_window_size
        self._orig_get_mouse_button = glfw.get_mouse_button
        self._orig_get_key          = glfw.get_key
        self._orig_get_cursor_pos   = glfw.get_cursor_pos
        self._orig_set_input_mode   = glfw.set_input_mode
        self._orig_set_cursor_pos   = glfw.set_cursor_pos

    def tearDown(self):
        # Restore GLFW functions
        glfw.get_window_size    = self._orig_get_window_size
        glfw.get_mouse_button   = self._orig_get_mouse_button
        glfw.get_key            = self._orig_get_key
        glfw.get_cursor_pos     = self._orig_get_cursor_pos
        glfw.set_input_mode     = self._orig_set_input_mode
        glfw.set_cursor_pos     = self._orig_set_cursor_pos

    def test_get_camera_direction_default(self):
        """Direction with yaw=-90°, pitch=0° should be (0,0,-1)."""
        direction = self.cam.GetCameraDirection()
        self.assertAlmostEqual(direction.x, 0.0, places=5)
        self.assertAlmostEqual(direction.y, 0.0, places=5)
        self.assertAlmostEqual(direction.z, -1.0, places=5)

    def test_get_view_matrix_eye_position(self):
        """With yaw=-90°, pitch=0°, eye should be at (0,0,-5)."""
        view = self.cam.GetViewMatrix()
        inv = glm.inverse(view)
        eye = glm.vec3(inv[3].x, inv[3].y, inv[3].z)
        self.assertAlmostEqual(eye.x, 0.0, places=5)
        self.assertAlmostEqual(eye.y, 0.0, places=5)
        self.assertAlmostEqual(eye.z, -5.0, places=5)

    def test_on_update_zero_height(self):
        """If window height is zero, aspect must remain unchanged."""
        def stub_window_size(window):
            return (100, 0)
        glfw.get_window_size = stub_window_size

        original_aspect = self.cam.aspect
        self.cam.OnUpdate(None)
        self.assertEqual(self.cam.aspect, original_aspect)

    def test_on_update_toggle_dragging(self):
        """Press then release left button toggles dragging state."""
        # stub window size non-zero
        def stub_window_size(window):
            return (80, 40)
        glfw.get_window_size = stub_window_size

        # stub no modifier keys pressed
        def stub_get_key(window, key):
            return glfw.RELEASE
        glfw.get_key = stub_get_key

        # stub mouse button: first call returns PRESS, then RELEASE
        call_count = {'n': 0}
        def stub_mouse_button(window, button):
            call_count['n'] += 1
            if call_count['n'] == 1:
                return glfw.PRESS
            return glfw.RELEASE
        glfw.get_mouse_button = stub_mouse_button

        # stub cursor position always center
        def stub_cursor_pos(window):
            return (40.0, 20.0)
        glfw.get_cursor_pos = stub_cursor_pos

        # stub cursor and input-mode setters to no-op
        def stub_set_input_mode(window, mode, value):
            pass
        glfw.set_input_mode = stub_set_input_mode

        def stub_set_cursor_pos(window, x, y):
            pass
        glfw.set_cursor_pos = stub_set_cursor_pos

        # First update -> start dragging
        self.cam.OnUpdate(None)
        self.assertTrue(self.cam._dragging)
        self.assertEqual(self.cam._last_x, 40)
        self.assertEqual(self.cam._last_y, 20)

        # Second update -> end dragging
        self.cam.OnUpdate(None)
        self.assertFalse(self.cam._dragging)
        self.assertIsNone(self.cam._last_x)
        self.assertIsNone(self.cam._last_y)

class TestGenerateUVSphere(unittest.TestCase):

    def test_output_length(self):
        stacks = 5
        slices = 8
        verts = Mesh.GenerateUVSphere(stacks, slices)
        # each stack×slice produces 2 triangles,
        # each triangle = 3 verts, each vert = 3 floats
        expected_length = stacks * slices * 2 * 3 * 3
        self.assertEqual(len(verts), expected_length)

    def test_unit_sphere_simple_case(self):
        # stacks=1,slices=1 should give 2 triangles = 6 verts = 18 floats
        verts = Mesh.GenerateUVSphere(1, 1)
        self.assertEqual(len(verts), 18)

        # For stacks=1: phi0 = -pi/2, phi1 = +pi/2 → y0 = -1, y1 = +1; r0 = r1 = 0
        # So all x,z == 0
        # Triangle1: (0,-1,0),(0,1,0),(0,1,0)
        # Triangle2: (0,-1,0),(0,1,0),(0,-1,0)
        expected = [
            0.0, -1.0,  0.0,
            0.0,  1.0,  0.0,
            0.0,  1.0,  0.0,
            0.0, -1.0,  0.0,
            0.0,  1.0,  0.0,
            0.0, -1.0,  0.0,
        ]
        for v, e in zip(verts, expected):
            self.assertAlmostEqual(v, e)

    def test_custom_radius(self):
        # same simple case but radius=2.0
        verts = Mesh.GenerateUVSphere(1, 1, radius=2.0)
        # y0 = -2, y1 = +2, x/z remain 0
        expected = [
            0.0, -2.0,  0.0,
            0.0,  2.0,  0.0,
            0.0,  2.0,  0.0,
            0.0, -2.0,  0.0,
            0.0,  2.0,  0.0,
            0.0, -2.0,  0.0,
        ]
        for v, e in zip(verts, expected):
            self.assertAlmostEqual(v, e)


class TestDeltaTime(unittest.TestCase):
    def test_get_seconds_zero(self):
        dt = DeltaTime(0)
        self.assertEqual(dt.GetSeconds(), 0)

    def test_get_seconds_positive(self):
        dt = DeltaTime(1.234)
        self.assertAlmostEqual(dt.GetSeconds(), 1.234)

    def test_get_seconds_negative(self):
        dt = DeltaTime(-2.5)
        self.assertAlmostEqual(dt.GetSeconds(), -2.5)

    def test_get_milliseconds_zero(self):
        dt = DeltaTime(0)
        self.assertEqual(dt.GetMilliseconds(), 0)

    def test_get_milliseconds_integer(self):
        dt = DeltaTime(2)
        self.assertEqual(dt.GetMilliseconds(), 2000)

    def test_get_milliseconds_fraction(self):
        dt = DeltaTime(0.75)
        self.assertAlmostEqual(dt.GetMilliseconds(), 750)

    def test_get_milliseconds_negative(self):
        dt = DeltaTime(-1.2)
        self.assertAlmostEqual(dt.GetMilliseconds(), -1200)

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