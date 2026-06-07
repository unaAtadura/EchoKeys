import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QCursor, QRegion


class MouseHighlightWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.left_pressed = False
        self.right_pressed = False
        self.current_color = QColor(255, 200, 0, 100)
        self.window_size = 80
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_window_internal)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setWindowOpacity(0.7)
        self.setFixedSize(self.window_size, self.window_size)
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QBrush(self.current_color))
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1))
        painter.drawEllipse(0, 0, self.width(), self.height())

        region = QRegion(self.rect(), QRegion.Ellipse)
        self.setMask(region)

    def update_color(self):
        if self.left_pressed and self.right_pressed:
            self.current_color = QColor(100, 100, 255, 100)
        elif self.left_pressed:
            self.current_color = QColor(255, 200, 0, 100)
        elif self.right_pressed:
            self.current_color = QColor(255, 105, 180, 100)
        else:
            self.current_color = QColor(255, 200, 0, 100)

    def update_position(self):
        cursor_pos = QCursor.pos()
        x = cursor_pos.x() - self.window_size // 2
        y = cursor_pos.y() - self.window_size // 2
        self.move(x, y)

    def on_left_press(self, x, y):
        self.left_pressed = True
        self.hide_timer.stop()
        self.update_color()
        self.update_position()
        self.show()
        self.update()

    def on_right_press(self, x, y):
        self.right_pressed = True
        self.hide_timer.stop()
        self.update_color()
        self.update_position()
        self.show()
        self.update()

    def on_left_release(self, x, y):
        self.left_pressed = False
        if self.right_pressed:
            self.update_color()
            self.update()
        else:
            self.hide_window_internal()

    def on_right_release(self, x, y):
        self.right_pressed = False
        if self.left_pressed:
            self.update_color()
            self.update()
        else:
            self.hide_window_internal()

    def on_mouse_move(self, x, y):
        if self.left_pressed or self.right_pressed:
            self.update_position()

    def hide_window_internal(self):
        self.hide()


def main():
    app = QApplication(sys.argv)
    window = MouseHighlightWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
