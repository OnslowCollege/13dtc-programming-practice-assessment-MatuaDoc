"""
Café ordering system.

Single file version for Tkinter.

Created by Matua Doc.
Created on 2023-06-11.
"""


from dataclasses import dataclass
from enum import Enum
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Callable


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


class CafeWindow(tk.Tk):
    """Main window for the café ordering system."""

    def __init__(self) -> None:
        """Create the window layout."""
        super().__init__()

        # Add section for menu items.
        self.menu_widget = tk.Frame(self)
        self.menu_widget.pack()

        self.order_label = tk.Label(self, text="")
        self.order_label.pack()

        # Add finalise order button.
        self.finalise_order_button = tk.Button(self, text="Finalise order")
        self.finalise_order_button.pack(side=tk.BOTTOM)

        # Detect the screen size and centre.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 640
        window_height = 400
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")


class Row:
    """A row of widgets."""

    def __init__(self,
                 category: MenuCategory,
                 items: list[MenuItem],
                 frame: tk.Frame,
                 add_method: Callable[[MenuCategory], None],
                 remove_method: Callable[[MenuCategory], None]) -> None:
        """Connect the signal function for the buttons."""
        self.category = category
        self.frame = frame

        # Create widgets.
        self.combo_box = ttk.Combobox(
            self.frame,
            values=[f"{item.name} ({format_price(item.price, '$')})"
                    for item
                    in items])
        self.combo_box.current(0)

        # Set up buttons.
        self.add_button = tk.Button(
            self.frame, text="+", command=lambda: add_method(self.category))
        self.remove_button = tk.Button(
            self.frame, text="-", command=lambda: remove_method(self.category))

        # Pack widgets.
        self.combo_box.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.add_button.pack(side=tk.LEFT)
        self.remove_button.pack(side=tk.LEFT)
        self.frame.pack(side=tk.TOP)


class CafeProgram:
    """The program to run."""

    def __init__(self, menu: Menu, order: Order) -> None:
        """Create the controller/presenter for the UI version."""
        self.menu = menu
        self.order = order

        # Add the view.
        self.view = CafeWindow()

        # Keep track of the per-category widgets.
        self.rows = []

        # Add items for each category.
        for category in MenuCategory:
            # Add a frame for the category.
            frame = tk.Frame(self.view.menu_widget)

            # Add the category's label.
            category_label = tk.Label(
                frame, text=str(category), width=10, anchor="w")
            category_label.pack(side=tk.LEFT)

            # Add the items to a combo box.
            items = self.menu.items_in_category(category)

            self.rows.append(Row(category,
                                 items,
                                 frame,
                                 self.add_item_from_combobox,
                                 self.remove_item_from_combobox))

        # Bind the finalise button.
        self.view.finalise_order_button.bind(
            '<Button-1>',
            self.finalise_order_button_clicked)
        self.view.mainloop()

    def update_ui(self) -> None:
        """Update the UI after an item is added/removed."""
        self.view.order_label["text"] = str(self.order)

    def add_item_from_combobox(self, category: MenuCategory) -> None:
        """Add an item from a combo box to the order."""
        # Determine the current item based on the combo box's index.
        index = self.rows[category.value].combo_box.current()
        item = self.menu.items_in_category(category)[index]

        # Try adding the item.
        try:
            self.order.add_item(item)
            self.update_ui()
        except RuntimeError as error:
            messagebox.showerror("Add item error", str(error))

    def remove_item_from_combobox(self, category: MenuCategory) -> None:
        """Remove an item the order based on the selection in the combo box."""
        # Determine the current item based on the combo box's index.
        index = self.rows[category.value].combo_box.current()
        item = self.menu.items_in_category(category)[index]

        # Try adding the item.
        try:
            self.order.remove_item(item)
            self.update_ui()
        except RuntimeError as error:
            messagebox.showerror("Remove item error", str(error))

    def finalise_order_button_clicked(self, event: tk.Event) -> None:
        """Show the finalise order button window."""
        first_name = None
        last_name = None

        # Check if the user cancels at any time.
        user_did_cancel = False

        # Ask for the first and last name until they are non-empty strings.
        while not first_name:
            # Get the first name.
            first_name = simpledialog.askstring(
                "Enter first name", "Please enter your first name.")
            if first_name is None:
                user_did_cancel = True
                break

        # Do the same as above for the last name. Don't ask for the last name
        # if the user cancelled on the first name.
        while not last_name and not user_did_cancel:
            # Get the last name.
            last_name = simpledialog.askstring(
                "Enter last name", "Please enter your last name.")
            if last_name is None:
                user_did_cancel = True
                break

        # Only calculate the order if the user didn't cancel.
        if not user_did_cancel:
            # Calculate the order.
            for item_name in self.order.items.keys():
                count = self.order.items[item_name]
                item = self.menu.item_named(item_name)
                self.menu.sell_item(item, count)
            messagebox.showinfo("Order complete",
                                f"""Your order has been sent to the café.
    Please pay {format_price(self.order.order_total, '$')} at lunch time.
    Quote the order for {first_name} {last_name}. Thank you!""")
            self.order = Order(self.menu)
            self.update_ui()


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
