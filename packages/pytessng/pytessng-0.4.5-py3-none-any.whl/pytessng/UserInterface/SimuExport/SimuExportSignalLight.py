import os
from PySide2.QtWidgets import QCheckBox, QLineEdit, QPushButton

from ..BaseUI import BaseUserInterface, MyQHBoxLayout, MyQVBoxLayout, MyQGroupBox
from pytessng.ToolInterface import MyOperation
from pytessng.Config import PathConfig


class SimuExportSignalLight(BaseUserInterface):
    name = "信号灯数据导出"

    # 记忆参数
    memory_params = {
        "is_json": False,
        "json_path": PathConfig.DEFAULT_SAVE_TRAJ_DIR_PATH,
    }

    # 设置界面布局
    def set_widget_layout(self):
        # 第一行：勾选框
        self.check_box_json = QCheckBox('保存为Json文件')
        # 第二行：文本和按钮
        self.line_edit_json = QLineEdit()
        self.line_edit_json.setFixedWidth(500)
        self.button_json_save = QPushButton('选择保存位置')
        # 第三行：按钮
        self.button = QPushButton('确定')

        # 总体布局
        layout = MyQVBoxLayout([
            self.check_box_json,
            MyQGroupBox(
                    MyQVBoxLayout([
                        MyQHBoxLayout([self.line_edit_json, self.button_json_save])
                    ])
            ),
            self.button
        ])
        self.setLayout(layout)

    def set_monitor_connect(self):
        self.check_box_json.stateChanged.connect(self.apply_monitor_state)
        self.line_edit_json.textChanged.connect(self.apply_monitor_state)

    def set_button_connect(self):
        self.button_json_save.clicked.connect(self.select_folder)
        self.button.clicked.connect(self.apply_button_action)

    def set_default_state(self):
        if self.memory_params["is_json"]:
            self.check_box_json.setChecked(True)
        if self.memory_params["json_path"] is not None:
            self.line_edit_json.setText(self.memory_params["json_path"])

        self.apply_monitor_state()

        # 创建默认保存文件夹
        if not os.path.exists(PathConfig.DEFAULT_SAVE_SIGNAL_DIR_PATH):
            os.makedirs(PathConfig.DEFAULT_SAVE_SIGNAL_DIR_PATH, exist_ok=True)

    def apply_monitor_state(self):
        # 勾选框的状态
        enabled_checkBox_json = self.check_box_json.isChecked()

        # 设置可用状态
        self.line_edit_json.setEnabled(enabled_checkBox_json)
        self.button_json_save.setEnabled(enabled_checkBox_json)

        # Json有无问题
        folder_path = self.line_edit_json.text()
        isdir = os.path.isdir(folder_path)
        json_state = (not enabled_checkBox_json) or (enabled_checkBox_json and isdir)

        self.button.setEnabled(json_state)

    def apply_button_action(self):
        # 获取保存为JSON的配置
        if self.check_box_json.isChecked():
            self.memory_params["is_json"] = True
            json_path = self.line_edit_json.text()
            self.memory_params["json_path"] = json_path
            traj_json_config = {
                "folder_path": json_path,
            }
        else:
            self.memory_params["is_json"] = False
            traj_json_config = None

        if traj_json_config:
            params = {
                "json_config": traj_json_config,
            }
        # 否则传入空配置
        else:
            params = {}
        MyOperation.apply_simu_data_import_or_export_operation("simu_export_signal_light", params)

        # 关闭窗口
        self.close()

    # 特有方法：选择JSON保存文件夹
    def select_folder(self):
        folder_path = self.utils.open_folder()
        if folder_path:
            # 显示文件路径在LineEdit中
            self.line_edit_json.setText(folder_path)
