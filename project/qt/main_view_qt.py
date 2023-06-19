"""
Café ordering system.

Qt view.

Created by Matua Doc.
Created on 2023-06-11.
"""

from PySide6.QtWidgets import *


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
