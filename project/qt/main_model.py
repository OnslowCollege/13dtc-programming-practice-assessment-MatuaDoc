"""
Café ordering system.

Models.

Created by Matua Doc.
Created on 2023-06-11.
"""

from enum import Enum
from dataclasses import dataclass

from main_utils import format_price


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
