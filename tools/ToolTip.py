import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont


class ToolTipWindow(QWidget):
    tooltip_closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("使用提示")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.95)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("欢迎使用 EchoKeys")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)

        tips = [
            "1. 从任务托盘的图标打开日志窗口可以暂停对键鼠的监控",
            "2. 觉得蓝色圆点碍事的话，也可以在任务托盘的图标处点击「隐藏窗口」",
            "3. 用鼠标移动一下下面的蓝色圆点就可以关闭我啦！"
        ]

        for tip in tips:
            label = QLabel(tip)
            label.setAlignment(Qt.AlignLeft)
            label.setFont(QFont("Microsoft YaHei", 10))
            label.setStyleSheet("color: #ffffff;")
            label.setWordWrap(True)
            layout.addWidget(label)

        self.adjustSize()
        self.setMinimumWidth(380)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        color = QColor(60, 60, 80, 240)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(100, 120, 180), 2))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 12, 12)

    def close_tooltip(self):
        self.tooltip_closed.emit()
        self.hide()
        self.close()


def main():
    app = QApplication(sys.argv)
    window = ToolTipWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
