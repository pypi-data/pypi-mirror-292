# Tire Codes

## Description
Tire codes is a lightweight, easy-to-use Python tool designed to parse various tire specifications from tire codes.

## Features
- Parses tire specifications from various formats.
- Extractable specs include:
  - FORMAT
  - SERVICE_TYPE
  - WIDTH
  - ASPECT_RATIO
  - WHEEL_DIAMETER
  - CONSTRUCTION
  - OVERALL_DIAMETER
  - LOAD_INDEX
  - LOAD_INDEX_DUAL
  - SPEED_RATING

## Installation
Install directly with pip. No external dependencies.

```bash
pip install tire-codes
```

## Example
For a tire code like "215/70R16 100T" (metric) or "35X12.5R20 125S" (off-road), the parser will automatically detect the format and extract the details into a `TireSpecs` object.

## Usage
To parse a tire code, pass your tire code string to the `TireCodeParser` object:

```python
from tire_codes import TireCodeParser, TireCodeParsingError, TireCodeValidationError

try:
    parser = TireCodeParser("295/40R21 111Y")
    specs = parser.parse()
    print(specs)
except TireCodeParsingError as e:
    print(f"Parsing error: {e}")
except TireCodeValidationError as e:
    print(f"Validation error: {e}")
```

You can also access all spec values as a dictionary:

```python
print(specs.to_dict())
```

### Command-Line Interface

You can also run the parser from the command line:

```bash
python3 main.py "295/40R21 111Y"
```

## Contributing
Any suggestions or contributions are welcome! I hope you find this package useful.

## License
MIT License
