import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.click_count = 0

    def init_ui(self):
        self.setWindowTitle("PyQt5 示例程序")
        self.resize(400, 300)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        title_label = QLabel("Hello PyQt5!")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.counter_label = QLabel("按钮点击次数: 0")
        counter_font = QFont("Arial", 12)
        self.counter_label.setFont(counter_font)
        self.counter_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.counter_label)

        self.button = QPushButton("点击我")
        button_font = QFont("Arial", 14)
        self.button.setFont(button_font)
        self.button.clicked.connect(self.on_button_click)
        self.button.setMinimumHeight(40)
        layout.addWidget(self.button)

        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def on_button_click(self):
        self.click_count += 1
        self.counter_label.setText(f"按钮点击次数: {self.click_count}")
        self.status_label.setText(f"已点击 {self.click_count} 次")
        self.status_label.setStyleSheet("color: green;")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
