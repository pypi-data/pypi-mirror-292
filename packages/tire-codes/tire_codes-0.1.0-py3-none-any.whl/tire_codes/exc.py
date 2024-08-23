from typing import Any


class TireCodeParsingError(Exception):
    """Raised when the tire code can not be successfully parsed."""
    def __init__(self, field_name:str, tire_code:str):
        message = f"Could not parse {field_name} for tire code `{tire_code}`"
        super().__init__(message)


class TireSpecValidationError(Exception):
    """Raised when TireSpecValidator fails to validate a particular field of TireSpecs object.
    This is due to the value parsed being of an incorrect type or outside an acceptable range
    as defined in validation.py
    """
    def __init__(self, field_name:str, value: Any, tire_code:str):
        message = f"Could not validate `{field_name}`: `{value}` for tire code `{tire_code}`"
        super().__init__(message)