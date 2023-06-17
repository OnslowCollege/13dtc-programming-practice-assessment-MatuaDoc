"""
Main.

Created by: NAME
Date: DATE
"""

from PySide6.QtWidgets import *

if __name__ == "__main__":
    # Required
    app = QApplication()
    
    # Main window
    main_window = QMainWindow()
    main_window.resize(1280, 720)
    
    # Central widget
    main_widget = QWidget()
    main_widget_layout = QVBoxLayout(main_widget)
    main_window.setCentralWidget(main_widget)
    
    # Add items to central widget
    for i in range(5):
        main_widget_layout.addWidget(QLabel(str(i)))
    main_widget.addWidget(QPushButton("OK"))
    
    # Run the program
    main_window.show()
    app.exec()
