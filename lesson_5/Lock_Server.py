import socket
import threading

# создаем Lock для защиты общих ресурсов
client_counter_lock = threading.Lock()  # для безопасного подсчета клиентов
input_lock = threading.Lock()  # для защиты ввода с консоли
client_counter = 1

# обрабатываем одного клиента
def handle_client(client_socket, client_address, client_id):
    print(f"Подключился клиент {client_id} с адресом: {client_address}")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            client_message = data.decode('utf-8')

            # захватываем Lock сразу после получения сообщения
            input_lock.acquire()
            try:
                print(f"\nКлиент {client_id} сказал: {client_message}")

                if client_message.lower() == 'exit':
                    print(f"Клиент {client_id} завершил диалог")
                    break

                server_response = input(f"Введите ответ для клиента {client_id}: ")

                client_socket.send(server_response.encode('utf-8'))

                if server_response.lower() == 'exit':
                    print(f"Сервер завершил диалог с клиентом {client_id}")
                    break
            finally:
                # освобождаем блокировку в любом случае
                input_lock.release()

    except Exception as e:
        print(f"Ошибка с клиентом {client_id}: {e}")
    finally:
        client_socket.close()
        print(f"Соединение с клиентом {client_id} закрыто")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

PORT = 5555

server_socket.bind(('localhost', PORT))

server_socket.listen(5)
print(f"Сервер запущен. Жду подключения")

while True:
    print(f"\nЖду нового клиента...")

    client_socket, client_address = server_socket.accept()

    # захватываем блокировку для счетчика клиентов
    client_counter_lock.acquire()
    try:
        current_client_id = client_counter
        client_counter += 1
    finally:
        # освобождаем блокировку в любом случае
        client_counter_lock.release()

    print(f"Принято подключение от {client_address}, назначаем ID: {current_client_id}")

    client_thread = threading.Thread(
        target=handle_client,
        args=(client_socket, client_address, current_client_id)
    )
    client_thread.start()

    print(f"Запущен поток для клиента {current_client_id}")