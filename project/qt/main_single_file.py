"""
Café ordering system.

Single file version for Qt.

Created by Matua Doc.
Created on 2023-06-11.
"""


from enum import Enum
from dataclasses import dataclass
import json
from PySide6.QtWidgets import *
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


class CafeWindow(QMainWindow):
    """Main window for the café ordering system."""

    def __init__(self) -> None:
        """Create the window layout."""
        super().__init__()

        # Create the main widget and layout.
        self.widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.widget.setLayout(self.main_layout)
        self.setCentralWidget(self.widget)

        # Add section for menu items.
        self.menu_widget = QWidget()
        self.menu_widget_layout = QVBoxLayout()
        self.menu_widget.setLayout(self.menu_widget_layout)
        self.main_layout.addWidget(self.menu_widget)

        self.order_label = QLabel("")
        self.main_layout.addWidget(self.order_label)

        # Add finalise order button.
        self.finalise_order_button = QPushButton("Finalise order")
        self.main_layout.addWidget(self.finalise_order_button)

        self.resize(640, 400)


class FinaliseOrderWindow(QDialog):
    """The window asking for the user's name for the order."""

    def __init__(self) -> None:
        """Create the window to ask for the user's name."""
        super().__init__()

        # Create the layout.
        self.main_layout = QFormLayout()
        self.setLayout(self.main_layout)

        # Add the fields.
        self.first_name_line_edit = QLineEdit()
        self.last_name_line_edit = QLineEdit()
        self.main_layout.addRow("First name:", self.first_name_line_edit)
        self.main_layout.addRow("Last name:", self.last_name_line_edit)

        # Keep track of the names themselves.
        self.first_name = ""
        self.last_name = ""

        # Keep track of whether the names are non-empty.
        self.first_name_valid = False
        self.last_name_valid = False

        # Connect signal functions to disable the dialog buttons
        # if the line edits are empty.
        self.first_name_line_edit.textEdited.connect(self.first_textEdited)
        self.last_name_line_edit.textEdited.connect(self.last_textEdited)

        # Add the finalise button.
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.button(
            QDialogButtonBox.StandardButton.Save).setEnabled(False)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.main_layout.addWidget(self.buttonBox)

    def first_textEdited(self, text: str) -> None:
        """Update if the first name is non-empty."""
        self.first_name_valid = len(text) > 0
        self.first_name = text
        self.update_ui()

    def last_textEdited(self, text: str) -> None:
        """Update if the last name is non-empty."""
        self.last_name_valid = len(text) > 0
        self.last_name = text
        self.update_ui()

    def update_ui(self) -> None:
        """Enable the Save button if the name fields contain valid text."""
        valid = self.first_name_valid and self.last_name_valid
        self.buttonBox.button(
            QDialogButtonBox.StandardButton.Save).setEnabled(valid)


class Row:
    """A row of widgets."""

    def __init__(self,
                 category: MenuCategory,
                 combo_box: QComboBox,
                 add_button: QPushButton,
                 remove_button: QPushButton,
                 add_method: Callable[[MenuCategory], None],
                 remove_method: Callable[[MenuCategory], None]):
        """Connect the signal function for the buttons."""
        self._category = category
        self._combo_box = combo_box
        self._add_button = add_button
        self._remove_button = remove_button

        # Connect the signals.
        self._add_button.clicked.connect(lambda: add_method(self._category))
        self._remove_button.clicked.connect(lambda: (
            remove_method(self._category)))

    @property
    def category(self) -> MenuCategory:
        """Return the category for the row."""
        return self._category

    @property
    def combo_box(self) -> QComboBox:
        """Return the combo box for a category."""
        return self._combo_box

    @property
    def add_button(self) -> QPushButton:
        """Return the add button for a category."""
        return self._add_button

    @property
    def remove_button(self) -> QPushButton:
        """Return the remove button for a category."""
        return self._remove_button


@dataclass
class CafeProgram:
    """The program to run."""

    _menu: Menu
    _order: Order

    def __post_init__(self) -> None:
        """Create the controller/presenter for the UI version."""
        # Add the view.
        self._view = CafeWindow()
        self._view.show()

        # Keep track of the per-category widgets.
        self.rows: list[Row] = []

        # Add items for each category.
        for category in MenuCategory:
            row_layout = QHBoxLayout()

            # Add row label.
            label = QLabel(str(category))
            label.setFixedWidth(100)
            row_layout.addWidget(label)

            # Add the items to a combo box.
            combo_box = QComboBox()
            combo_box.setFixedWidth(400)
            items = self._menu.items_in_category(category)
            for item in items:
                combo_box.addItem(
                    f"{format_price(item.price, '$')} - {item.name}")
            row_layout.addWidget(combo_box)
            row_layout.addStretch()

            # Add the add and remove button.
            add_button = QPushButton("+")
            remove_button = QPushButton("-")
            row_layout.addWidget(add_button)
            row_layout.addWidget(remove_button)

            self.rows.append(Row(category,
                                 combo_box,
                                 add_button,
                                 remove_button,
                                 self.add_item_from_combobox,
                                 self.remove_item_from_combobox))

            # Add a row. Codespace might show an error, but the layout is
            # definitely a QVBoxLayout.
            self._view.menu_widget_layout.addLayout(row_layout)

        # Connect signal function for the finalise button.
        self._view.finalise_order_button.clicked.connect(
            self.finalise_order_button_clicked)

    def update_ui(self) -> None:
        """Update the UI after an item is added/removed."""
        self._view.order_label.setText(str(self._order))

    def add_item_from_combobox(self, category: MenuCategory) -> None:
        """Add an item from a combo box to the order."""
        # Determine the current item based on the combo box's index.
        index = self.rows[category.value].combo_box.currentIndex()
        item = self._menu.items_in_category(category)[index]

        # Try adding the item.
        try:
            self._order.add_item(item)
            self.update_ui()
        except RuntimeError as error:
            QMessageBox(
                QMessageBox.Icon.Critical,
                "Add item error",
                str(error)
            ).exec()

    def remove_item_from_combobox(self, category: MenuCategory) -> None:
        """Remove an item the order based on the selection in the combo box."""
        # Determine the current item based on the combo box's index.
        index = self.rows[category.value].combo_box.currentIndex()
        item = self._menu.items_in_category(category)[index]

        # Try adding the item.
        try:
            self._order.remove_item(item)
            self.update_ui()
        except RuntimeError as error:
            QMessageBox(
                QMessageBox.Icon.Critical,
                "Remove item error",
                str(error)
            ).exec()

    def finalise_order_button_clicked(self, checked: bool) -> None:
        """Show the finalise order button window."""
        window = FinaliseOrderWindow()
        result = window.exec()
        if result:
            # Remove the items from stock.
            for item_name in self._order.items.keys():
                count = self._order.items[item_name]
                item = self._menu.item_named(item_name)
                self._menu.sell_item(item, count)
            QMessageBox(
                QMessageBox.Icon.Information,
                "Order complete",
                f"""Thank you {window.first_name} {window.last_name}.
Your order has been sent to the café.

Please pay {format_price(self._order.order_total, '$')} at lunch time."""
            ).exec()
            self._order = Order(self._menu)
            self.update_ui()


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
