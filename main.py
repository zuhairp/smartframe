import os

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *

import os
import sys
from photo_widget import Picture
from comics_widget import ComicStats

from prayer_widget import PrayerTable
from clock import Clock

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        QFontDatabase.addApplicationFont("Roboto-Regular.ttf")
        QFontDatabase.addApplicationFont("Roboto-Bold.ttf")

        windowWidget = QWidget()

        picture = Picture()
        picture.setParent(windowWidget)

        clock = Clock()
        clock.setParent(windowWidget)
        clock.move(50, 50)

        comic_info = ComicStats()
        comic_info.setParent(windowWidget)
        x = 20
        y = 1080 - comic_info.height() - 20
        comic_info.move(x, y)

        prayer_times = PrayerTable()
        prayer_times.setParent(windowWidget)

        x = 1920 - prayer_times.width() - 20
        y = 1080 - prayer_times.height() - 20
        prayer_times.move(x, y)

        clock.on_minute.connect(prayer_times.play_adhan_if_necessary)
        clock.on_day.connect(prayer_times.refresh_data)

        self.setCentralWidget(windowWidget)
        self.showFullScreen()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())