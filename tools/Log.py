import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import pyqtSignal


class LogWindow(QWidget):
    window_opened = pyqtSignal()
    window_closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("日志")
        self.resize(600, 400)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def append_log(self, message, color="#d4d4d4"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_text.append(
            f'<span style="color: #888888;">[{timestamp}]</span> <span style="color: {color};">{message}</span>'
        )
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)

    def append_log_with_timestamp(self, timestamp, message, color="#d4d4d4"):
        self.log_text.append(
            f'<span style="color: #888888;">[{timestamp}]</span> <span style="color: {color};">{message}</span>'
        )
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)

    def clear_log(self):
        self.log_text.clear()

    def showEvent(self, event):
        super().showEvent(event)
        self.window_opened.emit()

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = LogWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
