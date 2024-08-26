import os
import time
import json
from typing import Callable, Optional
from datetime import datetime
from queue import Queue
from threading import Thread
from pyproj import Proj

from .TrajectoryDataCalculator import TrajectoryDataCalculator
from ...public.communication.KafkaMessage import KafkaMessageProducer
from pytessng.Logger import logger


class SimuExportTrajectoryActor:
    def __init__(self, netiface, simuiface, Online):
        # TESSNG接口
        self._netiface = netiface
        self._simuiface = simuiface

        # JSON保存路径
        self._json_save_path: Optional[str] = None
        # kafka生产者对象
        self._kafka_producer: Optional[KafkaMessageProducer] = None

        # 比例尺
        self._p2m: Optional[Callable] = None
        # 投影
        self._proj_func: Optional[Callable] = None
        # move
        self._move_distance: Optional[dict] = None

        # 轨迹数据队列
        self._trajectory_data_queue: Queue = Queue()
        # 是否正在运行
        self._is_running: bool = False
        # 发送轨迹数据线程
        self._send_data_thread: Optional[Thread] = None

    def init_data(self, params: dict) -> None:
        # 投影字符串
        proj_string: str = params["proj_string"]
        # 保存为JSON的配置信息
        json_config: dict = params["json_config"]
        # 上传到kafka的配置信息
        kafka_config: dict = params["kafka_config"]

        # =============== JSON ===============
        if json_config:
            # 文件夹根路径
            folder_path = json_config["folder_path"]
            # 文件夹名称
            current_time = datetime.now().strftime("%Y%m%d%H%M%S")
            folder_name = f"轨迹数据_{current_time}"
            # 轨迹数据文件夹路段
            folder_path = os.path.join(folder_path, folder_name)
            # 创建文件夹
            os.makedirs(folder_path, exist_ok=True)
            self._json_save_path = os.path.join(folder_path, "{}.json")

        # =============== kafka ===============
        if kafka_config:
            ip = kafka_config["ip"]
            port = kafka_config["port"]
            topic = kafka_config["topic"]
            self._kafka_producer = KafkaMessageProducer(f"{ip}:{port}", topic)

        # =============== 工具 ===============
        # 1.比例尺转换
        scene_scale = self._netiface.sceneScale()
        self._p2m = lambda x: x * scene_scale
        # 2.投影关系
        if len(proj_string) > 0:
            self._proj_func = Proj(proj_string)
        else:
            self._proj_func = lambda x, y, inverse=None: (None, None)
        # 3.移动距离
        move_distance = self._netiface.netAttrs().otherAttrs().get("move_distance")
        if move_distance is None or "tmerc" in proj_string:
            self._move_distance = {"x_move": 0, "y_move": 0}
        else:
            self._move_distance = {"x_move": -move_distance["x_move"], "y_move": -move_distance["y_move"]}

    def ready(self):
        # 更改运行状态
        self._is_running = True
        # 数据发送线程
        self._send_data_thread = Thread(target=self._apply_send_data)
        self._send_data_thread.start()

    def operate(self):
        # 计算轨迹数据
        traj_data = TrajectoryDataCalculator.get_basic_trajectory_data(self._simuiface, self._p2m)
        # 放入队列
        self._trajectory_data_queue.put(traj_data)

    def finish(self):
        # 清空队列
        while not self._trajectory_data_queue.empty():
            time.sleep(0.01)
        self._is_running = False
        self._send_data_thread = None

    def _apply_send_data(self):
        logger.logger_pytessng.info("The trajectory data sending thread has started.")

        while True:
            time.sleep(0.01)

            # 如果队列为空
            if self._trajectory_data_queue.empty():
                # 如果在运行就继续
                if self._is_running:
                    continue
                # 如果不在运行就退出
                else:
                    logger.logger_pytessng.info("The trajectory data sending thread has been closed.")
                    break

            traj_data = self._trajectory_data_queue.get()  # 使用堵塞模式
            TrajectoryDataCalculator.get_complete_trajectory_data(traj_data, self._proj_func, self._move_distance)

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
            # 需要上传至kafka
            if self._kafka_producer:
                traj_data_json = json.dumps(traj_data)
                self._is_running = self._kafka_producer.send_message(traj_data_json)
                if not self._is_running:
                    logger.logger_pytessng.info("Due to Kafka data sending failure, the trajectory data sending thread is closed.")
                    break

            t3 = time.time()
            json_time = round((t2 - t1) * 1000, 1)
            kafka_time = round((t3 - t2) * 1000, 1)

            # logger.logger_pytessng.info(f"仿真批次：{batchNum}，导出时间：{json_time}ms，上传时间：{kafka_time}ms，队列大小：{self._trajectory_data_queue.qsize()}")
            print(f"\r仿真批次：{batch_num}，导出时间：{json_time}ms，上传时间：{kafka_time}ms，队列大小：{self._trajectory_data_queue.qsize()}", end="")
