from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QKeySequence, QPainter, QColor, QPaintEvent, QKeyEvent


class Dimmer(QWidget):
    def __init__(self):
        super(Dimmer, self).__init__()
        self.setGeometry(0, 0, 1920, 1080)
        self.opacity = 0

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)

        color = QColor(0, 0, 0, self.opacity)
        painter.setBrush(color)
        painter.drawRect(0, 0, 1920, 1080)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        key = a0.key()
        print(key)
        super(Dimmer, self).keyPressEvent(a0)
        # if key_name == "[":
        #     self.opacity = max(0, self.opacity - 51)
        # elif key_name == "]":
        #     self.opacity = min(255, self.opacity + 51)
