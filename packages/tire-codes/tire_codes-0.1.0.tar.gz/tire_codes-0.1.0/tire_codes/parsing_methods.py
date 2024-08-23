from tire_codes.exc import TireCodeParsingError
from tire_codes.regex import TireCodeRegex


class BaseParsingMethods:

    def __init__(self, tire_code: str):
        self.tire_code = tire_code
        self.regex = TireCodeRegex

    @property
    def tire_code_no_spaces(self) -> str:
        return ''.join([char for char in self.tire_code.split() if char != ' '])

    @property
    def tire_code_remove_leading_alpha(self) -> str:
        if self.tire_code[0].isalpha():
            for i, char in enumerate(self.tire_code):
                if not char.isalpha():
                    return self.tire_code[i:]
        return self.tire_code

    @staticmethod
    def extract_alpha(s: str, reverse: bool = False) -> str:
        """Extracts a contiguous sequence of alphabetic characters from the start of a string."""
        if reverse:
            s = s[::-1]
        alpha_str = ''
        for char in s:
            if char.isalpha():
                alpha_str += char
            else:
                break
        return alpha_str[::-1] if reverse else alpha_str

    @staticmethod
    def extract_digits(s: str, reverse: bool = False) -> str:
        """Extracts a contiguous sequence of digits from the start of a string."""
        if reverse:
            s = s[::-1]
        digit_str = ''
        for char in s:
            if char.isdigit():
                digit_str += char
            else:
                break
        return digit_str[::-1] if reverse else digit_str

    @staticmethod
    def slice_after_substring(s: str, substring: str) -> str:
        """Returns the portion of the string after a given substring."""
        return s[s.find(substring) + len(substring):]

    def speed_rating(self) -> str | None:
        s = self.tire_code.replace('REINF', '').strip()
        speed_rating = self.extract_alpha(s, reverse=True)
        return speed_rating if speed_rating else None

    def load_index(self) -> str | None:
        split_string = self.tire_code.split(' ')[-1].strip()
        load_index = self.extract_digits(s=split_string)
        return load_index if load_index else None

    def load_index_dual(self) -> str | None:
        load_index_dual = None
        split_string = self.tire_code.split(' ')[-1]
        dual_string = split_string.split('/')[-1]
        if split_string != dual_string:
            load_index_dual = self.extract_digits(dual_string)
        return load_index_dual


class MetricParser(BaseParsingMethods):

    def _service_type_start(self) -> str | None:
        """Checks if the service type is at the start of the string"""
        service_type = None
        if self.tire_code != self.tire_code_remove_leading_alpha:
            service_type = self.extract_alpha(self.tire_code)

        return service_type

    def service_type(self, construction: str, wheel_diameter: str) -> str | None:

        service_type = self._service_type_start()
        if not service_type:
            substring = construction + wheel_diameter
            tire_code_slice = self.slice_after_substring(
                s=self.tire_code, substring=substring)
            service_type = self.extract_alpha(tire_code_slice)

        return service_type

    def construction(self) -> str:
        match = self.regex.metric_construction.search(self.tire_code)
        if match:
            return match.group(0)
        else:
            raise TireCodeParsingError("construction type", self.tire_code)

    def wheel_diameter(self, construction: str) -> str:

        sliced_tire_code = self.slice_after_substring(
            s=self.tire_code_remove_leading_alpha, substring=construction)
        wheel_diameter = self.extract_digits(sliced_tire_code)
        if not wheel_diameter:
            raise TireCodeParsingError("wheel diameter", self.tire_code)
        return wheel_diameter

    def width_and_aspect_ratio(self) -> tuple[str, str | None]:
        match = self.regex.metric_width_aspect_ratio.search(
            self.tire_code_no_spaces)
        if match:
            try:
                return match.group(1), match.group(2)
            except (IndexError):
                pass
        raise TireCodeParsingError("width and/or aspect ratio", self.tire_code)


class OffRoadParser(BaseParsingMethods):

    def overall_diamater_and_width(self) -> tuple[str, str]:
        overall_diameter_and_width_string = ''
        if self.tire_code[0].isdigit():
            for char in self.tire_code:
                if char.isdigit() or char == '.' or char == 'X':
                    overall_diameter_and_width_string += char
                else:
                    break
            overall_diameter_and_width_list = overall_diameter_and_width_string.split(
                'X')
            if len(overall_diameter_and_width_list) != 2:
                raise TireCodeParsingError(
                    "overall diameter and/or width", self.tire_code)

        return tuple(overall_diameter_and_width_list)

    def wheel_diameter(self, diameter_width_string: str, construction: str) -> str:
        """Param diameter_width_string will be in the format of '37x13.5'"""
        substring = diameter_width_string+construction
        sliced_tire_code = self.slice_after_substring(
            self.tire_code, substring)
        wheel_diameter = self.extract_digits(sliced_tire_code)
        if not wheel_diameter:
            raise TireCodeParsingError("wheel diameter", self.tire_code)
        return wheel_diameter

    def construction(self, diameter_width_string: str) -> str:

        sliced_tire_code = self.slice_after_substring(
            s=self.tire_code, substring=diameter_width_string)
        construction = self.extract_alpha(s=sliced_tire_code)
        if not construction:
            raise TireCodeParsingError("construction type", self.tire_code)

        return construction

    def service_type(self) -> str | None:
        service_type = ''
        for char in self.tire_code.split(' ')[0][::-1]:
            if char.isalpha():
                service_type += char
            else:
                break
        if service_type:
            return ''.join([char for char in service_type[::-1]])
