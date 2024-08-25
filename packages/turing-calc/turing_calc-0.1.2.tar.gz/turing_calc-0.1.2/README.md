# Calculator Project

Calculator module that accepts arithmetic operations as user input and stores resulting value in memory.

## Structure

```
.
├── tests/
│   ├── __init__.py
│   └── test_calculator.py
├── turing_calc/
│   ├── __init__.py
│   ├── calculator.py
│   └── main.py
├── README.md
└── pyproject.toml

```

## Features

- Basic arithmetic operations: addition, subtraction, multiplication, division, and nth root.
- Memory management: store and use results from previous calculations and reset to 0.
- Format validation: ensures that the inputs are properly formatted.

## Installation

### Poetry

To install with poetry use `poetry add turing-calculator`

### pip

To install with pip use `pip install turing-calculator`

## Usage

python

```
from calculator import Calculator

calc = Calculator()
print(calc.add(10))         # Outputs: 10.0
print(calc.sub(2))          # Outputs: 8
print(calc.mul(4))          # Outputs: 32.0
print(calc.div(2))          # Outputs: 16.0
print(calc.root(4))         # Outputs: 2.0
calc.clear()                # Resets memory to 0.0
calc.quit()                 # Exits module
```

## Testing

Tests are located in the `tests/` directory and can be run using `pytest`.


## Contributing

1. Fork the repository.
2. Create a new branch for your features or fixes.
3. Write tests that cover your changes.
4. Submit a pull request and provide a detailed description of your changes.

## License

This project is licensed under the terms of the [LICENSE](./LICENSE) file.
