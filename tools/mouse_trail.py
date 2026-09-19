import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QCursor


class MouseTrailWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.trail_points = []
        self.max_trail_length = 50
        self.head_radius = 5
        self.tail_width = 6
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(16)
        self.refresh_timer.timeout.connect(self._refresh_trail)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setFixedSize(screen_geometry.width(), screen_geometry.height())
        self.move(0, 0)
        self.hide()

    def paintEvent(self, event):
        point_count = len(self.trail_points)
        if point_count == 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 彗尾：线段向尾部逐段变细、变淡，形成拖尾收尾效果
        for i in range(point_count - 1):
            fade = 1.0 - i / max(point_count - 1, 1)
            alpha = int(160 * fade)
            width = max(1.0, self.tail_width * fade)
            painter.setPen(QPen(QColor(135, 206, 250, alpha), width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.trail_points[i], self.trail_points[i + 1])
        # 彗星头部：鼠标当前位置的亮点
        head = self.trail_points[0]
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(135, 206, 250, 200)))
        painter.drawEllipse(head, self.head_radius, self.head_radius)

    def on_mouse_move(self, x, y):
        # 与 MouseHighlightWindow 相同：忽略监听线程的物理坐标，
        # 统一用 QCursor 的 Qt 逻辑坐标，规避高 DPI 换算差异
        head_pos = QCursor.pos()
        self.trail_points.insert(0, head_pos)
        del self.trail_points[self.max_trail_length:]
        if not self.isVisible():
            self.show()
        if not self.refresh_timer.isActive():
            self.refresh_timer.start()
        self.update()

    def _refresh_trail(self):
        # 鼠标静止时逐帧收缩拖尾，实现自然收尾后隐藏窗口
        if self.trail_points:
            del self.trail_points[-1]
            self.update()
        if not self.trail_points:
            self.refresh_timer.stop()
            self.hide()


def main():
    app = QApplication(sys.argv)
    window = MouseTrailWindow()
    probe_timer = QTimer()
    probe_timer.setInterval(16)
    last_pos = None
    def probe_cursor():
        nonlocal last_pos
        pos = QCursor.pos()
        if pos != last_pos:
            last_pos = pos
            window.on_mouse_move(pos.x(), pos.y())
    probe_timer.timeout.connect(probe_cursor)
    probe_timer.start()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
