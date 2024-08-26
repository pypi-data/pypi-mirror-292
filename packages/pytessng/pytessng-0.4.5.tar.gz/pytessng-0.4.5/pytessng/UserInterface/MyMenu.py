import traceback
from functools import partial
from typing import Optional
from PySide2.QtWidgets import QMenu, QAction, QWidget, QMessageBox
from PySide2.QtGui import QIcon

from .Utils import Utils
from .NetworkImport.NetworkImportOpendrive import NetworkImportOpendrive
from .NetworkImport.NetworkImportShape import NetworkImportShape
from .NetworkImport.NetworkImportOpenstreetmap import NetworkImportOpenstreetmap
from .NetworkImport.NetworkImportJson import NetworkImportJson
from .NetworkImport.NetworkImportExcel import NetworkImportExcel
from .NetworkImport.NetworkImportAidaroe import NetworkImportAidaroe
from .NetworkImport.NetworkImportAnnex import NetworkImportAnnex
from .NetworkExport.NetworkExportOpendrive import NetworkExportOpendrive
from .NetworkExport.NetworkExportShape import NetworkExportShape
from .NetworkExport.NetworkExportGeojson import NetworkExportGeojson
from .NetworkExport.NetworkExportUnity import NetworkExportUnity
from .NetworkExport.NetworkExportJson import NetworkExportJson
from .LinkEdit.LinkEditCreate import LinkEditCreate
from .LinkEdit.LinkEditSplit import LinkEditSplit
from .LinkEdit.LinkEditRemove import LinkEditRemove
from .LinkEdit.LinkEditReverse import LinkEditReverse
from .LinkEdit.LinkEditMerge import LinkEditMerge
from .LinkEdit.LinkEditSimplify import LinkEditSimplify
from .LinkEdit.LinkEditLimitC import LinkEditLimitC
from .LinkEdit.LinkEditLimitL import LinkEditLimitL
from .LinkEdit.LinkEditRecalculate import LinkEditRecalculate
from .LinkEdit.LinkEditModify import LinkEditModify
from .LinkEdit.LinkEditMove import LinkEditMove
from .LinkEdit.LinkEditRotate import LinkEditRotate
from .SimuImport.SimuImportTrajectory import SimuImportTrajectory
from .SimuExport.SimuExportTrajectory import SimuExportTrajectory
from .SimuExport.SimuExportSignalLight import SimuExportSignalLight
from .FileExport.FileExportPileNumber import FileExportPileNumber
from .FileExport.FileExportGrid import FileExportGrid
from .Other.OpenInstruction import OpenInstruction
from .Other.OpenExamples import OpenExamples
from .Other.SendAdvise import SendAdvise
from .View.ViewAttrs import ViewAttrs
from .View.ViewXodrJunction import ViewXodrJunction
from .View.ViewXodrRoad import ViewXodrRoad
from pytessng.DLLs.Tessng import tessngIFace
from pytessng.Config import UIConfig
from pytessng.GlobalVar import GlobalVar


class MyMenu(QMenu):
    # 按钮名称和类映射
    action_name_and_class_mapping = {
        "network_import": {
            "opendrive": ("action_network_import_opendrive", NetworkImportOpendrive),
            "shape": ("action_network_import_shape", NetworkImportShape),
            "osm": ("action_network_import_openstreetmap", NetworkImportOpenstreetmap),
            "json": ("action_network_import_json", NetworkImportJson),
            "excel": ("action_network_import_excel", NetworkImportExcel),
            "aidaroe": ("action_network_import_aidaroe", NetworkImportAidaroe),
            "annex": ("action_network_import_annex", NetworkImportAnnex),
        },
        "network_export": {
            "opendrive": ("action_network_export_opendrive", NetworkExportOpendrive),
            "shape": ("action_network_export_shape", NetworkExportShape),
            "geojson": ("action_network_export_geojson", NetworkExportGeojson),
            "unity": ("action_network_export_unity", NetworkExportUnity),
            "json": ("action_network_export_json", NetworkExportJson),
        },
        "link_edit": {
            "create": ("action_link_edit_create", LinkEditCreate),
            "split": ("action_link_edit_split", LinkEditSplit),
            "remove": ("action_link_edit_remove", LinkEditRemove),
            "reverse": ("action_link_edit_reverse", LinkEditReverse),
            "merge": ("action_link_edit_merge", LinkEditMerge),
            "simplify": ("action_link_edit_simplify", LinkEditSimplify),
            "limit_c": ("action_link_edit_limit_c", LinkEditLimitC),
            "limit_l": ("action_link_edit_limit_l", LinkEditLimitL),
            "recalculate": ("action_link_edit_recalculate", LinkEditRecalculate),
            "modify": ("action_link_edit_modify", LinkEditModify),
            "move": ("action_link_edit_move", LinkEditMove),
            "rotate": ("action_link_edit_rotate", LinkEditRotate),
        },
        "simu_data_import": {
            "trajectory": ("action_simu_import_trajectory", SimuImportTrajectory),
        },
        "simu_data_export": {
            "trajectory": ("action_simu_export_trajectory", SimuExportTrajectory),
            "signal_light": ("action_simu_export_signal_light", SimuExportSignalLight),
        },
        "config_file_export": {
            "pile_number": ("action_file_export_pile_number", FileExportPileNumber),
            "grid": ("action_file_export_grid", FileExportGrid),
        },
        "other": {
            "instruction": ("action_other_instruction", OpenInstruction),
            "examples": ("action_other_examples", OpenExamples),
            "advise": ("action_other_advise", SendAdvise),
        },
        "view": {
            "attrs": ("action_view_attrs", ViewAttrs),
            "xodr_junction": ("action_view_xodr_junction", ViewXodrJunction),
            "xodr_road": ("action_view_xodr_road", ViewXodrRoad),
        }
    }
    # 工具包
    utils = Utils

    def __init__(self, *args, extension: bool = False):
        super().__init__(*args)
        self.iface = tessngIFace()
        self.guiiface = self.iface.guiInterface()
        self.win = self.guiiface.mainWindow()

        # 是否功能拓展
        self.extension: bool = extension
        # 当前菜单
        self.current_dialog: Optional[QWidget] = None

        # 与鼠标事件相关的按钮
        self.actions_related_to_mouse_event: dict = {}
        # 只能正式版本使用的按钮
        self.actions_only_official_version: list = []

        # 初始化
        self.init()

    def init(self):
        # 设置对象名和标题
        self.setObjectName("pytessng")
        self.setTitle("数据导入导出")

        # 添加菜单
        self.add_menus_and_actions()
        # 关联按钮与槽函数
        self.connect_actions_and_functions()
        # 隐藏配置项
        self.hide_extended_actions()
        # 添加到主界面
        self.add_to_main_window()

        # 统计用户数量
        self.utils.send_message("operation", "visit")

    def add_menus_and_actions(self):
        # =============== 1.路网创建 ===============
        self.menu_network_import = self.addMenu('路网数据导入')
        # 1.1.导入OpenDrive
        self.action_network_import_opendrive = self.menu_network_import.addAction('导入OpenDrive (.xodr)')
        # 1.2.导入Shape
        self.action_network_import_shape = self.menu_network_import.addAction('导入Shape')
        # 1.3.导入OpenStreetMap
        self.action_network_import_openstreetmap = self.menu_network_import.addAction('导入OpenStreetMap')
        # 1.4.导入Json
        self.action_network_import_json = self.menu_network_import.addAction('导入Json')
        # 1.5.导入Excel
        self.action_network_import_excel = self.menu_network_import.addAction('导入Excel (.xlsx/.xls/.csv)')
        # 1.6.导入Aidaroe
        self.action_network_import_aidaroe = self.menu_network_import.addAction('导入Aidaroe (.jat)')
        # 1.7.导入路网元素
        self.action_network_import_annex = self.menu_network_import.addAction('导入路网元素 (.json)')

        # =============== 2.路网数据导出 ===============
        self.menu_network_export = self.addMenu('路网数据导出')
        # 2.1.导出OpenDrive
        self.action_network_export_opendrive = self.menu_network_export.addAction('导出为OpenDrive (.xodr)')
        # 2.2.导出Shape
        self.action_network_export_shape = self.menu_network_export.addAction('导出为Shape')
        # 2.3.导出GeoJson
        self.action_network_export_geojson = self.menu_network_export.addAction('导出为GeoJson')
        # 2.4.导出Unity
        self.action_network_export_unity = self.menu_network_export.addAction('导出为Unity (.json)')
        # 2.5.导出Json
        self.action_network_export_json = self.menu_network_export.addAction('导出为Json')

        # =============== 3.路段编辑 ===============
        self.menu_link_edit = self.addMenu('路段编辑')
        # 3.1.创建路段
        self.action_link_edit_create = self.menu_link_edit.addAction('创建路段')
        # 3.2.打断路段
        self.action_link_edit_split = QAction("打断路段")
        self.menu_link_edit.addAction(self.action_link_edit_split)
        self.action_link_edit_split.setCheckable(True)  # 开启是否勾选(1/4)
        # 3.3.删除路段
        self.action_link_edit_remove = QAction("框选删除路段")
        self.menu_link_edit.addAction(self.action_link_edit_remove)
        self.action_link_edit_remove.setCheckable(True)  # 开启是否勾选(2/4)
        # 3.4.逆序路段
        self.action_link_edit_reverse = QAction("框选反转路段")
        self.menu_link_edit.addAction(self.action_link_edit_reverse)
        self.action_link_edit_reverse.setCheckable(True)  # 开启是否勾选(3/4)
        # 3.5.合并路段
        self.action_link_edit_merge = self.menu_link_edit.addAction('合并路段（路网级）')
        # 3.6.简化路段点位
        self.action_link_edit_simplify = self.menu_link_edit.addAction('简化路段点位（路网级）')
        # 3.7.限制连接段最小长度
        self.action_link_edit_limit_c = self.menu_link_edit.addAction('限制连接段最小长度（路网级）')
        # 3.8.限制路段最大长度
        self.action_link_edit_limit_l = self.menu_link_edit.addAction('限制路段最大长度（路网级）')
        # 3.9.重新计算路段中心线
        self.action_link_edit_recalculate = self.menu_link_edit.addAction('重新计算路段中心线（路网级）')
        # 3.10.修改路段限速
        self.action_link_edit_modify = self.menu_link_edit.addAction('修改路段限速（路网级）')
        # 3.11.移动路网
        self.action_link_edit_move = self.menu_link_edit.addAction('移动路网')
        # 3.12.旋转路网
        self.action_link_edit_rotate = self.menu_link_edit.addAction('旋转路网')

        # =============== 4.仿真数据导入 ===============
        self.menu_simu_import = self.addMenu('仿真数据导入')
        # 4.1.导出轨迹数据
        self.action_simu_import_trajectory = QAction("导入轨迹数据")
        self.menu_simu_import.addAction(self.action_simu_import_trajectory)

        # =============== 5.仿真数据导出 ===============
        self.menu_simu_export = self.addMenu('仿真数据导出')
        # 5.1.导出轨迹数据
        self.action_simu_export_trajectory = QAction("导出轨迹数据")
        self.menu_simu_export.addAction(self.action_simu_export_trajectory)
        # 5.2.导出信号灯数据
        self.action_simu_export_signal_light = QAction("导出信号灯数据")
        self.menu_simu_export.addAction(self.action_simu_export_signal_light)

        # =============== 6.配置文件导出 ===============
        self.menu_file_export = self.addMenu('配置文件导出')
        # 6.1.导出桩号数据
        self.action_file_export_pile_number = self.menu_file_export.addAction('导出桩号数据')
        # 6.2.导出选区数据
        self.action_file_export_grid = QAction("导出选区数据")
        self.menu_file_export.addAction(self.action_file_export_grid)
        self.action_file_export_grid.setCheckable(True)  # 开启是否勾选(4/4)

        # =============== 7.更多 ===============
        self.menu_other = self.addMenu('更多')
        # 7.1.打开说明书
        self.action_other_instruction = self.menu_other.addAction("打开说明书")
        # 7.2.打开样例
        self.action_other_examples = self.menu_other.addAction("打开路网创建样例")
        # 7.3.提出建议
        self.action_other_advise = self.menu_other.addAction("提交用户反馈")

        # =============== 8.查看 ===============
        # 8.1.查看路网属性
        self.action_view_attrs = self.menu_other.addAction('查看路网属性')
        # 8.2.查看junction
        self.action_view_xodr_junction = self.menu_other.addAction('查看junction (xodr)')
        # 8.3.查看road
        self.action_view_xodr_road = self.menu_other.addAction('查看road (xodr)')

        # =============== 鼠标事件相关 ===============
        # 与鼠标事件相关的按钮
        self.actions_related_to_mouse_event: dict = {
            "split": self.action_link_edit_split,
            "remove": self.action_link_edit_remove,
            "reverse": self.action_link_edit_reverse,
            "grid": self.action_file_export_grid,
        }

        # =============== 试用版相关 ===============
        # 只能正式版本使用的按钮
        self.actions_only_official_version: list = [
            self.action_link_edit_split,
            self.action_link_edit_remove,
            self.action_link_edit_reverse,
            self.action_simu_import_trajectory,
            self.action_simu_export_trajectory,
            self.action_simu_export_signal_light,
            self.action_file_export_grid,
        ]
        # 若是正版会在afterLoadNet中启用
        for action in self.actions_only_official_version:
            action.setEnabled(False)

    # 将按钮与函数关联
    def connect_actions_and_functions(self):
        # 关联按钮与功能函数
        for first_class, second_class_mapping in self.action_name_and_class_mapping.items():
            for second_class, action_and_class in second_class_mapping.items():
                # 获取按钮名称
                action_name = action_and_class[0]
                # 如果有这个按钮，而且也不是None
                if hasattr(self, action_name):
                    # 获取按钮
                    action = getattr(self, action_name)
                    # 关联函数
                    action.triggered.connect(partial(self.apply_action, first_class, second_class))

        # 关联在线地图导入OSM的槽函数
        self.win.forPythonOsmInfo.connect(NetworkImportOpenstreetmap.create_network_online)
        # 关闭在线地图
        self.win.showOsmInline(False)

        # 关联普通按钮与取消MyNet观察者的函数
        def uncheck():
            # 移除观察者
            GlobalVar.detach_observer_of_my_net()
            # 取消按钮选中
            for action0 in GlobalVar.actions_related_to_mouse_event.values():
                action0.setChecked(False)

        for actions in [self.guiiface.netToolBar().actions(), self.guiiface.operToolBar().actions()]:
            for action in actions:
                if not action or action.text() == "取消工具":
                    continue
                action.triggered.connect(uncheck)

    # 设置按钮隐藏
    def hide_extended_actions(self):
        # 如果是完整版
        if self.extension:
            return

        # 设置隐藏按钮
        for first_class, second_class_list in UIConfig.Menu.extension_list:
            # 如果是列表就单个隐藏
            if type(second_class_list) == list:
                for second_class in second_class_list:
                    action_name = f"action_{first_class}_{second_class}"
                    action = getattr(self, action_name)
                    action.setVisible(False)
            # 如果不是列表就是全部隐藏
            elif second_class_list == "all":
                menu_name = f"menu_{first_class}"
                menu = getattr(self, menu_name)
                menu.menuAction().setVisible(False)

    # 将菜单栏添加到主窗口
    def add_to_main_window(self):
        # 主界面菜单栏
        menu_bar = self.guiiface.menuBar()
        # 添加菜单栏
        menu_bar.insertAction(menu_bar.actions()[-1], self.menuAction())

        # 查看菜单栏
        view_menu = self.guiiface.viewMenu()
        view_menu.addAction(self.action_view_attrs)
        view_menu.addAction(self.action_view_xodr_junction)
        view_menu.addAction(self.action_view_xodr_road)

        # 工具栏
        # self.guiiface.operToolBar().addAction(self.action_link_edit_remove)

    # 执行操作
    def apply_action(self, first_class: str, second_class: str):
        # =============== 特殊情况特殊处理 ===============
        if first_class == "network_import" and second_class == "osm":
            messages = {
                "title": "OSM导入模式",
                "content": "请选择导入离线文件或获取在线地图",
                "yes": "导入离线文件",
                "no": "获取在线地图",
            }
            result = self.utils.show_confirm_dialog(messages)

            # No键
            if result == QMessageBox.No:
                # 显示在线地图
                self.win.showOsmInline(True)
                return
            # 取消键
            elif result == QMessageBox.Cancel:
                return
        # =============================================

        try:
            # 关闭上一个窗口
            if self.current_dialog:
                self.current_dialog.close()
            # 获取对应类
            action_class = self.action_name_and_class_mapping[first_class][second_class][1]
            dialog = action_class()
            # 显示窗口
            if dialog:
                self.current_dialog = dialog
                self.current_dialog.load()
                self.current_dialog.show()
        except:
            self.utils.show_info_box("该功能暂未开放！")
            traceback.print_exc()
