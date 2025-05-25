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
        
    # === WIDGET WRAPPERS ===
    @staticmethod
    def Text(msg: str):
        imgui.text(msg)

    @staticmethod
    def Button(label: str) -> bool:
        return imgui.button(label)

    @staticmethod
    def SliderInt(label: str, value: int, min_value: int, max_value: int):
        return imgui.slider_int(label, value, min_value, max_value)

    @staticmethod
    def SliderFloat(label: str, value: float, min_value: float, max_value: float):
        return imgui.slider_float(label, value, min_value, max_value)

    @staticmethod
    def SliderFloat3(label: str, vec3: list[float], min_value: float, max_value: float):
        return imgui.slider_float3(label, vec3, min_value, max_value)

    @staticmethod
    def Checkbox(label: str, value: bool):
        return imgui.checkbox(label, value)

    @staticmethod
    def ColorPicker(label: str, color: list[float]):
        return imgui.color_picker3(label, color)
