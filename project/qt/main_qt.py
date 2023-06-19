"""
Café ordering system.

Qt-based version.

Created by Matua Doc.
Created on 2023-06-11.
"""

import json
from main_controller_qt import CafeProgram
from main_model import Menu, MenuCategory, MenuItem, Order
from PySide6.QtWidgets import *
from typing import Callable


def read_menu() -> Menu:
    """
    Load the menu from a JSON file.

    Return the dictionary if it can be parsed, or None otherwise.
    """
    menu_json: dict[str, dict[str, str]] = {}

    # Try safely opening the menu.json file.
    try:
        with open("menu.json") as menu_file:
            menu_json = json.load(menu_file)
    except FileNotFoundError:
        print("No such file. Closing program.")
    except json.decoder.JSONDecodeError:
        print("Unable to parse JSON.")

    menu_items: list[MenuItem] = []

    # Create objects from the dictionary.
    for item_name in menu_json.keys():
        # Convert the price.
        price_text = menu_json[item_name]["price"]
        price = float(price_text)

        # Convert the category.
        category_text = menu_json[item_name]["category"]
        category_number = int(category_text)
        category = MenuCategory(category_number)

        # Add the item to the list.
        item = MenuItem(item_name, price, category)
        menu_items.append(item)

    return Menu(menu_items)


if __name__ == "__main__":
    menu = read_menu()

    order = Order(menu)

    app = QApplication()
    program = CafeProgram(menu, order)
    app.exec()
