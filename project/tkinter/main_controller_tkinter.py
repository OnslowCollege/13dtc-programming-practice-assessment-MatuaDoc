"""
Café ordering system.

Controller/presenter for UI version.

Created by Matua Doc.
Created on 2023-06-11.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Callable

from main_utils import format_price
from main_utils import get_valid_bool, get_valid_input, get_valid_int
from main_model import Menu, MenuItem, MenuCategory, Order
from main_view_tkinter import CafeWindow


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
