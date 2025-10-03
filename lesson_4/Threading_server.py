import socket
import threading
import time

def get(command, client_socket):
    try:
        filename = command[1]
        server_response = f"Сервер начинает читать файл {filename}\n"
        client_socket.send(server_response.encode('utf-8'))
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                client_socket.send(line.encode('utf-8'))

    except Exception as e:
        server_response = f"Возникла ошибка {e}\n"
        client_socket.send(server_response.encode('utf-8'))

    server_response = "Чтение файла завершено. Отправьте новую команду\n"
    client_socket.send(server_response.encode('utf-8'))
    
def lines(command, client_socket):
    try:
        filename = command[1]
        server_response = f"Сервер начинает считать строки в {filename}\n"
        client_socket.send(server_response.encode('utf-8'))
        count = 0
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                count += 1
        server_response = f"В файле {count} строк\n"
        client_socket.send(server_response.encode('utf-8'))

    except Exception as e:
        server_response = f"Возникла ошибка {e}\n"
        client_socket.send(server_response.encode('utf-8'))

    server_response = "Подсчет завершен. Отправьте новую команду\n"
    client_socket.send(server_response.encode('utf-8'))

def words(command, client_socket):
    try:
        filename = command[1]
        server_response = f"Сервер начинает считать слова в {filename}\n"
        client_socket.send(server_response.encode('utf-8'))
        count = 0
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                count += len(line.strip().split())
        server_response = f"В файле {count} слов\n"
        client_socket.send(server_response.encode('utf-8'))

    except Exception as e:
        server_response = f"Возникла ошибка {e}\n"
        client_socket.send(server_response.encode('utf-8'))

    server_response = "Подсчет завершен. Отправьте новую команду\n"
    client_socket.send(server_response.encode('utf-8'))


def handle_client(client_socket, client_address, client_id):
    print(f"Подключился клиент {client_id} с адресом: {client_address}")

    while True:
        data = client_socket.recv(1024)
        client_message = data.decode('utf-8')

        if client_message.lower() == '/exit':
            print(f"Клиент {client_id} завершил диалог")
            break
        if not data:
            continue

        command = client_message.strip().split()

        if command[0] == '/get':
            get(command, client_socket)
        elif command[0] == '/lines':
            lines(command, client_socket)
        elif command[0] == '/words':
            words(command, client_socket)
        else:
            server_response = "Неверная команда. /get <filename> | /lines <filename> | /words <filename> | /exit"
            client_socket.send(server_response.encode('utf-8'))
        time.sleep(1)
        server_response = "End"
        client_socket.send(server_response.encode('utf-8'))


    client_socket.close()
    print(f"Соединение с клиентом {client_id} закрыто")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

PORT = 5555

server_socket.bind(('localhost', PORT))

server_socket.listen(5)
print(f"Сервер запущен. Жду подключения")

client_counter = 1
while True:
    print(f"\nЖду клиента {client_counter}")

    client_socket, client_address = server_socket.accept()

    client_thread = threading.Thread(
        target=handle_client,
        args=(client_socket, client_address, client_counter)
    )
    client_thread.start()

    print(f"Запущен поток для клиента {client_counter}")
    client_counter += 1