from contextlib import contextmanager

from arcade.camera import CameraData, PerspectiveProjector, grips
from arcade.math import quaternion_rotation
import arcade.key as key

from pyglet.math import Vec2, Vec3
from arcade import get_window

from pyMRI.gui.gui import GUI

LOOK_SENSITIVITY: float = 60.0
ROLL_SPEED: float = 60.0
MOVE_SPEED: float = 60.0


class CarouselCamera:

    def look(self, x: int, y: int, dx: int, dy: int):
        raise NotImplementedError()

    def zoom(self, dy):
        raise NotImplementedError()

    def press(self, key, modifier):
        raise NotImplementedError()

    def release(self, key, modifier):
        raise NotImplementedError()

    def update(self, dt: float):
        raise NotImplementedError()

    def deselect(self):
        pass

    def select(self):
        pass


class FixedCamera(CarouselCamera):

    def __init__(
        self,
        camera_data: CameraData,
        pos: tuple[float, float, float],
        forward: tuple[float, float, float],
        up: tuple[float, float, float],
    ):
        self._data: CameraData = camera_data
        self._pos: tuple[float, float, float] = pos
        self._forward: tuple[float, float, float] = pos
        self._up: tuple[float, float, float] = pos

    def update(self, dt: float):
        self._data.position = self._pos
        self._data.up = self._up
        self._data.forward = self._forward


class OrbitCamera(CarouselCamera):

    def __init__(self):
        pass


class FlyAroundCamera(CarouselCamera):

    def __init__(self, data: CameraData):
        self._camera_data: CameraData = data

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

    def look(self, x: int, y: int, dx: int, dy: int):
        self._yaw_velocity = dx
        self._pitch_velocity = -dy

    def zoom(self, dy):
        if dy > 0:
            self._camera_data.zoom = max(min(self._camera_data.zoom * 1.25, 2.0), 0.5)
        elif dy < 0:
            self._camera_data.zoom = max(min(self._camera_data.zoom / 1.25, 2.0), 0.5)

    def press(self, symbol, modifier):
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

    def release(self, symbol, modifier):
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

    def update(self, dt: float):
        camera = self._camera_data

        if self._pitch_velocity or self._yaw_velocity:
            self._pitch = min(
                max(self._pitch + LOOK_SENSITIVITY * dt * self._pitch_velocity, -89.0),
                89.0,
            )
            self._yaw = (self._yaw + LOOK_SENSITIVITY * dt * self._yaw_velocity) % 360

            camera.up = self._global_up
            camera.forward = quaternion_rotation(
                self._global_up, (0.0, 0.0, -1.0), self._yaw
            )
            camera.up, camera.forward = grips.rotate_around_right(camera, self._pitch)

            self._pitch_velocity = 0.0
            self._yaw_velocity = 0.0

        if self._accelerate_forward:
            o_pos = camera.position
            fw = camera.forward
            fw_speed = MOVE_SPEED * self._accelerate_forward * dt
            camera.position = (
                o_pos[0] + fw_speed * fw[0],
                o_pos[1] + fw_speed * fw[1],
                o_pos[2] + fw_speed * fw[2],
            )

        if self._strafe_vertical or self._strafe_horizontal:
            strafe = (
                Vec2(self._strafe_horizontal, self._strafe_vertical).normalize()
                * MOVE_SPEED
                * dt
            )
            camera.position = grips.strafe(camera, strafe)

    def select(self):
        self._accelerate_forward = 0
        self._pitch_velocity = 0
        self._yaw_velocity = 0
        self._roll_velocity = 0


class CameraCarousel:

    def __init__(self):
        self._win = get_window()

        self.projector: PerspectiveProjector = PerspectiveProjector()
        self.projector.projection.far = 1000.0
        self.projector.view.position = (0.0, 0.0, 40.0)

        # Camera 1: Fly Around
        # Camera 2: Gimble
        # Camera 3-9: Locked Cameras, (X, Y, Z, XY, YZ, ZX, XYZ)
        self._current_camera: int = 0
        self._cameras: tuple[CarouselCamera, ...] = (
            FlyAroundCamera(self.projector.view),
        )

        self._win.push_handlers(
            self.on_mouse_motion,
            self.on_mouse_drag,
            self.on_mouse_scroll,
            self.on_key_press,
            self.on_key_release,
            self.on_update,
        )

    def switch_to(self, idx):
        if idx == self._current_camera:
            # TODO: toggle between orientations for this camera
            return

        self._cameras[self._current_camera].deselect()
        self._current_camera = idx % len(self._cameras)
        self._cameras[self._current_camera].select()

    def next(self):
        self.switch_to((self._current_camera + 1) % len(self._cameras))

    def prev(self):
        self.switch_to((self._current_camera - 1) % len(self._cameras))

    def on_mouse_motion(self, x, y, dx, dy):
        if GUI.exclusive or GUI.capturing_mouse:
            return
        self._cameras[self._current_camera].look(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if GUI.exclusive or GUI.capturing_mouse:
            return
        self.on_mouse_motion(dx, dy, x, y)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if GUI.exclusive or GUI.capturing_mouse:
            return
        self._cameras[self._current_camera].zoom(scroll_y)

    def on_key_press(self, symbol, modifiers):
        if GUI.exclusive or GUI.capturing_input:
            return
        self._cameras[self._current_camera].press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        if GUI.exclusive or GUI.capturing_input:
            return
        self._cameras[self._current_camera].release(symbol, modifiers)

    def on_update(self, delta_time: float):
        if GUI.exclusive or GUI.capturing_input:
            return
        self._cameras[self._current_camera].update(delta_time)

    def use(self):
        self.projector.use()

    @contextmanager
    def activate(self):
        try:
            with self.projector.activate() as cam:
                yield cam
        finally:
            pass
