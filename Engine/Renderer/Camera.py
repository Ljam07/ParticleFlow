import glm
import glfw

class Camera:
    def __init__(self,
                 pivot=glm.vec3(0,0,0),
                 distance=5.0,
                 yaw=-90.0,
                 pitch=0.0,
                 fov=45.0,
                 aspect=4/3,
                 near=0.1,
                 far=100.0):

        self.pivot    = glm.vec3(pivot)
        self.distance = distance
        self.yaw      = yaw
        self.pitch    = pitch
        self.fov      = fov
        self.aspect   = aspect
        self.near     = near
        self.far      = far

        self._last_x = None
        self._last_y = None
        self._dragging = False
        self._window_center = None

        self._pan_speed = 0.005
        self._rot_speed = 0.1
        self._zoom_speed = 0.5
        self._min_dist = 0.5
        self._max_dist = 100.0
        self._scroll_offset = 0.0

    def GetViewMatrix(self) -> glm.mat4:
        rad_yaw   = glm.radians(self.yaw)
        rad_pitch = glm.radians(self.pitch)
        x = self.distance * glm.cos(rad_pitch) * glm.cos(rad_yaw)
        y = self.distance * glm.sin(rad_pitch)
        z = self.distance * glm.cos(rad_pitch) * glm.sin(rad_yaw)
        eye = glm.vec3(x, y, z) + self.pivot
        return glm.lookAt(eye, self.pivot, glm.vec3(0,1,0))

    def GetProjectionMatrix(self) -> glm.mat4:
        return glm.perspective(glm.radians(self.fov), self.aspect, self.near, self.far)

    def GetCameraDirection(self):
        rad_yaw   = glm.radians(self.yaw)
        rad_pitch = glm.radians(self.pitch)
        x = glm.cos(rad_pitch) * glm.cos(rad_yaw)
        y = glm.sin(rad_pitch)
        z = glm.cos(rad_pitch) * glm.sin(rad_yaw)
        return glm.normalize(glm.vec3(x, y, z))

    def OnUpdate(self, window):
        # Get window centre
        w, h = glfw.get_window_size(window)
        
        if h == 0:
            return  # avoid divide-by-zero
        self.aspect = w / h
        
        cx, cy = w//2, h//2

        # Poll input
        left  = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT)  == glfw.PRESS
        right = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS
        alt   = (glfw.get_key(window, glfw.KEY_LEFT_ALT) == glfw.PRESS
             or glfw.get_key(window, glfw.KEY_RIGHT_ALT) == glfw.PRESS)
        x, y  = glfw.get_cursor_pos(window)

        dragging = left or right

        # Drag start: hide cursor & warp to centre
        if dragging and not self._dragging:
            self._dragging = True
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_HIDDEN)
            glfw.set_cursor_pos(window, cx, cy)
            self._last_x, self._last_y = cx, cy
            return  # skip until next frame

        # Drag end: unhide cursor
        if not dragging and self._dragging:
            self._dragging = False
            glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            self._last_x = self._last_y = None

        # Handle dragging
        if dragging:
            dx = x - self._last_x
            dy = y - self._last_y


            if left and alt:
                # Alt + left‐drag → zoom
                # drag *up* (negative dy) = zoom in, drag down = zoom out
                self.distance += dy * self._zoom_speed
                self.distance = max(self._min_dist, min(self._max_dist, self.distance))
            elif left:
                # rotate
                self.yaw   += dx * self._rot_speed
                self.pitch += dy * self._rot_speed
                self.pitch = max(-89, min(89, self.pitch))
            else:
                # pan (invert Y)
                right_dir = glm.normalize(glm.cross(self.GetCameraDirection(), glm.vec3(0,1,0)))
                up_dir    = glm.vec3(0,1,0)
                self.pivot += (dx * self._pan_speed) * right_dir
                self.pivot += ( dy * self._pan_speed) * up_dir

            # warp back to centre to avoid cursor hitting screen edges
            glfw.set_cursor_pos(window, cx, cy)
            self._last_x, self._last_y = cx, cy