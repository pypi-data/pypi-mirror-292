import ctypes

# Класс для управления событиями мыши
class MouseController:
    def __init__(self):
        # Константы для события мыши
        self.MOUSEEVENTF_MOVE = 0x0001
        self.MOUSEEVENTF_ABSOLUTE = 0x8000

    # Метод для перемещения мыши
    def move(self, x, y):
        ctypes.windll.user32.mouse_event(self.MOUSEEVENTF_MOVE, x, y, 0, 0)

    # Метод для получения состояния кнопок мыши (левая и правая кнопка)
    def get_key_state(self, vk_code):
        return ctypes.windll.user32.GetKeyState(vk_code)


# Создаем объект контроллера мыши
mouse = MouseController()
