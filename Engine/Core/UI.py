import imgui
from imgui.integrations.glfw import GlfwRenderer

class UI:
    def __init__(self):
        self._impl = None
    
    def InitUI(self, window):
        imgui.create_context()
        self._impl = GlfwRenderer(window)
        
    def BeginFrame(self):
        self._impl.process_inputs()
        imgui.new_frame()
        
    def EndFrame(self):
        imgui.render()
        self._impl.render(imgui.get_draw_data())
    
    @staticmethod
    def Begin(name: str, flags=0):
        imgui.begin(name, True, flags)

    @staticmethod
    def End():
        imgui.end()
        
    @staticmethod
    def IsHovered() -> bool:
        io = imgui.get_io()
        return io.want_capture_mouse
        
    # === WIDGET WRAPPERS ===
    # TODO Ensure that all wrappers work with python version of ImGui
    @staticmethod
    def Text(msg: str):
        return imgui.text(msg)

    @staticmethod
    def Button(label: str) -> bool:
        return imgui.button(label)

    @staticmethod
    def SliderInt(label: str, value: int, min_value: int, max_value: int):
        changed, new_val = imgui.slider_int(label, value, min_value, max_value)
        return new_val, changed

    @staticmethod
    def SliderFloat(label: str, value: float, min_value: float, max_value: float):
        changed, new_val = imgui.slider_float(label, value, min_value, max_value)
        return new_val, changed

    @staticmethod
    def SliderFloat3(label: str, value: list[float], min_value: float, max_value: float):
        changed, new_val = imgui.slider_float3(label, value[0], value[1], value[2], min_value, max_value)
        return new_val, changed

    @staticmethod
    def Checkbox(label: str, value: bool):
        changed, new_val = imgui.checkbox(label, value)
        return new_val, changed

    @staticmethod
    def ColorPicker(label: str, color: list[float]):
        changed, new_val = imgui.color_picker3(label, color)
        return new_val, changed

    @staticmethod
    def CheckboxState(label: str, default: bool = False):
        # stateful version
        old = UI._state.get(label, default)
        changed, new_val = imgui.checkbox(label, old)
        if changed:
            UI._state[label] = new_val
        return new_val

    @staticmethod
    def SliderIntState(label: str, default: int, min_value: int, max_value: int):
        old = UI._state.get(label, default)
        changed, new_val = imgui.slider_int(label, old, min_value, max_value)
        if changed:
            UI._state[label] = new_val
        return new_val