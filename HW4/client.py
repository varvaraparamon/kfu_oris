import socket
import threading
import json
from PyQt6.QtCore import QObject, pyqtSignal

HOST = '127.0.0.1'
PORT = 12345

class MessengerClient(QObject):
    tasks_updated = pyqtSignal(list)
    nickname_received = pyqtSignal(str)

    def __init__(self, host=HOST, port=PORT, on_update=None):
        super().__init__() 
        self.host = host
        self.port = port
        self.on_update = on_update
        self.tasks = []
        self.socket = None
    
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        threading.Thread(target=self.listen_server, daemon=True).start()
    
    def listen_server(self):
        buffer = ""

        while True:
            try:
                data = self.socket.recv(1024).decode('utf-8')

                if not data:
                    break

                buffer += data
                lines = buffer.split('\n')
                buffer = lines.pop()

                for line in lines:
                    if not line.strip():
                        continue
                    msg = json.loads(line)

                    if isinstance(msg, dict) and "your_nickname" in msg:
                        self.nickname = msg["your_nickname"]
                        self.nickname_received.emit(self.nickname)
                        continue
                    elif isinstance(msg, list):
                        self.tasks = msg
                        self.tasks_updated.emit(self.tasks)

                    if self.on_update:
                        self.on_update()

            except Exception as e:
                print("[ОШИБКА ПОДКЛЮЧЕНИЯ]", e)
                break

    def send_command(self, command: dict):
        try:
            msg = json.dumps(command, ensure_ascii=False) + "\n"
            self.socket.sendall(msg.encode("utf-8"))
        except Exception as e:
            print("[ОШИБКА ОТПРАВКИ]", e)