"""
Café ordering system.

Controller/presenter for text version.

Created by Matua Doc.
Created on 2023-06-11.
"""

from dataclasses import dataclass

from main_utils import format_price
from main_utils import get_valid_bool, get_valid_input, get_valid_int
from main_model import Menu, MenuCategory, MenuItem, Order


@dataclass
class CafeProgram:
    """The program to run."""

    _menu: Menu
    _order: Order
    _is_running: bool = True

    def run(self) -> None:
        """Run the program."""
        print("Welcome to OC Café.")
        print("-------------------")
        print()

        while self._is_running:
            # Ask for a category.
            category = self.ask_for_category()
            print()

            # Show items in the category.
            item = self.ask_for_item(category)
            print()

            # Ask if the user is adding or removing.
            print("""1. Add to order
2. Remove from order
3. Cancel""")
            task_choice = get_valid_int("Enter a choice: ", 1, 3)
            match task_choice:
                case 1:
                    # Adding to order.
                    try:
                        self._order.add_item(item)
                    except RuntimeError as error:
                        print(error)
                case 2:
                    # Removing from order.
                    try:
                        self._order.remove_item(item)
                    except RuntimeError as error:
                        print(error)
            print()

            # Show the current order.
            print("Current order:")
            print(self._order)
            print("\n" * 5)

            # Check if the user will finish their current order.
            prompt = "Press 'y' to purchase order, or 'n' to continue: "
            if get_valid_bool(prompt):
                self.finalise_order()
            print()

    def print_menu_choices(self, category: MenuCategory | None = None) -> None:
        """
        Print the menu choices for a given category.

        If no category is given, print the list of categories instead.
        """
        if category is None:
            # Category is None, so  print the list of categories.
            for i, _ in enumerate(MenuCategory):
                print(f"{i + 1}. {MenuCategory(i)}")
        else:
            # Print items in the specified category.
            for i, item in enumerate(self._menu.items_in_category(category)):
                index = str(f"{i + 1}. ")
                stock = str(f"{self._menu.stock_for_item(item)}x")

                # Spaces from name to stock.
                stock_spaces = " " * (50 - len(index) - len(item.name))
                first_half = f"{index}{item.name}{stock_spaces}"

                # Spaces from stock to price.
                price_spaces = " " * (10 - len(stock) - len(item.price_text))
                second_half = f"{stock}{price_spaces}{item.price_text}"

                print(first_half + second_half)

    def ask_for_category(self) -> MenuCategory:
        """Ask the user for the menu category."""
        # Show the choices.
        self.print_menu_choices()

        # Ask the user for their choice.
        count = len(MenuCategory)
        category_choice = get_valid_int("Enter a category: ", 1, count)

        # Determine the category by the user's choice.
        category = MenuCategory(category_choice - 1)

        return category

    def ask_for_item(self, category: MenuCategory) -> MenuItem:
        """Ask the user for the choice of item."""
        # Show the choices, then get the items in the category.
        self.print_menu_choices(category)
        items = self._menu.items_in_category(category)

        # Ask the user for their choice.
        item_choice = get_valid_int("Enter a choice: ", 1, len(items))
        item = items[item_choice - 1]

        return item

    def finalise_order(self) -> None:
        """Ask for the user's name, save the order, then clear the order."""
        # Ask for the user's details.
        first_name = get_valid_input("Enter first name: ")
        last_name = get_valid_input("Enter last name: ")

        # Remove the items from stock.
        for item_name in self._order.items.keys():
            count = self._order.items[item_name]
            item = self._menu.item_named(item_name)
            self._menu.sell_item(item, count)
        print()

        # Reset the order for the next customer.
        print(f"Your order has been placed {first_name} {last_name}.")
        print(f"Please pay \
{format_price(self._order.order_total, '$')} at lunch time.")
        self._order = Order(self._menu)

        # Ask if the user should exit.
        if get_valid_bool("Press 'y' to exit, or 'n' to continue: "):
            self._is_running = False
