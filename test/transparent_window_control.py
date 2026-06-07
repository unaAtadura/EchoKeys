import sys
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                            QLabel, QHBoxLayout, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont, QIcon


LOG_FILE = r"d:\Workspace\Trae_Project\EchoKeys\test\debug.log"

def setup_logging():
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(f"=== Program Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()
logger.info("日志系统初始化完成")


class WindowController(QObject):
    show_window = pyqtSignal()
    hide_window = pyqtSignal()
    toggle_window = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._is_visible = False
    
    def show(self):
        logger.info("发送 show_window 信号")
        self._is_visible = True
        self.show_window.emit()
    
    def hide(self):
        logger.info("发送 hide_window 信号")
        self._is_visible = False
        self.hide_window.emit()
    
    def toggle(self):
        logger.info(f"发送 toggle_window 信号 (当前状态: {'显示' if self._is_visible else '隐藏'})")
        self._is_visible = not self._is_visible
        self.toggle_window.emit()
    
    @property
    def is_visible(self):
        return self._is_visible


class TransparentWindow(QWidget):
    def __init__(self):
        super().__init__()
        logger.debug("TransparentWindow.__init__ 开始")
        self._opacity = 0.6
        self.init_ui()
        logger.info("TransparentWindow 初始化完成")

    def init_ui(self):
        logger.debug("TransparentWindow.init_ui 开始")
        self.setWindowTitle("透明穿透窗口")
        self.resize(400, 300)
        logger.debug(f"窗口大小设置: 400x300")
        
        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput
        self.setWindowFlags(flags)
        logger.debug("窗口标志设置: FramelessWindowHint + WindowStaysOnTopHint + Tool + WindowTransparentForInput")
        
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        logger.debug("设置 WA_TranslucentBackground = True")
        
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        logger.debug("设置 WA_TransparentForMouseEvents = True (鼠标穿透)")
        
        self.setWindowOpacity(self._opacity)
        logger.debug(f"窗口透明度设置: {self._opacity}")
    
    def set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)
        logger.debug(f"窗口透明度已更新: {value}")
        self.update()
    
    def ensure_mouse_transparent(self):
        logger.debug("确保鼠标穿透属性已设置")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        logger.debug(f"WA_TransparentForMouseEvents: {self.testAttribute(Qt.WA_TransparentForMouseEvents)}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        alpha = int(255 * self._opacity * 0.8)
        color = QColor(100, 150, 255, alpha)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(50, 100, 200), 2))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        
        pen = QPen(QColor(255, 255, 255))
        painter.setPen(pen)
        font = QFont("Arial", 14, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, f"半透明穿透窗口\n透明度: {self._opacity:.1f}\n(鼠标可穿透到下层)")
    
    def on_show(self):
        logger.info("透明窗口: on_show 被调用")
        self.show()
        QTimer.singleShot(100, self.ensure_mouse_transparent)
    
    def on_hide(self):
        logger.info("透明窗口: on_hide 被调用")
        self.hide()
    
    def on_toggle(self):
        logger.info(f"透明窗口: on_toggle 被调用 (当前可见: {self.isVisible()})")
        if self.isVisible():
            self.hide()
        else:
            self.show()
            QTimer.singleShot(100, self.ensure_mouse_transparent)


class ControlWindow(QWidget):
    def __init__(self, controller, transparent_window):
        super().__init__()
        self.controller = controller
        self.transparent_window = transparent_window
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        self.setWindowTitle("透明窗口控制器")
        self.resize(350, 250)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("透明窗口控制器")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        self.status_label = QLabel("状态: 已隐藏")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        button_layout = QHBoxLayout()
        
        self.show_button = QPushButton("显示窗口")
        self.show_button.setMinimumHeight(40)
        self.show_button.clicked.connect(self.on_show_clicked)
        button_layout.addWidget(self.show_button)
        
        self.hide_button = QPushButton("隐藏窗口")
        self.hide_button.setMinimumHeight(40)
        self.hide_button.setEnabled(False)
        self.hide_button.clicked.connect(self.on_hide_clicked)
        button_layout.addWidget(self.hide_button)
        
        layout.addLayout(button_layout)
        
        self.toggle_button = QPushButton("切换显示/隐藏")
        self.toggle_button.setMinimumHeight(40)
        self.toggle_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.toggle_button.clicked.connect(self.on_toggle_clicked)
        layout.addWidget(self.toggle_button)
        
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("透明度:")
        opacity_layout.addWidget(opacity_label)
        
        self.opacity_spinbox = QSpinBox()
        self.opacity_spinbox.setRange(1, 10)
        self.opacity_spinbox.setValue(6)
        self.opacity_spinbox.setSuffix(" (0.1-1.0)")
        self.opacity_spinbox.valueChanged.connect(self.on_opacity_changed)
        opacity_layout.addWidget(self.opacity_spinbox)
        opacity_layout.addStretch()
        
        layout.addLayout(opacity_layout)
        
        self.setLayout(layout)
    
    def connect_signals(self):
        logger.debug("连接信号和槽")
        self.controller.show_window.connect(self.transparent_window.on_show)
        self.controller.hide_window.connect(self.transparent_window.on_hide)
        self.controller.toggle_window.connect(self.transparent_window.on_toggle)
    
    def on_show_clicked(self):
        logger.info("用户点击: 显示窗口按钮")
        self.controller.show()
        self.update_status(True)
    
    def on_hide_clicked(self):
        logger.info("用户点击: 隐藏窗口按钮")
        self.controller.hide()
        self.update_status(False)
    
    def on_toggle_clicked(self):
        logger.info("用户点击: 切换按钮")
        self.controller.toggle()
        self.update_status(self.controller.is_visible)
    
    def on_opacity_changed(self, value):
        opacity = value / 10.0
        logger.info(f"透明度改变: {opacity}")
        self.transparent_window.set_opacity(opacity)
    
    def update_status(self, visible):
        if visible:
            self.status_label.setText("状态: 已显示")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.show_button.setEnabled(False)
            self.hide_button.setEnabled(True)
        else:
            self.status_label.setText("状态: 已隐藏")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.show_button.setEnabled(True)
            self.hide_button.setEnabled(False)


def main():
    logger.info("程序主函数 main() 开始执行")
    app = QApplication(sys.argv)
    logger.debug("QApplication 创建完成")
    
    controller = WindowController()
    logger.debug("WindowController 创建完成")
    
    transparent_window = TransparentWindow()
    logger.debug("TransparentWindow 创建完成")
    
    control_window = ControlWindow(controller, transparent_window)
    logger.debug("ControlWindow 创建完成")
    
    control_window.show()
    logger.info("控制窗口已显示")
    
    try:
        exit_code = app.exec_()
        logger.info(f"事件循环结束，退出码: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
