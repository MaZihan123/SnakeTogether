# server.py
import socket
import threading
import pickle
import time
import pygame
from game_logic import Snake, Food, SCREEN_WIDTH, SCREEN_HEIGHT

BLOCK_SIZE = 20
NUM_PLAYERS = 2
directions = [pygame.K_RIGHT] * NUM_PLAYERS
players_connected = 0
scores = [0] * NUM_PLAYERS
usernames = ["Player1", "Player2"]

snake_list = [
    Snake(100, 300, pygame.K_RIGHT),
    Snake(700, 300, pygame.K_LEFT)
]
food = Food()

def send_with_header(conn, data_dict):
    body = pickle.dumps(data_dict)
    header = len(body).to_bytes(4, 'big')
    conn.sendall(header + body)

def recv_with_header(conn):
    try:
        header = conn.recv(4)
        if not header:
            return None
        length = int.from_bytes(header, 'big')
        body = b""
        while len(body) < length:
            chunk = conn.recv(length - len(body))
            if not chunk:
                return None
            body += chunk
        return pickle.loads(body)
    except:
        return None

def client_handler(conn, player_id):
    global directions, players_connected, usernames
    try:
        init_msg = recv_with_header(conn)
        if isinstance(init_msg, dict) and init_msg.get("type") == "init":
            usernames[player_id] = init_msg.get("username", f"Player{player_id+1}")
            print(f"Player {player_id} connected as: {usernames[player_id]}")
        else:
            print(f"Player {player_id} failed to send init info.")
    except Exception as e:
        print(f"Error receiving init from player {player_id}: {e}")
        conn.close()
        return

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            new_dir = pickle.loads(data)
            directions[player_id] = new_dir
        except:
            break
    conn.close()
    print(f"{usernames[player_id]} disconnected.")
    players_connected -= 1

def broadcast_game_state(conns):
    global snake_list, food, directions, scores
    clock = pygame.time.Clock()
    while True:
        clock.tick(10)
        ate = [False, False]

        for i, snake in enumerate(snake_list):
            snake.change_direction(directions[i])
            snake.move()

            if snake.body[0].colliderect(food.rect):
                tail = snake.body[-1].copy()
                snake.body.append(tail)
                scores[i] += 10
                food.refresh()
                ate[i] = True

            if snake.is_dead():
                print(f"{usernames[i]} died. Resetting game.")
                snake_list[0] = Snake(100,300,pygame.K_RIGHT)
                snake_list[1] = Snake(700,300,pygame.K_LEFT)
                scores[0], scores[1] = 0, 0
                food.refresh()
                ate = [False, False]

        game_state = {
            "snakes": [ [(node.x,node.y) for node in s.body] for s in snake_list ],
            "food": (food.rect.x, food.rect.y),
            "scores": scores,
            "ate": ate,
            "usernames": usernames
        }

        for c in conns:
            try:
                send_with_header(c, game_state)
            except:
                pass

def start_server():
    host = "0.0.0.0"
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(NUM_PLAYERS)

    print("Server listening on port:", port)
    conns = []
    global players_connected

    while players_connected < NUM_PLAYERS:
        conn, addr = server_socket.accept()
        print("Accepted connection from:", addr)
        player_id = players_connected
        players_connected += 1
        conns.append(conn)
        threading.Thread(target=client_handler, args=(conn, player_id), daemon=True).start()

    print("2 Players connected. Starting game.")
    broadcast_game_state(conns)

if __name__ == "__main__":
    start_server()