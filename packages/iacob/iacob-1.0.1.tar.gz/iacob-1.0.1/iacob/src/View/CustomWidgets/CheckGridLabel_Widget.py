import math

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QBrush, QColor, QPainter
from PyQt5.QtWidgets import QLabel, QWidget, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QVBoxLayout, \
    QSizePolicy


class CheckGridLabel_Widget(QWidget):
    name : str
    clicked = pyqtSignal(str)
    orientation : str
    checked : bool = True

    def __init__(self, name, orientation, color, rotation=0):
        super().__init__()

        self.name = name
        self.orientation = orientation

        self.setContentsMargins(0, 0, 0, 0)

        self.view = QGraphicsView(self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background: transparent;"
                                "border : 0px;")  # Set QGraphicsView background to transparent
        self.view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scene = QGraphicsScene(self.view)
        self.view.setScene(self.scene)

        # Add two spaces around the name
        label = QLabel(f" {name} ")
        label.setProperty("class", "standardLabel")
        label.setStyleSheet("background: transparent;")  # Set QLabel background to transparent

        # Convert 0 to 1 color values into 0 to 255 values
        color = [int(color * 255) for color in color]
        color = f"{color[0]}, {color[1]}, {color[2]}"
        label.setStyleSheet(f"background-color : rgb({color});")
        label.adjustSize()

        proxy = QGraphicsProxyWidget()
        proxy.setWidget(label)
        # Apply rotation transformation
        proxy.setTransformOriginPoint(label.rect().center())
        proxy.setRotation(rotation)

        self.scene.addItem(proxy)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        match rotation :
            case 0 | 180:
                self.setFixedHeight(label.height())
            case 45 | 135 | 225 | 315:
                self.setFixedWidth(label.width() ** (1/2))
                self.setFixedHeight(label.width() ** (1/2))
            case 90 | 270:
                self.setFixedWidth(label.height())



    def mousePressEvent(self, ev):
        # Emit object name
        self.clicked.emit(self.objectName())
