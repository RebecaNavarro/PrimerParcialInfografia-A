import math
import arcade
from dataclasses import dataclass
from logging import getLogger

logger = getLogger(__name__)


@dataclass
class ImpulseVector:
    angle: float
    impulse: float


@dataclass
class Point2D:
    x: float = 0
    y: float = 0


def get_angle_radians(point_a: Point2D, point_b: Point2D) -> float:
    delta_x = point_b.x - point_a.x
    delta_y = point_b.y - point_a.y
    angle = math.atan2(delta_y, delta_x)
    return angle


def get_distance(point_a: Point2D, point_b: Point2D) -> float:
    distance = math.sqrt((point_b.x - point_a.x) ** 2 + (point_b.y - point_a.y) ** 2)
    return distance


def get_impulse_vector(start_point: Point2D, end_point: Point2D, reduction_factor: float = 0.7) -> ImpulseVector:
    angle = get_angle_radians(start_point, end_point)
    distance = get_distance(start_point, end_point)
    reduced_impulse = -distance * reduction_factor
    return ImpulseVector(angle, reduced_impulse)
