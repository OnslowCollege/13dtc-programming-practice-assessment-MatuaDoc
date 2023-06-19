"""
Café ordering system.

Tkinter view.

Created by Matua Doc.
Created on 2023-06-11.
"""

import tkinter as tk
from tkinter import messagebox


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
