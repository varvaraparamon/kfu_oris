import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

clients = {}  # {conn: player_name}
rooms = {}    # {room_name: [conn1, conn2, ...]}

client_counter_lock = threading.Lock()  # для безопасного подсчета клиентов
input_lock = threading.Lock()  # для защиты ввода с консоли
client_counter = 1

def send_message(conn, message, current_room=None):
    try:
        conn.sendall(message.encode('utf-8'))
    except ConnectionResetError:
        print(f"[ОШИБКА] Не удалось отправить сообщение клиенту {conn}")
        if conn in clients:
            del clients[conn]
        leave_room(conn, current_room)
        # TODO: удалить клиента из rooms и clients при ошибке

def leave_room(conn, current_room):
    if current_room and conn in rooms[current_room]:
        rooms[current_room].remove(conn)

def handle_client(conn, addr):
    print(f"[НОВОЕ ПОДКЛЮЧЕНИЕ] {addr}")
    clients[conn] = f"Player{addr[1]}"

    current_room = None
    
    try:
        send_message(conn, "Добро пожаловать! Введите команду или сообщение:", current_room)

        while True:
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break

            input_lock.acquire()

            if data.startswith("/join"):
                room_name = data.split(maxsplit=1)[1]
                # TODO: выйти из старой комнаты, если есть
                leave_room(conn, current_room)
                # TODO: добавить в новую комнату
                if room_name not in rooms:
                    rooms[room_name] = []
                rooms[room_name].append(conn)
                current_room = room_name

                print(rooms)

                send_message(conn, f"Вы вошли в комнату {room_name}", current_room)

            elif data.startswith("/leave"):
                # TODO: удалить из текущей комнаты
                leave_room(conn, current_room)
                current_room = None
                send_message(conn, "Вы покинули комнату", current_room)

            elif data.startswith("/list"):
                msg = "Комнаты:\n"
                for room, participants in rooms.items():
                    names = [clients[c] for c in participants]
                    msg += f"{room}: {', '.join(names)}\n"
                send_message(conn, msg, current_room)

            else:
                # TODO: отправить текст только участникам current_room
                if current_room:
                    for user in rooms[current_room]:
                        if user == conn:
                            continue
                        send_message(user, f"{clients[conn]}: {data}", current_room)
                    send_message(conn, f"Вы: {data}", current_room)
                else:
                    send_message(conn, "Вы не в комнате. Сначала войдите с помощью /join", current_room)
                
            input_lock.release()

    except ConnectionResetError:
        print(f"[ОТКЛЮЧЕНИЕ] Клиент {addr} отключился")
    finally:
        if conn in clients:
            del clients[conn]
        # TODO: удалить из комнаты
        leave_room(conn, current_room)

        conn.close()

def start_server():
    global client_counter

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    with server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[СЕРВЕР ЗАПУЩЕН] {HOST}:{PORT}")
        while True:
            client_counter_lock.acquire()
            try:
                current_client_id = client_counter
                client_counter += 1
            finally:
                client_counter_lock.release()

            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
