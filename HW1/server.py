import socket
import threading
import pandas as pd
import time

HOST = '127.0.0.1'
PORT = 12345

clients = [] # список подключенных клиентов
clients_lock = threading.Lock() # сразу приготовили lock для того, чтобы изменять список АКТИВНЫХ клиентов
games = {}  # словарь для хранения игр: {player_name: {"opponent": opponent_name, "board": [...], "turn": "X", "last_move"}}

def inicialize_board():
    board = {
        'A' : {'1' : ' ', '2' : ' ', '3': ' '},
        'B' : {'1' : ' ', '2' : ' ', '3': ' '},
        'C' : {'1' : ' ', '2' : ' ', '3': ' '},
    }
    return board

def board_to_str(player_name, X_player):
    board = games[X_player]["board"]
    turn = games[X_player]["turn"]
    your_turn = "(Ход соперника)"
    if player_name == X_player:
        opponent = games[X_player]["opponent"]
        if turn == 'X':
            your_turn = "(Ваш ход!)"
    else:
        opponent = X_player
        if turn == 'O':
            your_turn = "(Ваш ход!)"
    
    output = f'''
    ╔═══════════════════╗
    ║  КРЕСТИКИ-НОЛИКИ  ║
    ╠═══════════════════╣
    ║     1   2   3     ║
    ║   ┌───┬───┬───┐   ║
    ║ A │ {board['A']['1']} │ {board['A']['2']} │ {board['A']['3']} │   ║
    ║   ├───┼───┼───┤   ║
    ║ B │ {board['B']['1']} │ {board['B']['2']} │ {board['B']['3']} │   ║
    ║   ├───┼───┼───┤   ║
    ║ C │ {board['C']['1']} │ {board['C']['2']} │ {board['C']['3']} │   ║
    ║   └───┴───┴───┘   ║
    ╚═══════════════════╝
    Ход: {turn} {your_turn}
    Соперник: {opponent}
Чат:  '''
    last_cell = games[X_player]['last_cell']
    if your_turn == "(Ваш ход!)" and last_cell is not None:
        output += f"\n[CЕРВЕР] : Противник сходил на {last_cell}"
    return output


# функция для отправки сообщения клиенту
def send_message(client, message):
    try:
        client.sendall(message.encode('utf-8'))
    except (ConnectionResetError, BrokenPipeError):
        print(f"[ОШИБКА] Не удалось отправить сообщение клиенту {client}")

def wait_for_opponent(player_name):
    while games[player_name]["opponent"] is None:
        time.sleep(0.1)

def find_opponent(conn, player_name):
    has_opponent = False
    X_player = None
    oponnent_name = None

    for player, game in games.items():
        if game["opponent"] is None:
            games[player]["opponent"] = player_name
            oponnent_name = player
            send_message(conn, f"OPPONENT - {player}")
            has_opponent = True
            X_player = player
            break

    if not has_opponent:
        games[player_name] = {"opponent": None, "board": inicialize_board(), "turn": "X", "last_cell" : None}
        send_message(conn, "Ждем подключения противника") 
        wait_for_opponent(player_name)
        send_message(conn, f"OPPONENT - {games[player_name]['opponent']}")
        oponnent_name = games[player_name]['opponent']
        X_player = player_name

    return X_player, oponnent_name

def game_end(conn, X_player, player_name):
    board = pd.DataFrame(games[X_player]['board'])
    is_win = False
    winner = None

    for i in range(board.shape[0]):
        if board.iloc[i, 0] != ' ' and \
                board.iloc[i, 1] == board.iloc[i, 0] and board.iloc[i, 2] == board.iloc[i, 0]:
            is_win = True
            winner = board.iloc[i, 0]
            break

    for j in range(board.shape[1]):
        if board.iloc[0, j] != ' ' and \
                board.iloc[1, j] == board.iloc[0, j] and board.iloc[2, j] == board.iloc[0, j]:
            is_win = True
            winner = board.iloc[0, j]
            break

    if board.iloc[0, 0] != ' ' and \
            board.iloc[0, 0] == board.iloc[1, 1] and board.iloc[0, 0] == board.iloc[2, 2]:
        is_win = True
        winner = board.iloc[0, 0]
    
    if board.iloc[0, 2] != ' ' and \
            board.iloc[0, 2] == board.iloc[1, 1] and board.iloc[0, 2] == board.iloc[2, 0]:
        is_win = True
        winner = board.iloc[0, 2]

    if is_win:
        return True, winner
    

    is_end = True
    for row_idx, cols in games[X_player]['board'].items():
        for col_idx, cell in cols.items():
            if cell == ' ':
                is_end = False
    
    return is_end, winner

def send_end(conn, winner, player_name, X_player):
    if winner is None:
        send_message(conn, "Игра закончена. Ничья :/")
    else:
        if (winner == 'X' and player_name == X_player) or \
                (winner == 'O' and X_player != player_name):
            send_message(conn, "Игра закончена. Вы выиграли! :)")
        else:
            send_message(conn, "Игра закончена. Вы проиграли :(")


def move(conn, X_player, player_name, cell):
    dict_ = {'X' : 'O', 'O' : 'X'}
    rows_idx = ('A', 'B', 'C')
    col_idx = ('1', '2', '3')
    turn = games[X_player]["turn"]
    row = cell[0]
    col = cell[1]

    with clients_lock:
        if len(cell) != 2 or row not in rows_idx or col not in col_idx:
            send_message(conn, f"Клетки {cell} на поле нет. Попробуйте еще раз")
        
        elif player_name == X_player and turn == 'O' or \
                player_name != X_player and turn == 'X':
            send_message(conn, "Не ваш ход!")
            
        elif games[X_player]["board"][row][col] == " ":
            games[X_player]["board"][row][col] = turn
            games[X_player]["turn"] = dict_[turn]
            games[X_player]['last_cell'] = cell
        else:
            send_message(conn, "Эта клетка уже занята!")

def send_board(conn, player_name, X_player):
    last_board = None

    while True:
        try:
            with clients_lock:
                board_view = board_to_str(player_name, X_player)

            if board_view != last_board :  
                send_message(conn, board_view)
                last_board = board_view

                is_end, winner = game_end(conn, X_player, player_name)
                if is_end:
                    time.sleep(1)
                    send_end(conn, winner, player_name, X_player)
                    break
                
            time.sleep(0.1)
        except:
            break

def handle_client(conn, addr):
    print(f"[НОВОЕ ПОДКЛЮЧЕНИЕ] {addr}")
    with clients_lock:
        clients.append(conn)  # добавляем клиента в общий список

    player_name = f"Player{addr[1]}"

    try:
        X_player, opponent_name = find_opponent(conn, player_name)

        opponent_conn = None
        with clients_lock:
            for client in clients:
                if f"Player{client.getpeername()[1]}" == opponent_name:
                    opponent_conn = client
                    break

        threading.Thread(target=send_board, args=(conn, player_name, X_player), daemon=True).start()

        while True:

            data = conn.recv(1024).decode('utf-8')

            # если клиент отключился, то на сервер придет b""
            if not data:
                print(f"[ОТКЛЮЧЕНИЕ] Клиент {addr} закрыл соединение")
                break

            if data.startswith("MOVE"):
                cell = data.split()[1]
                move(conn, X_player, player_name, cell)
                
            elif data.startswith("CHAT"):
                message_text = data[5:] 
                send_message(opponent_conn, f"[CHAT] {player_name}: {message_text}")

            elif data.startswith("STATUS"):
                turn = games[X_player]['turn']
                send_message(conn, f"Имя вашего соперника - {opponent_name}, сейчас ход {turn}")

            elif data.lower() == "exit":
                print(f"[ОТКЛЮЧЕНИЕ] Клиент {addr} вышел из игры")
                try:
                    send_message(opponent_conn, "Противник вышел из игры")
                except:
                    pass
                time.sleep(0.1)
                break
            else:
                send_message(conn, "НЕИЗВЕСТНАЯ КОМАНДА")
    except ConnectionResetError:
        print(f"[ОТКЛЮЧЕНИЕ] Клиент {addr} отключился некорректно")

    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)

        try:
            del games[X_player]
        except:
            pass

        conn.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    with server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER RUNNING] {HOST}:{PORT}")
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    start_server()
