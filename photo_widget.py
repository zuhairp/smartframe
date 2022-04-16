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

        self.watcher = QFileSystemWatcher()
        self.watcher.setParent(self)

        self.watcher.addPath('/home/zuhair/smartframe/wallpaper.jpg')
        self.watcher.addPath('/home/zuhair/smartframe')

        self.watcher.fileChanged.connect(self.reload_image)
        self.watcher.directoryChanged.connect(self.reload_image)

    def reload_image(self, path):
        print(path)
        self.picture_widget.setPixmap(QPixmap('wallpaper.jpg'))
