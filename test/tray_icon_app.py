import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                            QPushButton, QSystemTrayIcon, QMenu, QAction, QStyle)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class MainWindow(QWidget):
    def __init__(self, tray_icon):
        super().__init__()
        self.tray_icon = tray_icon
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("托盘程序")
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        label = QLabel("这是主窗口")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label)
        
        info_label = QLabel("点击关闭按钮或最小化按钮\n窗口将最小化到系统托盘")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: gray;")
        layout.addWidget(info_label)
        
        hide_button = QPushButton("最小化到托盘")
        hide_button.clicked.connect(self.hide_to_tray)
        layout.addWidget(hide_button)
        
        exit_button = QPushButton("退出程序")
        exit_button.clicked.connect(self.exit_app)
        layout.addWidget(exit_button)
        
        self.setLayout(layout)
    
    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "托盘程序",
                "程序已最小化到系统托盘",
                QSystemTrayIcon.Information,
                2000
            )
            event.ignore()
        else:
            event.accept()
    
    def hide_to_tray(self):
        self.hide()
        self.tray_icon.showMessage(
            "托盘程序",
            "程序已最小化到系统托盘",
            QSystemTrayIcon.Information,
            2000
        )
    
    def exit_app(self):
        self.tray_icon.hide()
        QApplication.quit()


def create_tray_icon(app, main_window):
    tray_icon = QSystemTrayIcon(app)
    
    icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
    tray_icon.setIcon(icon)
    tray_icon.setToolTip("托盘程序")
    
    menu = QMenu()
    
    show_action = QAction("显示窗口", app)
    show_action.triggered.connect(main_window.show)
    show_action.triggered.connect(main_window.raise_)
    show_action.triggered.connect(main_window.activateWindow)
    menu.addAction(show_action)
    
    hide_action = QAction("隐藏窗口", app)
    hide_action.triggered.connect(main_window.hide)
    menu.addAction(hide_action)
    
    menu.addSeparator()
    
    exit_action = QAction("退出", app)
    exit_action.triggered.connect(tray_icon.hide)
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)
    
    tray_icon.setContextMenu(menu)
    
    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.Trigger:
            if main_window.isVisible():
                main_window.hide()
            else:
                main_window.show()
                main_window.raise_()
                main_window.activateWindow()
    
    tray_icon.activated.connect(on_tray_activated)
    
    return tray_icon


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    main_window = MainWindow(None)
    
    tray_icon = create_tray_icon(app, main_window)
    main_window.tray_icon = tray_icon
    
    tray_icon.show()
    main_window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
