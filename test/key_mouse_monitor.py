import sys
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                            QTextEdit, QPushButton, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QTextCursor, QCloseEvent
from pynput import keyboard, mouse


class SignalBridge(QObject):
    key_pressed = pyqtSignal(str)
    key_released = pyqtSignal(str)
    mouse_pressed = pyqtSignal(str, str, str)
    mouse_scrolled = pyqtSignal(str, str, str, str)


class MonitorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.signal_bridge = SignalBridge()
        self.is_monitoring = False
        self.keyboard_listener = None
        self.mouse_listener = None
        self.pressed_keys = {}
        self.key_repeat_counts = {}
        
        self.signal_bridge.key_pressed.connect(self.on_key_down)
        self.signal_bridge.key_released.connect(self.on_key_up)
        self.signal_bridge.mouse_pressed.connect(self.on_mouse_pressed)
        self.signal_bridge.mouse_scrolled.connect(self.on_mouse_scrolled)
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("键鼠监听器")
        self.resize(600, 550)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("键盘鼠标监听器")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        self.status_label = QLabel("状态: 已停止")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        info_layout = QHBoxLayout()
        
        self.current_key_label = QLabel("当前按键: 无")
        self.current_key_label.setAlignment(Qt.AlignCenter)
        self.current_key_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3;")
        info_layout.addWidget(self.current_key_label)
        
        self.repeat_count_label = QLabel("重复次数: 0")
        self.repeat_count_label.setAlignment(Qt.AlignCenter)
        self.repeat_count_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        info_layout.addWidget(self.repeat_count_label)
        
        layout.addLayout(info_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(self.log_text)
        
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("开始监听")
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.start_button.clicked.connect(self.start_monitoring)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("停止监听")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.stop_button.clicked.connect(self.stop_monitoring)
        button_layout.addWidget(self.stop_button)
        
        self.clear_button = QPushButton("清空日志")
        self.clear_button.setMinimumHeight(40)
        self.clear_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        info_label = QLabel("注意：此程序仅在应用窗口内显示按键信息，点击'开始监听'按钮后开始监听")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info_label)
        
        self.setLayout(layout)
        
        self.append_log("程序已启动，点击'开始监听'按钮开始")
    
    def append_log(self, message, color="#d4d4d4"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_text.append(f'<span style="color: #888888;">[{timestamp}]</span> <span style="color: {color};">{message}</span>')
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def start_monitoring(self):
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.pressed_keys.clear()
        self.key_repeat_counts.clear()
        self.current_key_label.setText("当前按键: 无")
        self.repeat_count_label.setText("重复次数: 0")
        
        self.status_label.setText("状态: 监听中")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.append_log("=" * 50, "#ffd700")
        self.append_log("开始监听键盘和鼠标事件", "#4CAF50")
        self.append_log("=" * 50, "#ffd700")
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_keyboard_press,
            on_release=self.on_keyboard_release
        )
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click, on_scroll=self.on_mouse_scroll_callback)
        
        self.keyboard_listener.start()
        self.mouse_listener.start()
    
    def stop_monitoring(self):
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        self.status_label.setText("状态: 已停止")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        self.append_log("=" * 50, "#ffd700")
        self.append_log("已停止监听", "#f44336")
        self.append_log("=" * 50, "#ffd700")
    
    def clear_log(self):
        self.log_text.clear()
        self.pressed_keys.clear()
        self.key_repeat_counts.clear()
        self.current_key_label.setText("当前按键: 无")
        self.repeat_count_label.setText("重复次数: 0")
        self.append_log("日志已清空")
    
    def on_keyboard_press(self, key):
        try:
            key_str = self.format_key(key)
            self.signal_bridge.key_pressed.emit(key_str)
        except Exception as e:
            print(f"Key error: {e}")
    
    def on_keyboard_release(self, key):
        try:
            key_str = self.format_key(key)
            self.signal_bridge.key_released.emit(key_str)
        except Exception as e:
            print(f"Key release error: {e}")
    
    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            try:
                self.signal_bridge.mouse_pressed.emit(str(button), str(x), str(y))
            except Exception as e:
                print(f"Mouse error: {e}")
    
    def on_mouse_scroll_callback(self, x, y, dx, dy):
        try:
            self.signal_bridge.mouse_scrolled.emit(str(x), str(y), str(dx), str(dy))
        except Exception as e:
            print(f"Scroll error: {e}")
    
    def format_key(self, key):
        if hasattr(key, 'name'):
            return f"Key.{key.name}"
        elif hasattr(key, 'vk'):
            vk = key.vk
            if 96 <= vk <= 105:
                return f"NumPad {vk - 96}"
            elif vk == 110:
                return "NumPad ."
            elif vk == 106:
                return "NumPad *"
            elif vk == 107:
                return "NumPad +"
            elif vk == 109:
                return "NumPad -"
            elif vk == 111:
                return "NumPad /"
            elif hasattr(key, 'char') and key.char:
                return key.char
            else:
                return f"VK:{vk}"
        elif hasattr(key, 'char') and key.char:
            return key.char
        else:
            return str(key)
    
    def on_key_down(self, key_str):
        key_str = key_str.replace("Key.", "")
        
        if key_str in self.pressed_keys and self.pressed_keys[key_str]:
            if key_str not in self.key_repeat_counts:
                self.key_repeat_counts[key_str] = 0
            
            self.key_repeat_counts[key_str] += 1
            count = self.key_repeat_counts[key_str]
            
            self.current_key_label.setText(f"当前按键: {key_str}")
            self.repeat_count_label.setText(f"重复次数: {count}")
            
            if count == 1:
                self.append_log(f"[长按开始] {key_str} - 开始计数", "#ff9900")
            else:
                self.append_log(f"[重复 #{count}] {key_str}", "#ffcc00")
        else:
            self.pressed_keys[key_str] = True
            self.current_key_label.setText(f"当前按键: {key_str}")
            self.append_log(f"[键盘] {key_str}", "#66ff66")
    
    def on_key_up(self, key_str):
        key_str = key_str.replace("Key.", "")
        
        if key_str in self.pressed_keys:
            self.pressed_keys[key_str] = False
            repeat_count = self.key_repeat_counts.get(key_str, 0)
            
            if repeat_count > 0:
                self.append_log(f"[释放] {key_str} - 共重复 {repeat_count} 次", "#66ccff")
            else:
                self.append_log(f"[释放] {key_str} - 无重复（短按）", "#66ccff")
            
            if self.current_key_label.text() == f"当前按键: {key_str}":
                self.current_key_label.setText("当前按键: 无")
                self.repeat_count_label.setText("重复次数: 0")
    
    def on_mouse_pressed(self, button, x, y):
        button_name = button.replace("Button.", "")
        self.append_log(f"[鼠标] {button_name} 点击 (位置: {x}, {y})", "#66ccff")
    
    def on_mouse_scrolled(self, x, y, dx, dy):
        direction = "上滚" if int(dy) > 0 else "下滚"
        if int(dx) != 0:
            direction = "左滚" if int(dx) < 0 else "右滚"
        self.append_log(f"[鼠标] 滚轮{direction} (位置: {x}, {y})", "#ff9966")
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.is_monitoring:
                self.stop_monitoring()
            else:
                self.start_monitoring()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.is_monitoring:
                self.stop_monitoring()
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MonitorWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
