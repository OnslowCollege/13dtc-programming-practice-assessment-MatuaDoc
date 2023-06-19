"""
Café ordering system.

Useful functions.

Created by Matua Doc.
Created on 2023-06-11.
"""


def get_valid_input(prompt: str) -> str:
    """Continually ask for user input until a valid string is given."""
    user_input: str | None = None

    # Loop until user_input is non-empty.
    while not user_input:
        user_input = input(prompt)

    return user_input


def get_valid_int(prompt: str, min: int, max: int) -> int:
    """Continually ask for user input until a valid int is given."""
    user_int: int | None = None

    # Loop until user_int is a valid number.
    while not user_int:
        try:
            user_int = int(get_valid_input(prompt))

            # Reset user_int to None if the number is out of bounds.
            if user_int < min or user_int > max:
                user_int = None
        except ValueError:
            print("Please enter a valid number.")

    return user_int


def get_valid_bool(prompt: str) -> bool:
    """Continually ask for user input until a valid yes/no choice is given."""
    user_bool: bool | None = None

    # Loop until user_bool is a valid bool.
    while user_bool is None:
        user_text = get_valid_input(prompt).lower()
        match user_text:
            # If the user enters y/n, set the relevant bool value.
            case "y": user_bool = True
            case "n": user_bool = False

            # Reset the bool because an invalid choice has been made.
            case _: user_bool = None

    return user_bool


def format_price(price: float, symbol: str, prefix: bool = True) -> str:
    """
    Format a price float as text.

    The result has a currency symbol and 2 decimal places.

    Parameters:
    - price (float): the price to format.
    - symbol (str): the symbol to use in the result.
    - prefix (bool): whether the symbol goes at the front (True)/end (False).

    Returns a formatted string containing the price.
    """
    return f"{symbol if prefix else ''}{price:.2f}\
{symbol if not prefix else ''}"
