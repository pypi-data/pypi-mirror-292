import unittest
from tire_codes import TireCodeParser, TireSpecs
from tests.sample_codes import sample_codes


class TestTireCodeParser(unittest.TestCase):
    
    expected_spec_keys = [
        'SERVICE_TYPE', 'TIRE_WIDTH', 'ASPECT_RATIO', 
        'WHEEL_DIAMETER', 'OVERALL_DIAMETER', 'LOAD_INDEX', 
        'LOAD_INDEX_DUAL', 'SPEED_RATING'
    ]

    def test_tire_code_parser(self):
        for tire_code in sample_codes:
            with self.subTest(tire_code=tire_code):
                parser = TireCodeParser(tire_code)
                specs = parser.parse()
                self.assertIsInstance(specs, TireSpecs)
                for key in self.expected_spec_keys:
                    self.assertIn(key, specs.__dict__)
                self.assertIsNotNone(specs.WIDTH, f"TIRE_WIDTH is missing or None for {tire_code}")
                self.assertIsNotNone(specs.WHEEL_DIAMETER, f"WHEEL_DIAMETER is missing or None for {tire_code}")


if __name__ == '__main__':
    unittest.main()