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
        pen.setColor(QColor(150, 150, 150))
        painter.setPen(pen)

        font = painter.font()
        font.setFamily("Roboto")
        font.setPointSize(10)
        painter.setFont(font)

        painter.drawText(0, 0, 100, 20, Qt.AlignmentFlag.AlignCenter, self.name)
        painter.drawText(0, 80, 100, 20, Qt.AlignmentFlag.AlignCenter, self.metric)

        # Draw value
        pen = painter.pen()
        pen.setColor(QColor("white"))
        painter.setPen(pen)
        font = painter.font()
        font.setFamily("Roboto")
        font.setPointSize(30)
        painter.setFont(font)

        painter.drawText(0, 20, 100, 60, Qt.AlignmentFlag.AlignCenter, self.value)

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
        completed_rect = QRect(0, 0, completed_width, self.height())
        remaining_rect = QRect(completed_width, 0, remaining_width, self.height())
        painter.fillRect(completed_rect, QColor(200, 200, 200))
        painter.fillRect(remaining_rect, QColor(120, 120, 120))

        painter.end()


class ComicStats(QWidget):
    def __init__(self):
        super(ComicStats, self).__init__()

        self.setFixedSize(500, 115)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(0, 0, 0, 150))
        self.setPalette(p)
        path = QPainterPath()
        rect = QRectF(self.rect())
        path.addRoundedRect(rect, 20, 20)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

        self.today = StatView("Today", "Read", "", parent=self)
        self.today.move(0, 5)

        self.yesterday = StatView("Yesterday", "Read", "", parent=self)
        self.yesterday.move(100, 5)

        self.week = StatView("This Week", "Read", "", parent=self)
        self.week.move(200, 5)

        self.last_week = StatView("Last Week", "Read", "", parent=self)
        self.last_week.move(200, 5)
        self.last_week.hide()

        self.month = StatView("This Month", "Read", "", parent=self)
        self.month.move(300, 5)

        self.last_month = StatView("Last Month", "Read", "", parent=self)
        self.last_month.move(300, 5)
        self.last_month.hide()

        self.overall = StatView("Total", "Read", "", parent=self)
        self.overall.move(400, 5)

        self.progressBar = ProgressBar()
        self.progressBar.setParent(self)
        self.progressBar.move(10, 105)

        self.refresh_data()

        self.counter = 0
        self.toggle_timer = QTimer()
        self.toggle_timer.timeout.connect(self.toggle_metrics)
        self.toggle_timer.start(10000)

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)

    def refresh_data(self):
        data = self.get_comics_data()
        self.progresses = self.daily_progress(data["progress"])
        self.progressBar.total = data["total"]
        self.update_metrics()

    def toggle_metrics(self):
        self.counter += 1

        if self.counter % 2 == 0:
            self.week.show()
            self.month.show()

            self.last_week.hide()
            self.last_month.hide()
        else:
            self.week.hide()
            self.month.hide()

            self.last_week.show()
            self.last_month.show()

    def update_metrics(self):
        self.update_today()
        self.update_yesterday()
        self.update_week_to_date()
        self.update_month_to_date()
        self.update_total()
        self.update_last_week()
        self.update_last_month()

        for child in self.children():
            child.update()

    def update_today(self):
        _, today_progress = self.progresses[-1]
        _, yesterday_progress = self.progresses[-2]

        self.today.value = str(today_progress - yesterday_progress)

    def update_yesterday(self):
        _, yesterday_progress = self.progresses[-2]
        _, day_before_yesterday_progress = self.progresses[-3]

        self.yesterday.value = str(yesterday_progress - day_before_yesterday_progress)

    def update_total(self):
        _, today_progress = self.progresses[-1]
        self.overall.value = str(today_progress)
        self.progressBar.progress = today_progress

    def update_week_to_date(self):
        today, today_progress = self.progresses[-1]

        last_sunday_index = -(today.weekday() + 1) - 1
        _, last_week_progress = self.progresses[last_sunday_index]
        self.week.value = str(today_progress - last_week_progress)

    def update_last_week(self):
        today, _ = self.progresses[-1]

        last_sunday_index = -(today.weekday() + 1) - 1
        sunday_before_index = last_sunday_index - 7

        _, p1 = self.progresses[last_sunday_index]
        _, p2 = self.progresses[sunday_before_index]

        self.last_week.value = str(p1 - p2)

    def update_month_to_date(self):
        today, today_progress = self.progresses[-1]
        last_month_index = -(today.day + 1) - 1

        _, p = self.progresses[last_month_index]
        self.month.value = str(today_progress - p)

    def update_last_month(self):
        today, _ = self.progresses[-1]
        last_month_index = -(today.day + 1) - 1

        d1, p1 = self.progresses[last_month_index]

        last_last_month_index = -d1.day + last_month_index
        _, p2 = self.progresses[last_last_month_index]

        self.last_month.value = str(p1 - p2)

    def get_comics_data(self):
        url = r"https://raw.githubusercontent.com/zuhairp/comics-tracker/main/data/2022.yml"
        file = requests.get(url).content.decode("utf-8")
        data = yaml.safe_load(file)
        return data

    def daily_progress(self, progresses) -> list[tuple[datetime, int]]:
        if len(progresses) == 0:
            return []

        all_data = (p for p in progresses)
        data = next(all_data)

        current_day = data["date"]
        today = datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        )

        result = []
        previous_count = data["count"]
        while current_day <= today:
            if current_day == data["date"]:
                previous_count = data["count"]
                result.append((current_day, data["count"]))
                data = next(all_data, data)
            else:
                result.append((current_day, previous_count))
            current_day = current_day + timedelta(days=1)

        return result
