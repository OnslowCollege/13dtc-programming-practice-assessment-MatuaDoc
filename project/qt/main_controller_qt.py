"""
Café ordering system.

Controller/presenter for UI version.

Created by Matua Doc.
Created on 2023-06-11.
"""

from main_view_qt import CafeWindow, FinaliseOrderWindow
from main_model import Menu, MenuCategory, Order
from main_utils import get_valid_bool, get_valid_input, get_valid_int
from main_utils import format_price
from dataclasses import dataclass
from PySide6.QtWidgets import *
from typing import Callable


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
                f""" Your order has been sent to the café.
Please pay {format_price(self._order.order_total, '$')} at lunch time.
Quote the order for {window.first_name} {window.last_name}. Thank you!"""
            ).exec()
            self._order = Order(self._menu)
            self.update_ui()
