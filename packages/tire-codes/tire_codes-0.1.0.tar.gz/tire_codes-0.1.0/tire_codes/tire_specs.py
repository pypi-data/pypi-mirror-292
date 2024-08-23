from dataclasses import dataclass, asdict
from tire_codes.enums import TireCodeFormat
from tire_codes.exc import TireSpecValidationError
from tire_codes.validation import TireSpecValidator

@dataclass
class TireSpecs:
    FORMAT: TireCodeFormat
    TIRE_CODE: str
    SERVICE_TYPE: str | None
    WIDTH: int
    ASPECT_RATIO: int | None
    WHEEL_DIAMETER: int
    CONSTRUCTION: str | None
    OVERALL_DIAMETER: float | None
    LOAD_INDEX: int | None
    LOAD_INDEX_DUAL: int | None
    SPEED_RATING: str | None

    def __post_init__(self):
        validator = TireSpecValidator(self)
        try:
            validator.validate()
        except TireSpecValidationError:
            raise

    def to_dict(self) -> dict:
        """
        Returns the tire specifications as a dictionary.

        This method provides a dictionary representation of the specs, 
        which may be preferred over accessing them through a separate class.
        """
        return asdict(self)