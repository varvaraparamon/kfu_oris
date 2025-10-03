# Импортируем библиотеку для работы с сокетами
import socket

# Создаём TCP-сокет
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Подключаемся к серверу
client_socket.connect(('localhost', 5555))
print("Подключились к серверу")

# Цикл диалога
while True:
    # Отправляем сообщение серверу
    client_message = input("Введите сообщение для сервера: ")
    client_socket.send(client_message.encode('utf-8'))

    if client_message.lower() == '/exit':
        print("Завершаем диалог")
        break

    data = client_socket.recv(1024)
    server_response = data.decode('utf-8')

    while server_response != "End":
        print(server_response)
        data = client_socket.recv(1024)
        server_response = data.decode('utf-8')     



# Закрываем сокет
client_socket.close()