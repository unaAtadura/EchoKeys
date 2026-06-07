import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont, QFontMetrics


class DialogWindow(QWidget):
    def __init__(self, text, height, is_latest=False, parent=None):
        super().__init__(parent)
        self.text = text
        self.target_height = height
        self.is_latest = is_latest
        self.init_ui()
        self.destroy_timer = QTimer(self)
        self.destroy_timer.timeout.connect(self.destroy)

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.9)

        if self.is_latest:
            font = QFont("Arial", 18, QFont.Bold)
        else:
            font = QFont("Arial", 14, QFont.Bold)
        
        self.current_font = font
        fm = QFontMetrics(font)
        text_width = fm.width(self.text)

        padding = 20
        window_width = text_width + padding * 2
        self.setFixedSize(window_width, self.target_height)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel(self.text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font)
        self.label.setStyleSheet("color: white;")
        layout.addWidget(self.label)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        color = QColor(80, 80, 80, 220)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 10, 10)

    def set_text(self, text):
        self.text = text
        self.label.setText(text)
        self.update_size()

    def update_size(self):
        fm = QFontMetrics(self.current_font)
        text_width = fm.width(self.text)
        padding = 20
        window_width = text_width + padding * 2
        self.setFixedSize(window_width, self.height())

    def set_height(self, height):
        self.target_height = height
        self.setFixedHeight(height)

    def set_to_old_style(self):
        self.is_latest = False
        font = QFont("Arial", 14, QFont.Bold)
        self.current_font = font
        self.label.setFont(font)
        fm = QFontMetrics(font)
        text_width = fm.width(self.text)
        padding = 20
        window_width = text_width + padding * 2
        self.setFixedSize(window_width, self.height())

    def start_destroy_timer(self, seconds=5):
        self.destroy_timer.start(seconds * 1000)

    def stop_destroy_timer(self):
        self.destroy_timer.stop()


def main():
    app = QApplication(sys.argv)
    window = DialogWindow("测试文本", 80)
    window.show()
    window.start_destroy_timer(5)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
