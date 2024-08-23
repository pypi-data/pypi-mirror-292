import argparse
from tire_codes import TireCodeParser, TireSpecValidationError, TireCodeParsingError


def main():
    arg_parser = argparse.ArgumentParser(
        description="Parse a tire code and validate its components.")
    arg_parser.add_argument("tire_code", type=str,
                        help="The tire code to be parsed and validated (e.g., '295/40R21 111Y').")
    args = arg_parser.parse_args()
    tire_code = args.tire_code
    try:
        parser = TireCodeParser(tire_code)
        specs = parser.parse().to_dict()
        specs['FORMAT'] = specs['FORMAT'].value.title()
        print(specs)
    except TireCodeParsingError:
        print(f"Parsing failed: {e}")
    except TireSpecValidationError as e:
        print(f"Validation failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()