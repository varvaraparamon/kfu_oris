import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QApplication, QPushButton, \
    QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QMessageBox, \
    QScrollArea, QMainWindow, QTextEdit, QSplitter

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFontMetrics
from client import MessengerClient


class MessageLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setWordWrap(True)
        self.setStyleSheet("background:#f0f0f0; padding:6px; border-radius:5px;")

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        lines = fm.boundingRect(0, 0, self.width(), 10000, Qt.TextFlag.TextWordWrap, self.text())
        return QSize(self.width(), lines.height() + 12)


class ChatWindow(QScrollArea):
    def __init__(self):
        super().__init__()
        container = QWidget()
        self.setWidget(container)
        self.setWidgetResizable(True)

        self.layout = QVBoxLayout(container)
        self.layout.addStretch()

    def add_message(self, html):
        label = MessageLabel(html)
        self.layout.insertWidget(self.layout.count() - 1, label)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def clear_messages(self):
        for i in range(self.layout.count() - 1, -1, -1):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.nickname = None
        self.resize(500, 500)

        self.chat = ChatWindow()
        self.input = QTextEdit()
        self.input.setPlaceholderText("Введите сообщение...")

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.addWidget(self.chat)
        self.splitter.addWidget(self.input)
        self.splitter.setSizes([400, 100])

        send_btn = QPushButton("Отправить")
        send_btn.clicked.connect(self.send_message)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.splitter)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(send_btn)

        main_layout.addLayout(btn_layout)

        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.client = MessengerClient()
        self.client.tasks_updated.connect(self.update_messages)
        self.client.nickname_received.connect(self.set_nickname)
        self.client.connect()

    def send_message(self):
        text = self.input.toPlainText().strip()
        if not text:
            return

        self.client.send_command({"nickname": self.nickname, "text": text})
        self.input.clear()

    def update_messages(self, tasks):
        self.chat.clear_messages()
        for msg in tasks:
            nickname = msg.get("nickname", "??")
            text = msg.get("text", "").replace("\n", "<br>")

            if nickname == self.nickname:
                html = f"<b>Вы:</b> {text}"
            else:
                html = f"<b>{nickname}:</b> {text}"

            self.chat.add_message(html)

    def set_nickname(self, nick):
        self.nickname = nick
        print("Ник получен:", nick)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
