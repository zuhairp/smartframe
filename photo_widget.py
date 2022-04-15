from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Picture(QWidget):
    def __init__(self):
        super(Picture, self).__init__()
        self.picture_widget = QLabel()
        self.picture_widget.setGeometry(0,0,1920,1080)
        self.picture_widget.setPixmap(QPixmap('wallpaper.jpg'))
        self.picture_widget.setScaledContents(True)
        self.picture_widget.setParent(self)