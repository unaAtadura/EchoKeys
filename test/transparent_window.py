import sys
import logging
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont

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


class TransparentWindow(QWidget):
    def __init__(self):
        super().__init__()
        logger.debug("TransparentWindow.__init__ 开始")
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
        
        self.setWindowOpacity(0.6)
        logger.debug("窗口透明度设置: 0.6")
    
    def ensure_mouse_transparent(self):
        logger.debug("确保鼠标穿透属性已设置")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        logger.debug(f"WA_TransparentForMouseEvents: {self.testAttribute(Qt.WA_TransparentForMouseEvents)}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(100, 150, 255, 150)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor(50, 100, 200), 2))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        
        pen = QPen(QColor(255, 255, 255))
        painter.setPen(pen)
        font = QFont("Arial", 14, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, "半透明穿透窗口\n(鼠标可穿透到下层)")


def main():
    logger.info("程序主函数 main() 开始执行")
    app = QApplication(sys.argv)
    logger.debug("QApplication 创建完成")
    
    window = TransparentWindow()
    window.show()
    logger.info("窗口已显示")
    
    QTimer.singleShot(100, window.ensure_mouse_transparent)
    logger.info("已调度 ensure_mouse_transparent 定时器")
    
    try:
        exit_code = app.exec_()
        logger.info(f"事件循环结束，退出码: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
