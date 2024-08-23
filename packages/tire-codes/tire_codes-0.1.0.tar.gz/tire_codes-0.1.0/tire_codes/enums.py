from enum import Enum


class TireCodeFormat(Enum):
    METRIC = 'metric'
    OFF_ROAD = 'off-road'


class TireSpecsEnum(Enum):
    FORMAT = "FORMAT"
    SERVICE_TYPE = "SERVICE_TYPE"
    WIDTH = "WIDTH"
    ASPECT_RATIO = "ASPECT_RATIO"
    WHEEL_DIAMETER = "WHEEL_DIAMETER"
    CONSTRUCTION = "CONSTRUCTION"
    LOAD_INDEX = "LOAD_INDEX"
    LOAD_INDEX_DUAL = "LOAD_INDEX_DUAL"
    SPEED_RATING = "SPEED_RATING"