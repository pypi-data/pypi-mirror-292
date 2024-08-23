import re


class TireCodeRegex:
    format_metric = re.compile(r'^[A-Za-z]*\d+\/')
    format_off_road = re.compile(r'\d+\s*X')
    metric_width_aspect_ratio = re.compile(r'(\d+)/(\d+)')
    metric_construction = re.compile(r'(?<=\d)[A-Za-z]+(?=\d)')

