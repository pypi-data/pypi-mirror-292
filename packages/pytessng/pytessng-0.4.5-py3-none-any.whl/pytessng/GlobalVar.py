from typing import Callable
from PySide2.QtWidgets import QAction


class GlobalVar:
    # ========== MyNet.py ==========
    # 与鼠标事件相关的按钮
    actions_related_to_mouse_event: dict = {}
    # 只能正式版本使用的按钮
    actions_only_official_version: list = []

    # 给MySimulator添加仿真观察者的函数
    attach_observer_of_my_net: Callable = None
    # 给MySimulator移除仿真观察者的函数
    detach_observer_of_my_net: Callable = None

    # ========== MySimulator.py ==========
    # 给MySimulator添加仿真观察者的函数
    attach_observer_of_my_simulator: Callable = None
    # 给MySimulator移除仿真观察者的函数
    detach_observer_of_my_simulator: Callable = None
