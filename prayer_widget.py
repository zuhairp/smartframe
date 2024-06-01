import sys
import pathlib
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *

from datetime import date, datetime
from praytime import PrayTimes

class PrayerTime(QWidget):
    def __init__(self, name: str):
        super(PrayerTime, self).__init__()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)


        self.name = QLabel(name+":")
        self.time = QLabel("0:00")

        font = QFont('Roboto', 28)

        text_style = r"QLabel {color: white; padding: 0px; margin: 0px;}"
        self.name.setStyleSheet(text_style)
        self.time.setStyleSheet(text_style)
        self.name.setFont(font)
        self.time.setFont(font)

        self.name.adjustSize()
        self.time.adjustSize()

        self.layout.addWidget(self.name, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.time, 1, alignment=Qt.AlignmentFlag.AlignLeft)
    
    def set_time(self, time: str):
        self.time.setText(time)

class PrayerTable(QWidget):
    def __init__(self):
        super(PrayerTable, self).__init__()

        prayer_names = ['fajr', 'shuruq', 'zuhr', 'asr', 'maghrib', 'isha']
        self.time_widgets = {n: PrayerTime(n) for n in prayer_names}

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.setFixedSize(250, 300)
    
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(0,0,0,100))
        self.setPalette(p)

        self.layout.addSpacerItem(QSpacerItem(self.width(),20,QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding))
        for w in self.time_widgets.values():
            self.layout.addWidget(w)
        
        self.layout.addSpacerItem(QSpacerItem(self.width(),20,QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding))
        
        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, 25, 25)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

        self.player = QMediaPlayer()
        self.player.setParent(self)

        script_directory = pathlib.Path(__file__).parent.resolve()
        self.adhan = QMediaContent(QUrl.fromLocalFile(str(script_directory.joinpath("adhan.mp3").resolve())))
        self.fajr_adhan = QMediaContent(QUrl.fromLocalFile(str(script_directory.joinpath("fajr_adhan.mp3").resolve())))

        self.refresh_data()
    

    def str_to_datetime(self, time):
        today = date.today() 
        year, month, day = today.year, today.month, today.day
        return datetime.strptime(time, "%H:%M").replace(year=year, day=day, month=month)

    def refresh_data(self):
        prayTimes = PrayTimes('ISNA')
        prayTimes.adjust({'asr': 'Hanafi'})

        today = date.today() 
        year, month, day = today.year, today.month, today.day
        times = prayTimes.getTimes([year, month, day], (47.67, -122.12), -7)
        self.prayer_times = {
            'fajr': self.str_to_datetime(times['fajr']),
            'shuruq': self.str_to_datetime(times['sunrise']),
            'zuhr': self.str_to_datetime(times['dhuhr']),
            'asr': self.str_to_datetime(times['asr']),
            'maghrib': self.str_to_datetime(times['maghrib']),
            'isha': self.str_to_datetime(times['isha']),
        }

        for prayer, time in self.prayer_times.items():
            widget = self.time_widgets[prayer]

            if sys.platform == 'linux':
                time_str = time.strftime('%-I:%M')
            else:
                time_str = time.strftime('%#I:%M')

            widget.set_time(time_str)
    
    def play_adhan_if_necessary(self):

        time = datetime.now()
        h, m = time.hour, time.minute
        for prayer in ['zuhr', 'asr', 'maghrib', 'isha']:
            prayer_time = self.prayer_times[prayer]

            if prayer_time.hour == h and prayer_time.minute == m:
                self.player.setMedia(self.adhan)

                volume = 20 if prayer in ['zuhr', 'asr'] else 100
                self.player.setVolume(volume)
                self.player.play()
                return
        
        fajr_time = self.prayer_times['fajr']
        if fajr_time.hour == h and fajr_time.minute == m:
            self.player.setMedia(self.fajr_adhan)
            self.player.setVolume(100)
            self.player.play()
            return

        

