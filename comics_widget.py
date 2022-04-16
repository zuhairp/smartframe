from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *

import yaml
import requests
from datetime import datetime, timedelta, timezone

class StatView(QWidget):
    def __init__(self, name: str, metric: str, value: str, *args, **kwargs):
        super(StatView, self).__init__(*args, **kwargs)

        self.name = name
        self.metric = metric
        self.value = value

        self.setFixedSize(100, 100)

    def paintEvent(self, e):
        painter = QPainter(self)

        # Draw name and metric
        pen = painter.pen()
        pen.setColor(QColor(150,150,150))
        painter.setPen(pen)

        font = painter.font()
        font.setFamily('Roboto')
        font.setPointSize(10)
        painter.setFont(font)

        painter.drawText(0,0,100,20, Qt.AlignmentFlag.AlignCenter, self.name)
        painter.drawText(0,80,100,20, Qt.AlignmentFlag.AlignCenter, self.metric)

        # Draw value
        pen = painter.pen()
        pen.setColor(QColor('white'))
        painter.setPen(pen)
        font = painter.font()
        font.setFamily('Roboto')
        font.setPointSize(30)
        painter.setFont(font)

        painter.drawText(0,20,100,60, Qt.AlignmentFlag.AlignCenter, self.value)


        painter.end()

class ProgressBar(QWidget):
    def __init__(self):
        super(ProgressBar, self).__init__()

        self.progress = 0
        self.total = 1

        self.setFixedSize(480, 1)

    def paintEvent(self, e):
        painter = QPainter(self)

        ratio = self.progress / self.total 
        completed_width = int(self.width() * ratio)
        remaining_width = self.width() - completed_width

        # Draw completed progress
        completed_rect = QRect(0,0,completed_width,self.height())
        remaining_rect = QRect(completed_width, 0, remaining_width, self.height())
        painter.fillRect(completed_rect, QColor(200,200,200))
        painter.fillRect(remaining_rect, QColor(120,120,120))

        painter.end()
    
class ComicStats(QWidget):
    def __init__(self):
        super(ComicStats, self).__init__()

        self.setFixedSize(500, 115)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(0,0,0,150))
        self.setPalette(p)
        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, 20, 20)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

        self.today = StatView('Today', 'Read', '', parent=self)
        self.today.move(0,5)

        self.yesterday = StatView('Yesterday', 'Read', '', parent=self)
        self.yesterday.move(100,5)

        self.week = StatView('7-Day', 'Read', '', parent=self)
        self.week.move(200,5)

        self.month = StatView('30-Day', 'Read', '', parent=self)
        self.month.move(300,5)

        self.overall = StatView('Total', 'Read', '', parent=self)
        self.overall.move(400,5)

        self.progressBar = ProgressBar()
        self.progressBar.setParent(self)
        self.progressBar.move(10,105)

        self.refresh_data()

        self.metric = 'Read'
        self.toggle_timer = QTimer()
        self.toggle_timer.timeout.connect(self.toggle_metrics)
        self.toggle_timer.start(10000)

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)
    
    def refresh_data(self):
        data = self.get_comics_data() 
        self.progresses = self.daily_progress(data['progress'])
        self.progressBar.total = data['total']
        self.update_metrics('Average')
    
    def toggle_metrics(self):
        self.metric = 'Average' if self.metric == 'Read' else 'Read'
        self.update_metrics(self.metric)

    def update_metrics(self, metric='Read'):
        today, today_progress = self.progresses[-1]
        _, yesterday_progress = self.progresses[-2]
        _, day_before_yday_progress = self.progresses[-3]
        _, week_progress = self.progresses[-8]
        _, month_progress = self.progresses[-31]
        start_day, _ = self.progresses[0]

        self.progressBar.progress = today_progress

        self.today.value = str(today_progress - yesterday_progress)
        self.yesterday.value = str(yesterday_progress - day_before_yday_progress)
        self.overall.value = str(today_progress)

        if metric == 'Read':
            self.week.metric = 'Read'
            self.week.value = str(today_progress - week_progress)
            
            self.month.metric = 'Read'
            self.month.value = str(today_progress - month_progress)

        elif metric == 'Average':
            self.week.metric = 'Average'
            week_average = (today_progress - week_progress) / 7
            self.week.value = f'{week_average:.01f}'

            self.month.metric = 'Average'
            month_average = today_progress / (today - start_day).days
            self.month.value = f'{month_average:.01f}'
        else:
            assert False
        
        for child in self.children():
            child.update()

    def get_comics_data(self):
        url = r"https://raw.githubusercontent.com/zuhairp/comics-tracker/main/data/2022.yml"
        file = requests.get(url).content.decode('utf-8')
        data = yaml.safe_load(file)
        return data

    def daily_progress(self, progresses) -> list[tuple[datetime, int]]:
        if len(progresses) == 0:
            return []
        
        all_data = (p for p in progresses)
        data = next(all_data) 

        current_day = data['date']
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

        result = []
        previous_count = data['count']
        while current_day <= today:
            if current_day == data['date']:
                previous_count = data['count']
                result.append((current_day, data['count']))
                data = next(all_data, data)
            else: 
                result.append((current_day, previous_count))
            current_day = current_day + timedelta(days=1)

        return result 