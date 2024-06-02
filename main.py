import sys

from PyQt5.QtGui import QFontDatabase, QKeyEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt
from dimmer import Dimmer
from photo_widget import Picture

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

        prayer_times = PrayerTable()
        prayer_times.setParent(windowWidget)

        x = 1920 - prayer_times.width() - 20
        y = 1080 - prayer_times.height() - 20
        prayer_times.move(x, y)

        clock.on_minute.connect(prayer_times.play_adhan_if_necessary)
        clock.on_day.connect(prayer_times.refresh_data)

        self.dimmer = Dimmer()
        self.dimmer.setParent(windowWidget)

        self.setCentralWidget(windowWidget)
        self.showFullScreen()

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Q:
            sys.exit(0)
        elif a0.key() == Qt.Key.Key_D:
            self.dimmer.opacity = 200 if self.dimmer.opacity == 0 else 0
            self.dimmer.repaint()
        # elif a0.key() == Qt.Key.Key_BracketLeft:
        #     self.dimmer.opacity = min(255, self.dimmer.opacity + 80)
        #     self.dimmer.repaint()
        # elif a0.key() == Qt.Key.Key_BracketRight:
        #     self.dimmer.opacity = max(0, self.dimmer.opacity - 80)
        #     self.dimmer.repaint()


app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())
