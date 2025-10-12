import socket
import threading
import os
import time

# у нас будет два потока:
# первый поток (наш основной поток) - ввода команд пользователем
# второй поток (мы его создали дополнительно) - прием сообщений от сервера и отображение доски, чата и результатов игры

HOST = '127.0.0.1'
PORT = 12345

# функция для приёма сообщений от сервера
def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            if not data:
                print("[ОТКЛЮЧЕНИЕ] Сервер закрыл соединение")
                break

            if "КРЕСТИКИ-НОЛИКИ" in data:
                os.system('cls' if os.name == 'nt' else 'clear')

            print("\n[СЕРВЕР]:", data, "\nВведите команду: ", end="")

        except ConnectionResetError:
            print("[ОТКЛЮЧЕНИЕ] Соединение разорвано сервером")
            break

# основная функция клиента
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    with client_socket:
        client_socket.connect((HOST, PORT))
        print("[ПОДКЛЮЧЕНИЕ] Подключено к серверу")

        # поток для приёма сообщений от сервера
        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

        # основной поток для ввода команд пользователем
        while True:
            command = input("Введите команду (MOVE, CHAT, STATUS, exit): ").strip()
            if command.lower() == "exit":
                time.sleep(0.5)
                client_socket.sendall("exit".encode('utf-8'))
                print("[ВЫХОД] Вы отключились от сервера")
                break

            client_socket.sendall(command.encode('utf-8'))

if __name__ == "__main__":
    start_client()
