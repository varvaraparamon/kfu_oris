import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 12345

clients_lock = threading.Lock()
clients = []  # сокеты
tasks_lock = threading.Lock()
tasks = []  # {"text":..,"priority":..,"completed": True/False}


def broadcast_tasks():
    payload = json.dumps(tasks, ensure_ascii=False) + "\n"
    with clients_lock:
        for conn in clients:
            try:
                conn.sendall(payload.encode('utf-8'))
            except Exception as e:
                print(f"[ОШИБКА] Не удалось отправить сообщение клиенту {conn}", e)

def handle_client(conn, addr):
    print(f"[НОВОЕ ПОДКЛЮЧЕНИЕ] {addr}")

    with clients_lock:
        clients.append(conn)
    
    buffer = ""
    broadcast_tasks()

    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break

            buffer += data

            lines = buffer.split("\n")
            buffer = lines.pop()   # оставляем последнюю линию на след цикл, тк могла придти не полная информация

            for line in lines:
                if not line.strip():
                    continue

                info = json.loads(line)
                action = info["action"]

                with tasks_lock:
                    if action == "add":
                        tasks.append({"text" : info["text"], "priority" : info["priority"], "completed" : False})

                    elif action == "delete":
                        idx = info["index"]
                        tasks.pop(idx)

                    elif action == "update":
                        idx = info["index"]
                        completed = info["completed"]
                        tasks[idx]["completed"] = completed

                broadcast_tasks()
    except Exception as e:
        print(f"[ОТКЛЮЧЕНИЕ] Клиент {addr} отключился")
        with clients_lock:
            if conn in clients:
                clients.remove(conn)

        conn.close()




        
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    with server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[СЕРВЕР ЗАПУЩЕН] {HOST}:{PORT}")
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
