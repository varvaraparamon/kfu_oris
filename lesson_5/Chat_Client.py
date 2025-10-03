import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

def handle_input(client_socket):
    while True:
        # Получаем сообщения от сервера (если есть)
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print("\n[СЕРВЕР]:", data)
        except ConnectionResetError:
            print("[ОТКЛЮЧЕНИЕ] Соединение разорвано сервером")
            break

def handle_send(client_socket):
    while True:
        # Ввод команды/сообщения пользователем
        cmd = input().strip()
        if cmd.lower() == "exit":
            client_socket.sendall("exit".encode('utf-8'))
            print("[ВЫХОД] Вы отключились от сервера")
            break

        client_socket.sendall(cmd.encode('utf-8'))

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   
    client_socket.connect((HOST, PORT))
    print("[ПОДКЛЮЧЕНИЕ] Подключено к серверу")

    t2 = threading.Thread(target=handle_send, args=(client_socket, ))
    t1 = threading.Thread(target=handle_input, args=(client_socket, ))

    t1.start()
    t2.start()

    t2.join()
    client_socket.close()
    t1.join()



if __name__ == "__main__":
    start_client()
