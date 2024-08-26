from PySide2.QtGui import Qt, QMouseEvent, QKeyEvent, QWheelEvent, QVector3D
from PySide2.QtCore import QEvent, QPoint

from pytessng.DLLs.Tessng import PyCustomerNet, tessngIFace
from pytessng.GlobalVar import GlobalVar


class MyNet(PyCustomerNet):
    def __init__(self):
        super().__init__()
        self.iface = tessngIFace()
        self.netiface = self.iface.netInterface()
        self.guiiface = self.iface.guiInterface()
        self.view = self.netiface.graphicsView()

        # 当前观察者
        self._current_observer = None
        # 上一个按钮
        self._last_action = None
        # 鼠标当前位置
        self._mouse_pos = None

    # 重载方法：加载路网前执行
    def beforeLoadNet(self) -> None:
        # =============== 打印属性信息 ===============
        attrs = self.netiface.netAttrs().otherAttrs()
        print("=" * 66)
        print("Load network! Network attrs:")
        if attrs:
            for k, v in attrs.items():
                print(f"\t{k:<15}:{' ' * 5}{v}")
        else:
            print("\t(EMPTY)")
        print("=" * 66, "\n")

    # 重载方法：加载路网后执行
    def afterLoadNet(self) -> None:
        # 能执行这里说明是正版key就开启相关功能
        for action in GlobalVar.actions_only_official_version:
            action.setEnabled(True)

    # 重载方法：控制曲率最小距离
    def ref_curvatureMinDist(self, item_type: int, item_id: int, ref_min_dist):
        ref_min_dist.value = 0.1
        return True

    # 自定义方法：添加观察者
    def attach_observer(self, observer_obj):
        self._current_observer = observer_obj

    # 自定义方法：移除观察者
    def detach_observer(self):
        self._current_observer = None

    # 重载方法：鼠标点击后触发
    def afterViewMousePressEvent(self, event: QMouseEvent):
        self._apply_move_action(event, mode="press")
        # 执行观察者的动作
        if self._current_observer is not None:
            self._current_observer.handle_mouse_event(event, mode="press")

    # 重载方法：鼠标释放后触发
    def afterViewMouseReleaseEvent(self, event: QMouseEvent):
        self._apply_move_action(event, mode="release")
        # 执行观察者的动作
        if self._current_observer is not None:
            self._current_observer.handle_mouse_event(event, mode="release")

    # 重载方法：鼠标移动后触发
    def afterViewMouseMoveEvent(self, event: QMouseEvent) -> None:
        self._mouse_pos = self.view.mapToScene(event.pos())
        # 执行观察者的动作
        if self._current_observer is not None:
            self._current_observer.handle_mouse_event(event, mode="move")

    # 重载方法：键盘按下后触发
    def afterViewKeyPressEvent(self, event: QKeyEvent) -> None:
        # 执行观察者的动作
        if self._current_observer is not None:
            self._current_observer.handle_key_press_event(event)

    # 重载方法：鼠标滚轮滚动后触发
    def afterViewWheelEvent(self, event: QWheelEvent) -> None:
        if not self._mouse_pos:
            return

        mouse_pos = event.pos()
        scene_mouse_pos = self.view.mapToScene(mouse_pos)

        win_width, win_height = self.guiiface.winWidth() - 10, self.guiiface.winHeight() - 100
        center_pos = QPoint(win_width // 2, win_height // 2)
        scene_center_pos = self.view.mapToScene(center_pos)

        dx = scene_center_pos.x() - scene_mouse_pos.x()
        dy = scene_center_pos.y() - scene_mouse_pos.y()

        new_x = self._mouse_pos.x() + dx
        new_y = self._mouse_pos.y() + dy

        self.view.centerOn(new_x, new_y)

    # # 拖拽路段后触发
    # def afterLinkVertexMove(self, link, index: int, pressPoint, releasePoint):
    #     points = link.centerBreakPoint3Ds()
    #     points[index] = QVector3D(releasePoint.x(), releasePoint.y(), points[index].z())
    #     self.netiface.updateLink3DWithPoints(link, points)

    # 自定义方法：为了鼠标中键能够移动界面
    def _apply_move_action(self, event: QMouseEvent, mode: str):
        if event.button() == Qt.MiddleButton:
            # 按下模式
            if mode == "press":
                # 记录此时的按钮
                for actions in [self.guiiface.netToolBar().actions(), self.guiiface.operToolBar().actions()]:
                    for action in actions:
                        if action.isChecked():
                            self._last_action = action
                            break

                # 将按钮设置为移动
                self.guiiface.actionPan().trigger()

                # 创建一个左键点击事件
                pos = event.pos()
                left_click_event = QMouseEvent(QEvent.Type.MouseButtonPress, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
                self.view.mousePressEvent(left_click_event)

            # 释放模式
            elif mode == "release":
                # 创建一个左键释放事件
                pos = event.pos()
                left_click_event = QMouseEvent(QEvent.Type.MouseButtonRelease, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
                self.view.mouseReleaseEvent(left_click_event)

                # 恢复按钮
                if self._last_action is not None:
                    self._last_action.trigger()
                    self._last_action = None
