from typing import TYPE_CHECKING
from tire_codes.enums import TireCodeFormat
from tire_codes.exc import TireSpecValidationError


if TYPE_CHECKING:
    from tire_codes.tire_specs import TireSpecs


class TireSpecValidator:
    """Validates and ensures the correctness of attributes within a TireSpecs object.

    This class is responsible for converting string values to their appropriate types
    (e.g., integers, floats) and validating that these values fall within ranges that
    are, in my totally unscientific but reasonable hunch, likely to cover 99.99% 
    of real-world tire specifications.
    """
    def __init__(self, tire_specs:"TireSpecs"):
        self.tire_specs = tire_specs

    def validate(self):

        self.tire_specs.WIDTH = self.validate_width()
        self.tire_specs.ASPECT_RATIO = self.validate_aspect_ratio()
        self.tire_specs.CONSTRUCTION = self.validate_construction()
        self.tire_specs.OVERALL_DIAMETER = self.validate_overall_diameter()
        self.tire_specs.WHEEL_DIAMETER = self.validate_wheel_diameter()
        self.tire_specs.LOAD_INDEX = self.validate_load_index()
        self.tire_specs.LOAD_INDEX_DUAL = self.validate_load_index(dual=True)
        self.tire_specs.SPEED_RATING = self.validate_speed_rating()
        self.tire_specs.SERVICE_TYPE = self.validate_service_type()

    def validate_service_type(self) -> str | None:
        service_type = self.tire_specs.SERVICE_TYPE
        if not service_type:
            return
        if len(service_type) <= 3:
            return service_type
        raise TireSpecValidationError('SERVICE_TYPE', self.tire_specs.SERVICE_TYPE, self.tire_specs.TIRE_CODE)

    def validate_speed_rating(self) -> str | None:
        speed_rating = self.tire_specs.SPEED_RATING
        if not speed_rating:
            return
        if len(speed_rating) <= 2:
            return speed_rating
        raise TireSpecValidationError('SPEED_RATING', self.tire_specs.SPEED_RATING, self.tire_specs.TIRE_CODE)

    def validate_load_index(self, dual:bool=False) -> int | None:

        if dual:
            value = self.tire_specs.LOAD_INDEX_DUAL
            field = 'LOAD_INDEX_DUAL'
        else:
            value = self.tire_specs.LOAD_INDEX
            field = 'LOAD_INDEX'
        if not value:
            return
        try:
            load_index = int(value)
        except ValueError:
            raise TireSpecValidationError(field, value, self.tire_specs.TIRE_CODE)

        if 40 < load_index < 300:
            return value

        raise TireSpecValidationError(field, value, self.tire_specs.TIRE_CODE)

    def validate_wheel_diameter(self) -> int:
        field = 'WHEEL_DIAMETER'
        value = self.tire_specs.WHEEL_DIAMETER
        try:
            wheel_diameter = int(value)
        except ValueError:
            raise TireSpecValidationError(field, value, self.tire_specs.TIRE_CODE)
        if 10 < wheel_diameter < 100:
            return wheel_diameter
        raise TireSpecValidationError(field, value, self.tire_specs.TIRE_CODE)

    def validate_overall_diameter(self) -> float | None:
        if self.tire_specs.FORMAT == TireCodeFormat.METRIC:
            return None
        
        field = 'OVERALL_DIAMETER'
        value = self.tire_specs.OVERALL_DIAMETER
        try:
            overall_diameter = float(value)
        except ValueError:
            TireSpecValidationError(field, value, self.tire_specs.TIRE_CODE)
        if 10 < overall_diameter < 100:
            return overall_diameter
        raise TireSpecValidationError(field, value, self.tire_specs.TIRE_CODE)

    def validate_construction(self) -> str:

        if len(self.tire_specs.CONSTRUCTION) <= 4:
            return self.tire_specs.CONSTRUCTION
        raise TireSpecValidationError('CONSTRUCTION', self.tire_specs.CONSTRUCTION, self.tire_specs.TIRE_CODE)

    def validate_aspect_ratio(self) -> int | None:
        
        if self.tire_specs.FORMAT == TireCodeFormat.OFF_ROAD:
            return
        
        field = 'ASPECT_RATIO'
        value = self.tire_specs.ASPECT_RATIO
        try:
            aspect_ratio = int(value)
        except ValueError:
            TireSpecValidationError(field, value, self.tire_specs.TIRE_CODE)
        if 10 < aspect_ratio < 130:
            return aspect_ratio
        
        raise TireSpecValidationError(field, value, self.tire_specs.TIRE_CODE) 

    def validate_width(self) -> float:
        field = 'WIDTH'
        value = self.tire_specs.WIDTH
        try:
            width = float(value)
        except ValueError:
            TireSpecValidationError(field, value, self.tire_specs.TIRE_CODE)
        match self.tire_specs.FORMAT:
            case TireCodeFormat.METRIC:
                if 80 < width < 500:
                    return width 
            case TireCodeFormat.OFF_ROAD:
                if 3 < width < 50:
                    return width
        raise TireSpecValidationError(field, value, self.tire_specs.TIRE_CODE)
