import os
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout

class LoadingPopup(QDialog):
    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint)

        resourcedir = Path(__file__).parent.parent.parent / 'resources'
        with open(os.path.join(resourcedir, "Style_Application.qss"), 'r') as file:
            stylesheet = file.read()
            self.setStyleSheet(stylesheet)

        self.setWindowTitle("Loading")
        self.setModal(True)
        self.setFixedSize(200, 100)

        layout = QVBoxLayout()
        self.label = QLabel("Loading...", self)
        self.label.setProperty("class", "loadingPopup")

        layout.addWidget(self.label)
        self.setLayout(layout)
        