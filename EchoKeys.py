import sys
import re
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QSystemTrayIcon, QMenu, QAction, QStyle)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QRegion

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
try:
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
except AttributeError:
    pass
from tools.Log import LogWindow
from tools.Dialog import DialogWindow
from tools.key_mouse_monitor import KeyMouseMonitor
from tools.mouse_highlight import MouseHighlightWindow
from tools.ToolTip import ToolTipWindow
from PyQt5.QtCore import pyqtSignal


class CircleWindow(QWidget):
    position_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dragging = False
        self.drag_pos = QPoint()
        self._original_pos = None
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("EchoKeys")
        self.setFixedSize(80, 80)
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.7)
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(100, 150, 255, 180)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(50, 100, 200), 2))
        painter.drawEllipse(0, 0, self.width(), self.height())
        region = QRegion(self.rect(), QRegion.Ellipse)
        self.setMask(region)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self._original_pos = self.pos()
            event.accept()
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_pos
            
            screen_geometry = QApplication.primaryScreen().geometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            window_width = self.width()
            window_height = self.height()
            
            new_x = max(0, min(new_pos.x(), screen_width - window_width))
            new_y = max(0, min(new_pos.y(), screen_height - window_height))
            
            self.move(new_x, new_y)
            
            if self._original_pos is not None and (self.pos().x() != self._original_pos.x() or self.pos().y() != self._original_pos.y()):
                self.position_changed.emit()
                self._original_pos = None
            
            event.accept()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    def contains_global_point(self, global_x, global_y):
        rect = self.rect()
        local_point = self.mapFromGlobal(QPoint(global_x, global_y))
        if not rect.contains(local_point):
            return False
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        radius = rect.width() // 2
        dx = local_point.x() - center_x
        dy = local_point.y() - center_y
        return dx * dx + dy * dy <= radius * radius
def create_tray_icon(app, window, log_window):
    tray_icon = QSystemTrayIcon(app)
    icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
    tray_icon.setIcon(icon)
    tray_icon.setToolTip("EchoKeys")
    menu = QMenu()
    show_action = QAction("显示窗口", app)
    show_action.triggered.connect(window.show)
    show_action.triggered.connect(window.raise_)
    show_action.triggered.connect(window.activateWindow)
    menu.addAction(show_action)
    hide_action = QAction("隐藏窗口", app)
    hide_action.triggered.connect(window.hide)
    menu.addAction(hide_action)
    log_action = QAction("日志", app)
    log_action.triggered.connect(log_window.show)
    log_action.triggered.connect(log_window.raise_)
    log_action.triggered.connect(log_window.activateWindow)
    menu.addAction(log_action)
    menu.addSeparator()
    exit_action = QAction("退出", app)
    exit_action.triggered.connect(tray_icon.hide)
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)
    tray_icon.setContextMenu(menu)
    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.Trigger:
            if window.isVisible():
                window.hide()
            else:
                window.show()
                window.raise_()
                window.activateWindow()
    tray_icon.activated.connect(on_tray_activated)
    return tray_icon
def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = CircleWindow()
    log_window = LogWindow()
    
    monitor = KeyMouseMonitor()
    mouse_highlight = MouseHighlightWindow()
    
    CIRCLE_DIAMETER = 80
    CIRCLE_HEIGHT = 80
    MAX_DIALOGS = 6
    DIALOG_GAP = 5
    DIALOG_HEIGHT_LARGE = 60
    DIALOG_HEIGHT_SMALL = 30
    
    dialogs = []
    last_key_time = None
    last_key_is_alphanum = False
    
    log_history = []
    
    def add_log_history(message, color="#d4d4d4"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_history.append((timestamp, message, color))
    
    def on_log_window_opened():
        log_window.clear_log()
        for timestamp, message, color in log_history:
            log_window.append_log_with_timestamp(timestamp, message, color)
        monitor.stop()
    
    def on_log_window_closed():
        monitor.start()
    
    log_window.window_opened.connect(on_log_window_opened)
    log_window.window_closed.connect(on_log_window_closed)
    
    modifier_key_names = ['ctrl', 'shift', 'alt', 'cmd', 'fn', 'menu']
    special_key_names = ['space', 'enter', 'tab', 'escape', 'backspace', 'delete', 'insert', 
                         'home', 'end', 'page_up', 'page_down', 'up', 'down', 'left', 'right',
                         'caps_lock', 'num_lock', 'scroll_lock', 'print_screen', 'pause',
                         'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12']
    
    def is_alphanum_or_symbol(key_str):
        lower_key = key_str.lower().strip()
        if ' + ' in lower_key:
            return False
        for mod in modifier_key_names:
            if lower_key.startswith(mod + '_l') or lower_key.startswith(mod + '_r'):
                return False
        if lower_key in modifier_key_names:
            return False
        if lower_key in special_key_names:
            return False
        if lower_key.startswith('numpad'):
            return True
        if len(lower_key) == 1:
            if lower_key.isalnum():
                return True
            if re.match(r'[!@#$%^&*()_+\-=\[\]{};\\:"\'|,.<>/?`~]', lower_key):
                return True
        return False
    
    def get_dialog_direction():
        screen_geometry = QApplication.primaryScreen().geometry()
        circle_geom = window.geometry()
        space_above = circle_geom.top()
        space_below = screen_geometry.height() - circle_geom.bottom()
        return 'above' if space_above > space_below else 'below'
    
    def get_horizontal_alignment():
        screen_geometry = QApplication.primaryScreen().geometry()
        circle_geom = window.geometry()
        space_left = circle_geom.left()
        space_right = screen_geometry.width() - circle_geom.right()
        return 'left' if space_left < space_right else 'right'
    
    def update_dialog_positions():
        if not dialogs:
            return
        
        direction = get_dialog_direction()
        h_alignment = get_horizontal_alignment()
        circle_geom = window.geometry()
        circle_left_x = circle_geom.left()
        circle_right_x = circle_geom.right()
        
        reversed_dialogs = list(reversed(dialogs))
        
        for i, dialog in enumerate(reversed_dialogs):
            dialog_width = dialog.width()
            dialog_height = dialog.height()
            
            if h_alignment == 'left':
                x = circle_left_x
            else:
                x = circle_right_x - dialog_width
            
            if direction == 'below':
                y = circle_geom.bottom()
                for j in range(i):
                    y += reversed_dialogs[j].height() + DIALOG_GAP
            else:
                y = circle_geom.top()
                for j in range(i):
                    y -= reversed_dialogs[j].height() + DIALOG_GAP
                y -= dialog_height
            
            dialog.move(x, y)
    
    def show_key_dialog(key_str):
        nonlocal last_key_time, last_key_is_alphanum
        
        current_time = datetime.now()
        current_is_alphanum = is_alphanum_or_symbol(key_str)
        
        should_merge = False
        if dialogs and last_key_time is not None:
            time_diff = (current_time - last_key_time).total_seconds()
            if time_diff < 1.0 and last_key_is_alphanum and current_is_alphanum:
                should_merge = True
        
        if should_merge:
            latest_dialog = dialogs[-1]
            current_text = latest_dialog.label.text()
            new_text = current_text + key_str
            latest_dialog.set_text(new_text)
            latest_dialog.stop_destroy_timer()
            latest_dialog.start_destroy_timer(5)
            update_dialog_positions()
        else:
            direction = get_dialog_direction()
            
            for dialog in dialogs:
                if dialog.height() == DIALOG_HEIGHT_LARGE:
                    dialog.set_height(DIALOG_HEIGHT_SMALL)
                    dialog.set_to_old_style()
                    dialog.stop_destroy_timer()
                    dialog.start_destroy_timer(5)
            
            if len(dialogs) >= MAX_DIALOGS:
                oldest = dialogs.pop(0)
                oldest.hide()
                oldest.destroy()
            
            new_dialog = DialogWindow(key_str, DIALOG_HEIGHT_LARGE, is_latest=True)
            new_dialog.show()
            new_dialog.start_destroy_timer(5)
            dialogs.append(new_dialog)
            
            update_dialog_positions()
        
        last_key_time = current_time
        last_key_is_alphanum = current_is_alphanum
    
    def on_key_press(key_str):
        key_str = key_str.replace("Key.", "")
        add_log_history(f"[键盘按下] {key_str}", "#66ff66")
        if log_window.isVisible():
            log_window.append_log(f"[键盘按下] {key_str}", "#66ff66")
        show_key_dialog(key_str)
    
    def on_key_release(key_str):
        key_str = key_str.replace("Key.", "")
        add_log_history(f"[键盘释放] {key_str}", "#66ccff")
        if log_window.isVisible():
            log_window.append_log(f"[键盘释放] {key_str}", "#66ccff")
    
    def on_mouse_press(button, x, y):
        if button.startswith("release:"):
            button_name = button.replace("release:Button.", "")
            add_log_history(f"[鼠标释放] {button_name} (位置: {x}, {y})", "#ff9999")
            if log_window.isVisible():
                log_window.append_log(f"[鼠标释放] {button_name} (位置: {x}, {y})", "#ff9999")
        else:
            button_name = button.replace("Button.", "")
            add_log_history(f"[鼠标点击] {button_name} (位置: {x}, {y})", "#66ccff")
            if log_window.isVisible():
                log_window.append_log(f"[鼠标点击] {button_name} (位置: {x}, {y})", "#66ccff")
            if window.contains_global_point(int(x), int(y)):
                return
            show_key_dialog(f"[鼠标] {button_name}")
    
    def on_mouse_scroll(x, y, dx, dy):
        direction = "上滚" if int(dy) > 0 else "下滚"
        if int(dx) != 0:
            direction = "左滚" if int(dx) < 0 else "右滚"
        add_log_history(f"[鼠标滚轮] {direction} (位置: {x}, {y})", "#ff9966")
        if log_window.isVisible():
            log_window.append_log(f"[鼠标滚轮] {direction} (位置: {x}, {y})", "#ff9966")
        show_key_dialog(f"[滚轮] {direction}")
    
    monitor.key_pressed.connect(on_key_press)
    monitor.key_released.connect(on_key_release)
    monitor.mouse_pressed.connect(on_mouse_press)
    monitor.mouse_scrolled.connect(on_mouse_scroll)
    monitor.mouse_moved.connect(mouse_highlight.on_mouse_move)
    monitor.left_pressed.connect(mouse_highlight.on_left_press)
    monitor.left_released.connect(mouse_highlight.on_left_release)
    monitor.right_pressed.connect(mouse_highlight.on_right_press)
    monitor.right_released.connect(mouse_highlight.on_right_release)
    
    monitor.start()
    
    tray_icon = create_tray_icon(app, window, log_window)
    tray_icon.show()
    window.show()
    
    tooltip_window = ToolTipWindow()
    window.position_changed.connect(tooltip_window.close_tooltip)
    
    circle_geom = window.geometry()
    tooltip_width = tooltip_window.width()
    tooltip_height = tooltip_window.height()
    tooltip_x = circle_geom.center().x() - tooltip_width // 2
    tooltip_y = circle_geom.top() - tooltip_height - 10
    
    screen_geometry = QApplication.primaryScreen().geometry()
    tooltip_x = max(0, min(tooltip_x, screen_geometry.width() - tooltip_width))
    tooltip_y = max(0, min(tooltip_y, screen_geometry.height() - tooltip_height))
    
    tooltip_window.move(tooltip_x, tooltip_y)
    tooltip_window.show()
    
    exit_code = app.exec_()
    monitor.stop()
    for dialog in dialogs:
        dialog.hide()
        dialog.destroy()
    sys.exit(exit_code)
if __name__ == "__main__":
    main()
