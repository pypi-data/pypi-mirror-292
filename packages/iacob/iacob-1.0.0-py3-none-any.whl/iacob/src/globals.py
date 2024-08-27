from PyQt5.QtGui import QColor

version = "1.0.0"
release_date = "2024-08-26"

# Pay attention to the format (2 / 3 / 7 colors authorized) 
colorPalettes = {
            "Red -> White -> Blue": [
                [QColor(255, 0, 0), QColor(200, 200, 200), QColor(0, 0, 255)], 
                "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \
                stop:0 rgba(255, 0, 0, 255), \
                stop:0.5 rgba(200, 200, 200, 255), \
                stop:1 rgba(0, 0, 255, 255));"
            ],
            "White -> Blue": [
                [QColor(255, 255, 255), QColor(0, 0, 255)],
                "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \
                stop:0 rgba(255, 255, 255, 255), \
                stop:1 rgba(0, 0, 255, 255));"
            ],
            "White -> Red": [
                [QColor(255, 255, 255), QColor(255, 0, 0)],
                "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \
                stop:0 rgba(255, 255, 255, 255), \
                stop:1 rgba(255, 0, 0, 255));"
            ],
            "White -> Brown": [
                [QColor(255, 255, 255), QColor(165, 42, 42)],
                "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \
                stop:0 rgba(255, 255, 255, 255), \
                stop:1 rgba(165, 42, 42, 255));"
            ],
            "Rainbow": [
                [
                    QColor(48, 18, 59),    # Red
                    QColor(70, 134, 250),  # Orange
                    QColor(26, 228, 182),  # Yellow
                    QColor(163, 253, 60),    # Green
                    QColor(250, 186, 56),    # Blue
                    QColor(228, 70, 11),   # Indigo
                    QColor(122, 4, 3) # Violet
                ],
                "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \
                stop:0 rgba(48, 18, 59, 255), \
                stop:0.17 rgba(70, 134, 250, 255), \
                stop:0.33 rgba(26, 228, 182, 255), \
                stop:0.5 rgba(163, 253, 60, 255), \
                stop:0.67 rgba(250, 186, 56, 255), \
                stop:0.83 rgba(228, 70, 11, 255), \
                stop:1 rgba(122, 4, 3, 255));"
            ]
        }


