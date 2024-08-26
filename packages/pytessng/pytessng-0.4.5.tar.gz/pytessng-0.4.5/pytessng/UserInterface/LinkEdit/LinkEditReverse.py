from typing import Callable
from PySide2.QtWidgets import QGraphicsRectItem, QGraphicsPathItem, QMessageBox, QAction
from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QColor, QPainterPath, QPen

from ..BaseUI import BaseClass
from ..BaseMouse import BaseMouse
from pytessng.GlobalVar import GlobalVar
from pytessng.ToolInterface import MyOperation


class LinkEditReverse(BaseClass):
    name: str = "框选反转路段"
    mode: str = "reverse"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 按钮
        self.action: QAction = GlobalVar.actions_related_to_mouse_event["reverse"]
        # 将按钮与状态改变函数关联
        self.action.toggled.connect(self.monitor_check_state)

    # 重写抽象父类BaseUserInterface的方法
    def load(self):
        if self.action.isChecked():
            # 为了关联生效
            self.action.setChecked(False)
            self.action.setChecked(True)

    # 鼠标事件相关特有方法
    def monitor_check_state(self, checked):
        if checked:
            # 修改文字
            self.action.setText("取消选中框选反转路段")

            # 添加MyNet观察者
            netiface = self.iface.netInterface()
            mouse_reverse = MouseReverse(netiface, self.apply_reverse_links, self.utils)
            GlobalVar.attach_observer_of_my_net(mouse_reverse)

            # 修改按钮为【取消工具】
            guiiface = self.iface.guiInterface()
            guiiface.actionNullGMapTool().trigger()

            # 其他按钮取消勾选
            for action in GlobalVar.actions_related_to_mouse_event.values():
                if action.text() not in ["框选反转路段", "取消选中框选反转路段"]:
                    action.setChecked(False)
        else:
            # 修改文字
            self.action.setText("框选反转路段")

            # 移除MyNet观察者
            GlobalVar.detach_observer_of_my_net()

    def apply_reverse_links(self, params: dict):
        MyOperation.apply_link_edit_operation(self, params)


class MouseReverse(BaseMouse):
    def __init__(self, netiface, apply_reverse_links_func: Callable, utils):
        # 获取画布
        self.netiface = netiface
        self.scene = self.netiface.graphicsScene()

        # 执行函数
        self.apply_reverse_links_func = apply_reverse_links_func
        # 工具包
        self.utils = utils

        # 坐标
        self.pos1 = None
        self.pos2 = None
        # 透明框
        self.transparent_box_item = None
        # 高亮路段
        self.highlighted_line_items = []

    def handle_mouse_press_event(self, event):
        # 按下左键
        if event.button() == Qt.LeftButton:
            self.pos1 = self.netiface.graphicsView().mapToScene(event.pos())

    def handle_mouse_release_event(self, event) -> None:
        # 弹起左键
        if event.button() == Qt.LeftButton:
            self.pos2 = self.netiface.graphicsView().mapToScene(event.pos())
            # 执行删除
            params = {
                "p1": self.pos1,
                "p2": self.pos2,
                "confirm_function": self.show_confirm_dialog,
                "highlight_function": self.highlighted_links,
                "restore_function": self.restore_canvas,
            }
            self.apply_reverse_links_func(params)

            # 保险起见再次还原画布（防止仿真中操作）
            self.restore_canvas()

    def handle_mouse_move_event(self, event) -> None:
        if self.pos1 is None:
            return

        # 清除上一个
        if self.transparent_box_item is not None:
            self.scene.removeItem(self.transparent_box_item)

        # 计算位置和长宽
        p1 = self.pos1
        p2 = self.netiface.graphicsView().mapToScene(event.pos())
        x1, x2 = sorted([p1.x(), p2.x()])
        y1, y2 = sorted([p1.y(), p2.y()])
        width = x2 - x1
        height = y2 - y1

        # 创建透明方框item
        rect = QRectF(x1, y1, width, height)
        self.transparent_box_item = QGraphicsRectItem(rect)
        self.transparent_box_item.setPen(QColor(0, 255, 0))  # 设置边框颜色
        self.transparent_box_item.setBrush(QColor(255, 0, 0, 50))  # 设置填充颜色和透明度

        # 添加item到scene
        self.scene.addItem(self.transparent_box_item)

    # 显示确认删除对话框，作为参数
    def show_confirm_dialog(self, link_count: int, mode: int):
        text = "全部" if mode == 1 else "部分"
        messages = {
            "title": "反转框选路段",
            "content": f"有{link_count}条路段被{text}选中，是否反转",
            "yes": "反转",
        }
        confirm = self.utils.show_confirm_dialog(messages, default_result='yes')
        return confirm == QMessageBox.Yes

    # 高亮路段
    def highlighted_links(self, links):
        for link in links:
            for points in [link.centerBreakPoints(), link.leftBreakPoints(), link.rightBreakPoints()]:
                # 创建一个 QPainterPath 并将点添加到路径中
                path = QPainterPath()
                path.moveTo(points[0])
                for point in points[1:]:
                    path.lineTo(point)
                # 创建一个 QGraphicsPathItem 并设置路径
                path_item = QGraphicsPathItem(path)

                # 创建一个 QPen 并设置宽度和颜色
                pen = QPen(QColor(255, 255, 0))
                pen.setWidth(1)
                # 将 QPen 设置到路径项上
                path_item.setPen(pen)

                # 将路径项添加到场景中
                self.scene.addItem(path_item)
                self.highlighted_line_items.append(path_item)

    # 还原画布
    def restore_canvas(self):
        self.pos1 = None
        # 透明方框
        if self.transparent_box_item is not None:
            self.scene.removeItem(self.transparent_box_item)
        # 路段高亮
        for item in self.highlighted_line_items:
            self.scene.removeItem(item)
