import os
import time
import json
from typing import Optional
from datetime import datetime
from queue import Queue
from threading import Thread

from .SignalLightDataCalculator import SignalLightDataCalculator
from pytessng.Logger import logger


class SimuExportSignalLightActor:
    def __init__(self, netiface, simuiface, Online):
        # TESSNG接口
        self._netiface = netiface
        self._simuiface = simuiface

        # JSON保存路径
        self._json_save_path: Optional[str] = None

        # 信号灯数据队列
        self._signal_light_data_queue: Queue = Queue()
        # 是否正在运行
        self._is_running: bool = False
        # 发送信号灯数据线程
        self._send_data_thread: Optional[Thread] = None

    def init_data(self, params: dict) -> None:
        # 保存为JSON的配置信息
        json_config: dict = params["json_config"]

        # =============== JSON ===============
        if json_config:
            # 文件夹根路径
            folder_path = json_config["folder_path"]
            # 文件夹名称
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            folder_name = f"信号灯数据_{current_time}"
            # 轨迹数据文件夹路段
            folder_path = os.path.join(folder_path, folder_name)
            # 创建文件夹
            os.makedirs(folder_path, exist_ok=True)
            self._json_save_path = os.path.join(folder_path, "{}.json")

    def ready(self):
        # 更改运行状态
        self._is_running = True
        # 数据发送线程
        self._send_data_thread = Thread(target=self._apply_send_data)
        self._send_data_thread.start()

    def operate(self):
        # 计算轨迹数据
        signal_light_data = SignalLightDataCalculator.get_signal_light_data(self._simuiface, self._netiface)
        # 放入队列
        self._signal_light_data_queue.put(signal_light_data)

    def finish(self):
        # 清空队列
        while not self._signal_light_data_queue.empty():
            time.sleep(0.01)
        self._is_running = False
        self._send_data_thread = None

    def _apply_send_data(self):
        logger.logger_pytessng.info("The signal light data sending thread has started.")

        while True:
            time.sleep(0.01)

            # 如果队列为空
            if self._signal_light_data_queue.empty():
                # 如果在运行就继续
                if self._is_running:
                    continue
                # 如果不在运行就退出
                else:
                    logger.logger_pytessng.info("The signal light data sending thread has been closed.")
                    break

            traj_data = self._signal_light_data_queue.get()  # 使用堵塞模式

            # 当前仿真计算批次
            batch_num = traj_data["batchNum"]

            t1 = time.time()
            # 需要保存为JSON
            if self._json_save_path:
                # 当前仿真计算批次
                file_path = self._json_save_path.format(batch_num)
                # 将JSON数据写入文件
                with open(file_path, 'w', encoding="utf-8") as file:
                    json.dump(traj_data, file, indent=4, ensure_ascii=False)

            t2 = time.time()
            # json_time = round((t2 - t1) * 1000, 1)
            # print(f"\r仿真批次：{batchNum}，导出时间：{json_time}ms，队列大小：{self._signal_light_data_queue.qsize()}", end="")
