import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from datetime import datetime


class Clock(QWidget):
    on_minute = pyqtSignal()
    on_day = pyqtSignal()

    def __init__(self):
        super(Clock, self).__init__()
        self.time = datetime.now()
        self.time_widget = QLabel()

        text_style = r"QLabel {color: white; padding: 0px; margin: 0px;}"
        self.time_widget.setParent(self)
        self.time_widget.setFont(QFont("Roboto", 100))
        self.time_widget.setStyleSheet(text_style)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(500)

        self.draw_time()

    def update_time(self):
        prev_time = self.time
        self.time = datetime.now()
        if prev_time.minute != self.time.minute:
            self.draw_time()
            self.on_minute.emit()

        if prev_time.day != self.time.day:
            self.on_day.emit()

    def draw_time(self):
        fmt = "%-I:%M" if sys.platform == "linux" else "%#I:%M"
        self.time_widget.setText(self.time.strftime(fmt))
