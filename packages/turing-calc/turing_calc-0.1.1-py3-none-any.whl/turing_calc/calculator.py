import math
import sys
import re


class Calculator:
    """
    Calculator class that performs  arithmetic operations and clearing memory.
    """

    def __init__(self) -> None:
        """
        Initializes the Calculator with 0.00 in memory and a dictionary for
        mapping operations to their corresponding methods.
        """
        self.number: float = 0.00
        self.operations: dict = {
            "+": self.add, "-": self.sub, "*": self.mul, "/": self.div,
            "r": self.root, "m": self.clear, "q": self.quit
        }

    def __str__(self) -> str:
        """
        Returns a string representation of the current number in memory.

        :return: A string representing the current number.
        """
        return f"{self.number}"

    def validate_input(self, user_input: str) -> bool:
        """
        Validates the user input against the expected operation format.

        :param user_input: The input string from the user.
        :return: A boolean value whether the input was formatted correctly.
        """
        return re.match(r"^\s*(m|q|[+\-*/r]\s*-?\d*\.?\d+)\s*$", user_input, re.IGNORECASE)

    def add(self, n: float) -> float:
        """
        Adds the given number to the current number.

        :param n: The number to add.
        :return: The result of the addition.
        """
        return self.number + n

    def sub(self, n: float) -> float:
        """
        Subtracts the given number from the current number.

        :param n: The number to subtract.
        :return: The result of the subtraction.
        """
        return self.number - n

    def mul(self, n: float) -> float:
        """
        Multiplies the current number by the given number.

        :param n: The number to multiply by.
        :return: The result of the multiplication.
        """
        return self.number * n

    def div(self, n: float) -> float:
        """
        Divides the current number by the given number.

        :param n: The number to divide by.
        :return: The result of the division.
        """
        return self.number / n

    def root(self, n: float) -> float:
        """
        Calculates the nth root of the current number.

        :param n: The degree of the root.
        :return: The result of the root calculation.
        """
        return math.pow(self.number, 1.0 / n)

    def clear(self) -> float:
        """
        Clears the calculator's current memory, setting the number to 0.0.

        :return: The cleared value (0.0).
        """
        return 0.0

    def quit(self) -> None:
        """
        Exits the program.

        :return: None
        """
        sys.exit("Exiting...")

    @staticmethod
    def running() -> None:
        """
        Runs the calculator in a loop, accepting user input for operations
        and processing them until 'quit' command entered by the user
        terminates the loop.

        :return: None
        """
        calc = Calculator()

        while True:
            user_input = input(f"Operation: {calc} ").strip()
            if not calc.validate_input(user_input):
                print("Invalid operation. Try again.")
                continue
            else:
                operation, value = user_input[0], user_input[1:]

            if operation in ['+', '-', '*', '/', 'r']:
                try:
                    calc.number = calc.operations[operation](float(value))
                except (ValueError, ZeroDivisionError):
                    print("Invalid operation. Try again.")
            elif operation == 'q':
                calc.quit()
            elif operation == 'm':
                calc.number = calc.clear()
                continue
