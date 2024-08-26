import math
from typing import Union
from shapely.geometry import Polygon


POINT = Union[list, tuple]


class LineBase:
    # 计算两点间距
    @staticmethod
    def calculate_distance_between_two_points(p1: POINT, p2: POINT) -> float:
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

    # 计算两点连线与y正轴的顺时针角度(0~360)
    @staticmethod
    def calculate_angle_with_y_axis(p1: POINT, p2: POINT) -> float:
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        delta_x = x2 - x1
        delta_y = y2 - y1
        # 使用 atan2 计算角度（弧度）
        angle_rad = math.atan2(delta_x, delta_y)
        # 将弧度转换为角度
        angle_deg = math.degrees(angle_rad)
        # 将角度限制在0到360
        angle_deg_with_y_axis = (angle_deg + 360) % 360
        return angle_deg_with_y_axis

    # 给两个点算直线参数ABC
    @staticmethod
    def calculate_line_coefficients(p1: POINT, p2: POINT) -> (float, float, float):
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        # 处理垂直线，斜率不存在
        if x1 == x2:
            A, B, C = 1, 0, -x1
        else:
            # 计算斜率
            m = (y2 - y1) / (x2 - x1)
            # 计算截距
            b = y1 - m * x1
            # 转换为Ax + By + C = 0的形式
            A, B, C = -m, 1, -b
        return A, B, C

    # 对两点的线段进行线性插值
    @staticmethod
    def calculate_interpolate_point_between_two_points(p1: POINT, p2: POINT, t: float) -> list:
        x = p1[0] + (p2[0] - p1[0]) * t
        y = p1[1] + (p2[1] - p1[1]) * t
        if len(p1) == 2:
            return [x, y]
        else:
            z = p1[2] + (p2[2] - p1[2]) * t
            return [x, y, z]

    # 计算线段长度
    @staticmethod
    def calculate_line_length(line: list) -> float:
        return sum([
            LineBase.calculate_distance_between_two_points(line[i - 1], line[i])
            for i in range(1, len(line))
        ])

    @staticmethod
    # 根据首尾段角度计算转向类型
    def calculate_turn_type(line: list) -> str:
        start_angle = LineBase.calculate_angle_with_y_axis(line[0], line[1])
        end_angle = LineBase.calculate_angle_with_y_axis(line[-2], line[-1])
        # 角度差 -180~180
        angle_diff = (end_angle - start_angle + 180) % 360 - 180

        if -45 < angle_diff < 45:
            turn_type = "直行"
        elif -135 < angle_diff < -45:
            turn_type = "左转"
        elif 45 < angle_diff < 135:
            turn_type = "右转"
        else:
            turn_type = "调头"

        return turn_type

    # 计算两条线段合并后的线段
    @staticmethod
    def calculate_merged_line_from_two_lines(line1: list, line2: list) -> list:
        new_line = []
        for p1, p2 in zip(line1, line2):
            x = (p1[0] + p2[0]) / 2
            y = (p1[1] + p2[1]) / 2
            if len(p1) == 3:
                z = p1[2] + (p2[2] - p1[2]) / 2
                p = [x, y, z]
            else:
                p = [x, y]
            new_line.append(p)
        return new_line

    # 计算两直线交点
    @staticmethod
    def calculate_intersection_point_from_two_lines(first_line_coeff: tuple, second_line_coeff: tuple, point: POINT) -> (float, float):
        A1, B1, C1 = first_line_coeff
        A2, B2, C2 = second_line_coeff
        # 计算分母
        denominator = A1 * B2 - A2 * B1
        # 如果分母接近零，说明直线平行或重合
        if abs(denominator) < 1e-6:
            x, y = point
        else:
            # 计算交点坐标
            x = (B1 * C2 - B2 * C1) / denominator
            y = (A2 * C1 - A1 * C2) / denominator
        return x, y

    # 计算点到直线的垂足点坐标
    @staticmethod
    def calculate_foot_of_perpendicular(line_coeff: tuple, point: POINT) -> POINT:
        A, B, C = line_coeff
        x0, y0 = point[:2]
        denominator = A ** 2 + B ** 2
        x = (B * (B * x0 - A * y0) - A * C) / denominator
        y = (A * (-B * x0 + A * y0) - B * C) / denominator
        if len(point) == 2:
            return [x, y]
        else:
            return [x, y, point[2]]

    # 获取多边形边界点
    @staticmethod
    def calculate_boundary_points(area_boundary_points: list) -> list:
        union_boundary_coords = None
        try:
            # 构建多边形对象列表
            polygon_list = [Polygon(coords) for coords in area_boundary_points]
            # 计算多边形的并集
            union_polygon = polygon_list[0]
            for polygon in polygon_list[1:]:
                union_polygon = union_polygon.union(polygon)
            # 提取边界点
            union_boundary_coords = list(union_polygon.exterior.coords)
        except:
            pass
        return union_boundary_coords
