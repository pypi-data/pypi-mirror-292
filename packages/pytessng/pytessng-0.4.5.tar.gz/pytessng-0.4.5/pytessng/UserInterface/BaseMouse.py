from abc import ABC, abstractmethod
from PySide2.QtGui import QMouseEvent, QKeyEvent


class BaseMouse(ABC):
    def handle_mouse_event(self, event, mode: str = "press") -> None:
        if mode == "press":
            self.handle_mouse_press_event(event)
        elif mode == "release":
            self.handle_mouse_release_event(event)
        elif mode == "move":
            self.handle_mouse_move_event(event)

    @abstractmethod
    def handle_mouse_press_event(self, event: QMouseEvent) -> None:
        pass

    def handle_mouse_release_event(self, event: QMouseEvent) -> None:
        pass

    def handle_mouse_move_event(self, event: QMouseEvent) -> None:
        pass

    def handle_key_press_event(self, event: QKeyEvent) -> None:
        pass
