"""
Café ordering system.

Useful functions.

Created by Matua Doc.
Created on 2023-06-11.
"""


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
