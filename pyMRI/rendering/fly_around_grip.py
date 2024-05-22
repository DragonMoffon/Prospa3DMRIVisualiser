from arcade import get_window, key
from arcade.camera import CameraData, grips
from arcade.math import quaternion_rotation

from pyglet.math import Vec2, Vec3

LOOK_SENSITIVITY: float = 60.0
ROLL_SPEED: float = 60.0
MOVE_SPEED: float = 60.0


class FlyAroundGrip:

    def __init__(self, data: CameraData):
        self._win = get_window()
        self._win.push_handlers()
        self._camera_data = data
        data.forward = (0.0, 0.0, 1.0)

        self._forward_velocity: float = 0.0

        self._strafe_vertical: int = 0
        self._strafe_horizontal: int = 0
        self._accelerate_forward: int = 0
        self._roll_velocity: int = 0
        self._pitch_velocity: float = 0.0
        self._yaw_velocity: float = 0.0

        self._pitch: float = 0.0
        self._yaw: float = 0.0

        self._global_up = (0.0, 1.0, 0.0)

        self._active: bool = False

    def toggle(self):
        if self._active:
            self.deactivate()
        else:
            self.activate()

    def activate(self):
        if self._active:
            return

        self._accelerate_forward = 0
        self._pitch_velocity = 0
        self._yaw_velocity = 0
        self._roll_velocity = 0

        self._win.set_exclusive_mouse(True)
        self._win.push_handlers(
            self.on_mouse_motion,
            self.on_mouse_drag,
            self.on_mouse_scroll,
            self.on_key_press,
            self.on_key_release,
            self.on_update
        )
        self._active = True

    def deactivate(self):
        if not self._active:
            return

        self._accelerate_forward = 0
        self._pitch_velocity = 0
        self._yaw_velocity = 0
        self._roll_velocity = 0

        self._win.set_exclusive_mouse(False)
        self._win.remove_handlers(
            self.on_mouse_motion,
            self.on_mouse_drag,
            self.on_mouse_scroll,
            self.on_key_press,
            self.on_key_release,
            self.on_update
        )
        self._active = False

    def on_mouse_motion(self, x, y, dx, dy):
        self._yaw_velocity = dx
        self._pitch_velocity = -dy

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(dx, dy, x, y)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if scroll_y > 0:
            self._camera_data.zoom = max(min(self._camera_data.zoom * 1.25, 2.0), 0.5)
        elif scroll_y < 0:
            self._camera_data.zoom = max(min(self._camera_data.zoom / 1.25, 2.0), 0.5)

    def on_key_press(self, symbol, modifiers):
        match symbol:
            case key.SPACE:
                self._strafe_vertical += 1
            case key.LSHIFT:
                self._strafe_vertical -= 1
            case key.W:
                self._accelerate_forward += 1
            case key.S:
                self._accelerate_forward -= 1
            case key.A:
                self._strafe_horizontal -= 1
            case key.D:
                self._strafe_horizontal += 1
            case key.Q:
                self._roll_velocity += 1
            case key.E:
                self._roll_velocity -= 1

    def on_key_release(self, symbol, modifiers):
        match symbol:
            case key.SPACE:
                self._strafe_vertical -= 1
            case key.LSHIFT:
                self._strafe_vertical += 1
            case key.W:
                self._accelerate_forward -= 1
            case key.S:
                self._accelerate_forward += 1
            case key.A:
                self._strafe_horizontal += 1
            case key.D:
                self._strafe_horizontal -= 1
            case key.Q:
                self._roll_velocity -= 1
            case key.E:
                self._roll_velocity += 1

    def on_update(self, delta_time: float):
        camera = self._camera_data

        if self._pitch_velocity or self._yaw_velocity:
            self._pitch = min(max(self._pitch + LOOK_SENSITIVITY * delta_time * self._pitch_velocity, -89.0), 89.0)
            self._yaw = (self._yaw + LOOK_SENSITIVITY * delta_time * self._yaw_velocity) % 360

            camera.up = self._global_up
            camera.forward = quaternion_rotation(self._global_up, (0.0, 0.0, -1.0), self._yaw)
            camera.up, camera.forward = grips.rotate_around_right(camera, self._pitch)

            self._pitch_velocity = 0.0
            self._yaw_velocity = 0.0

        if self._accelerate_forward:
            o_pos = camera.position
            fw = camera.forward
            fw_speed = MOVE_SPEED * self._accelerate_forward * delta_time
            camera.position = o_pos[0] + fw_speed * fw[0], o_pos[1] + fw_speed * fw[1], o_pos[2] + fw_speed * fw[2]

        if self._strafe_vertical or self._strafe_horizontal:
            strafe = Vec2(self._strafe_horizontal, self._strafe_vertical).normalize() * MOVE_SPEED * delta_time
            camera.position = grips.strafe(camera, strafe)



