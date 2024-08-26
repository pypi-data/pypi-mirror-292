from typing import Union

from .linkCreator.LinkCreator import LinkCreator
from .linkLocator.LinkLocator import LinkLocator
from .linkSplitter.LinkSplitter import LinkSplitter
from .linkRemover.LinkRemover import LinkRemover
from .linkReverser.LinkReverser import LinkReverser
from .linkMerger.LinkMerger import LinkMerger
from .linkSimplifier.LinkSimplifier import LinkSimplifier
from .connectorLengthLimiter.ConnectorLengthLimiter import ConnectorLengthLimiter
from .linkLengthLimiter.LinkLengthLimiter import LinkLengthLimiter
from .linkRecalculater.LinkRecalculater import LinkRecalculater
from .linkLimitSpeedModifier.LinkLimitSpeedModifier import LinkLimitSpeedModifier
from .networkMover.NetworkMover import NetworkMover
from .networkRotater.NetworkRotater import NetworkRotater


class LinkEditorFactory:
    mode_mapping = {
        "create": LinkCreator,  # lane_count: int, lane_width: float, lane_points: str
        "locate": LinkLocator,  # pos: QPointF
        "remove": LinkRemover,  # p1: QPointF, p2: QPointF
        "split": LinkSplitter,  # link_id: int, pos: QPointF, min_connector_length: float = xxx
        "reverse": LinkReverser,  # p1: QPointF, p2: QPointF
        "merge": LinkMerger,  # include_connector: bool = xxx, simplify_points: bool = xxx
        "simplify": LinkSimplifier,  # max_distance: float = xxx, max_length: float = xxx
        "limit_c": ConnectorLengthLimiter,  # min_connector_length: float = xxx
        "limit_l": LinkLengthLimiter,  # max_length_length: float = xxx, min_connector_length: float = xxx
        "recalculate": LinkRecalculater,  # mode: int
        "modify": LinkLimitSpeedModifier,  # limit_speed: float
        "move": NetworkMover,  # move_to_center: bool, x_move: float, y_move: float
        "rotate": NetworkRotater,  # angle: float
    }

    @classmethod
    def build(cls, mode: str, netiface, params: dict) -> Union[None, list, int]:  # 当为int时只会是0
        if mode in cls.mode_mapping:
            model = cls.mode_mapping[mode](netiface)
            return model.edit(**params)
        else:
            raise Exception("No This Link Edit Mode!")
