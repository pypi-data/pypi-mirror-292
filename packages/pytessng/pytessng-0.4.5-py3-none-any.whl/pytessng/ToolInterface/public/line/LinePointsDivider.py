from .LineBase import LineBase


class LinePointsDivider:
    """ 分割路段 """
    # 通过给定的距离列表，将线段分割成若干段
    @staticmethod
    def divide_line_by_distances(line: list, given_distance_list: list) -> (list, list):
        assert len(line) >= 2

        given_distance_list = sorted(given_distance_list)
        assert len(given_distance_list) > 0

        total_length = LineBase.calculate_line_length(line)
        assert given_distance_list[0] > 0 and given_distance_list[-1] < total_length

        all_length = 0
        all_points = [(line[0], False)]
        divide_infos = []
        last_index = -1
        index = 1
        k = 0

        while True:
            if index >= len(line):
                break

            p1, p2 = line[index - 1], line[index]
            dist = given_distance_list[k] if k < len(given_distance_list) else 1e6

            section_length = LineBase.calculate_distance_between_two_points(p1, p2)
            if index != last_index:
                all_length += section_length
                last_index = index

            if all_length < dist:
                if p2 not in [v[0] for v in all_points]:
                    all_points.append((p2, False))
                index += 1
            elif all_length == dist:
                all_points.append([p2, True])
                divide_infos.append([index, None])
                k += 1
            else:
                before_length = all_length - section_length
                ratio = round((dist - before_length) / section_length, 3)
                cut_point = LineBase.calculate_interpolate_point_between_two_points(p1, p2, ratio)
                all_points.append([cut_point, True])
                divide_infos.append([index - 1, ratio])
                k += 1

        divided_points = [[], ]
        for p, flag in all_points:
            divided_points[-1].append(p)
            if flag:
                divided_points.append([p])

        return divided_points, divide_infos

    # 通过给定的索引列表和比例列表，将线段分割成若干段
    @staticmethod
    def divide_line_by_indexes_and_ratios(line: list, divide_infos: list, reference_points: list = None) -> list:
        assert len(line) >= 2
        if reference_points:
            assert len(divide_infos) == len(reference_points)
            # 用垂足
            algorithm = 1
        else:  # 为空或为None
            # 用比例
            algorithm = 2

        all_points = []
        i = 0  # 当前点的索引
        k = 0  # 当前分割点的索引
        while True:
            if k >= len(divide_infos):
                for j in range(i + 1, len(line)):
                    all_points.append((line[j], False))
                break

            index, ratio = divide_infos[k]
            reference_point = reference_points[k] if algorithm == 1 else None

            # 当前点是要看的点
            if index == i:
                # 如果是第一个点就加入
                if i == 0:
                    all_points.append((line[index], False))

                p1 = line[index]
                p2 = line[index + 1]

                # 计算分割点
                if algorithm == 1:
                    # 计算直线系数
                    line_coeff = LineBase.calculate_line_coefficients(p1, p2)
                    # 计算垂足点
                    cut_point = LineBase.calculate_foot_of_perpendicular(line_coeff, reference_point)
                else:
                    # 用比例计算
                    cut_point = LineBase.calculate_interpolate_point_between_two_points(p1, p2, ratio)

                all_points.append((cut_point, True))
                k += 1
            # 下一个点是要看的点
            elif index == i + 1:
                if ratio is None:
                    all_points.append((line[index], True))
                    k += 1
                else:
                    all_points.append((line[i], False))
                    all_points.append((line[i + 1], False))
                i += 1
            # 当前点和下一个点不是要看的点
            else:
                all_points.append((line[i], False))
                i += 1

        # 按照分割点的标记把线段分成多段
        divided_points = [[], ]
        for p, flag in all_points:
            divided_points[-1].append(p)
            if flag:
                divided_points.append([p])

        return divided_points


class LinkPointsDivider:
    @staticmethod
    def divide_link(points: list, lanes_points: list, given_distance_list: list) -> (list, list):
        # 分割的路段点位，分割信息
        divided_points, divide_infos = LinePointsDivider.divide_line_by_distances(points, given_distance_list)

        # 参考点列表
        reference_points: list = [points[-1] for points in divided_points[:-1]]

        # 分割的车道点位
        temp_lanes_points = [
            {
                "left": LinePointsDivider.divide_line_by_indexes_and_ratios(lane_points["left"], divide_infos, reference_points),
                "center": LinePointsDivider.divide_line_by_indexes_and_ratios(lane_points["center"], divide_infos, reference_points),
                "right": LinePointsDivider.divide_line_by_indexes_and_ratios(lane_points["right"], divide_infos, reference_points),
            }
            for lane_points in lanes_points
        ]

        divided_lanes_points = [
            [
                {
                    "left": lane_points["left"][number],
                    "center": lane_points["center"][number],
                    "right": lane_points["right"][number],
                }
                for lane_points in temp_lanes_points
            ]
            for number in range(len(divided_points))
        ]

        return divided_points, divided_lanes_points
