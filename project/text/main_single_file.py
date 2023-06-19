"""
Café ordering system.

Single file version — text-based.

Created by Matua Doc.
Created on 2023-06-11.
"""


from enum import Enum
from dataclasses import dataclass


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


class MenuCategory(Enum):
    """Menu category constants."""

    # Food categories.
    FOOD = 0
    RICE = 1
    DRINKS = 2

    def __str__(self) -> str:
        """Return the name of the category in human-readable form."""
        match self:
            case MenuCategory.FOOD: return "Food"
            case MenuCategory.RICE: return "Rice meals"
            case MenuCategory.DRINKS: return "Drinks"


@dataclass
class MenuItem:
    """An item on the menu."""

    _name: str
    _price: float
    _category: MenuCategory

    @property
    def name(self) -> str:
        """The name of the item."""
        return self._name

    @property
    def price(self) -> float:
        """The price of the item as a number."""
        return self._price

    @property
    def price_text(self) -> str:
        """The price of the item as text."""
        return format_price(self.price, "$")

    @property
    def category(self) -> MenuCategory:
        """The category of the item."""
        return self._category


@dataclass
class Menu:
    """All items on the menu, including stock."""

    _items: list[MenuItem]

    def __post_init__(self) -> None:
        """Create a stock dictionary based on the items passed in."""
        self._stock: dict[str, int] = {}
        for item in self._items:
            self._stock[item.name] = 20

    def item_named(self, name: str) -> MenuItem:
        """
        Return the item matching a given name.

        This is taken from _items rather than _stock, so as to fetch the price
        and category data.

        Raises an exception if no such item is found.
        """
        # Search the list of items for one with a corresponding name.
        for item in self._items:
            if item.name == name:
                return item

        # If no item was found, raise an exception.
        raise NameError(f"No such item '{name}'")

    def items_in_category(self, category: MenuCategory) -> list[MenuItem]:
        """All items in a given category."""
        items = []

        # Search the list of items for any with a matching category,
        # then add it to the items list.
        for item in self._items:
            if item.category == category:
                items.append(item)

        return items

    def stock_for_item(self, item: MenuItem) -> int:
        """Return the amount in stock for a given item."""
        return self._stock[item.name]

    def sell_item(self, item: MenuItem, count: int) -> None:
        """Sell the given number of items."""
        stock_count = self._stock[item.name]
        self._stock[item.name] = stock_count - count


class Order:
    """A customer's order."""

    # Constants.
    MAX_ITEM_COUNT = 2

    def __init__(self, menu: Menu) -> None:
        """Create the order."""
        self._menu = menu
        self._items: dict[str, int] = {}

    def __str__(self) -> str:
        """Pretty-printed version of the current order."""
        text = ""

        # Add the items to each line.
        for item in self._items.keys():
            count = self._items[item]
            text = text + f"{count}x {item}\n"

        # Show the order total price.
        text = text + "\n" + "TOTAL: " + format_price(self.order_total, "$")

        return text

    @property
    def items(self) -> dict[str, int]:
        """The items in the order."""
        return self._items

    @property
    def order_total(self) -> float:
        """The cost of the order so far."""
        running_total = 0.0

        # Loop over every item in the list to find the corresponding price of
        # the item in the menu, then multiply the purchase amount by that
        # price to find the cost.
        for item_name in self._items.keys():
            item = self._menu.item_named(item_name)
            count = self._items[item_name]
            running_total = running_total + (item.price * count)

        return running_total

    def add_item(self, item: MenuItem) -> None:
        """
        Add a given number of an item to the order.

        Raises an exception if no more items can be added.
        """
        # Check if the item is in stock. If not, raise an exception.
        if self._menu.stock_for_item(item) == 0:
            raise RuntimeError(f"No stock for {item.name}")

        # Otherwise, if the item is in stock…
        if item.name in self._items.keys():
            # The item already exists.
            count = self._items[item.name]

            if count == self.MAX_ITEM_COUNT:
                # There are already the maximum allowed number of this item.
                raise RuntimeError(f"Cannot order more than \
{self.MAX_ITEM_COUNT} of {item.name}")
            else:
                self._items[item.name] = count + 1
        else:
            # The item was not already in the order. Add it now.
            self._items[item.name] = 1

    def remove_item(self, item: MenuItem) -> None:
        """
        Remove 1 of an item from the order.

        Raises an exception if the item is not in the order.
        """
        # Raise an exception if no such item exists.
        if item.name not in self._items.keys():
            raise RuntimeError(f"No such item {item.name} in order.")
        else:
            count = self._items[item.name]
            if count > 1:
                # If there are more than 1 of the item, reduce by 1.
                self._items[item.name] = count - 1
            else:
                # If there's only one, delete the key altogether.
                del self._items[item.name]


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
