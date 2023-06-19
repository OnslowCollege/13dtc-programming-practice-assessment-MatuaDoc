"""
Café ordering system.

Text-based version.

Created by Matua Doc.
Created on 2023-06-11.
"""

from main_model import Menu, MenuCategory, MenuItem, Order
from main_controller_text import CafeProgram


def read_menu() -> Menu:
    """
    Load the menu from a text file.

    Return the dictionary if it can be parsed, or None otherwise.
    """
    menu_text: list[str] = []

    # Try safely opening the menu.txt file.
    try:
        with open("menu.txt") as menu_file:
            menu_text = menu_file.readlines()
    except FileNotFoundError:
        print("No such file. Closing program.")

    menu_items: list[MenuItem] = []

    # Create objects from the dictionary.
    for line in menu_text:
        components = line.split(",")

        # Convert the name.
        item_name = components[0]

        # Convert the price.
        price_text = components[1]
        price = float(price_text)

        # Convert the category.
        category_text = components[2]
        category_number = int(category_text)
        category = MenuCategory(category_number)

        # Add the item to the list.
        item = MenuItem(item_name, price, category)
        menu_items.append(item)

    return Menu(menu_items)


if __name__ == "__main__":
    menu = read_menu()
    order = Order(menu)

    program = CafeProgram(menu, order)
    program.run()
