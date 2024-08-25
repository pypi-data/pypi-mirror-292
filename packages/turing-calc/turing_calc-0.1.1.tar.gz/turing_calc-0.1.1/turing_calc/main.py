from calculator import Calculator


def main() -> None:
    """
    Displays the instructions and starts the calculator.

    :return: None
    """
    print("+n, -n, *n, /n, rn=n degree root, m=clear memory, q=quit")
    Calculator.running()


if __name__ == "__main__":
    main()
