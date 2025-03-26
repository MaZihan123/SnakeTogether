# server.py
import socket
import threading
import pickle
import time
import pygame
import random
from game_logic import Snake, Food, SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()
BLOCK_SIZE = 20
MAX_PLAYERS = 9

NUM_PLAYERS = 2
directions = []
snake_list = []
scores = []
usernames = []
connections = []

players_connected = 0
food_list = []
self_deaths = set()

game_started = False
game_over = False
winner = None
end_reason = ""
start_time = None
countdown = 3

def send_with_header(conn, data_dict):
    body = pickle.dumps(data_dict)
    header = len(body).to_bytes(4, 'big')
    conn.sendall(header + body)

def recv_with_header(conn):
    try:
        header = conn.recv(4)
        if not header: return None
        length = int.from_bytes(header, 'big')
        body = b''
        while len(body) < length:
            chunk = conn.recv(length - len(body))
            if not chunk: return None
            body += chunk
        return pickle.loads(body)
    except:
        return None

def init_game_state(num):
    global directions, snake_list, scores, usernames, food_list, self_deaths
    directions = [pygame.K_RIGHT] * num
    scores = [0] * num
    usernames = [f"Player{i+1}" for i in range(num)]
    snake_list.clear()
    self_deaths.clear()

    for _ in range(num):
        x = random.randint(100, SCREEN_WIDTH - 100)
        y = random.randint(100, SCREEN_HEIGHT - 100)
        dir = random.choice([pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN])
        snake = Snake(x, y, dir)
        snake_list.append(snake)

    food_list = [Food() for _ in range(max(1, num - 1))]

def client_handler(conn, player_id):
    global players_connected, usernames

    try:
        init_msg = recv_with_header(conn)
        if isinstance(init_msg, dict) and init_msg.get("type") == "init":
            if player_id == 0:
                global NUM_PLAYERS
                requested = init_msg.get("requested_mode", 2)
                NUM_PLAYERS = max(2, min(9, requested))
                print(f"游戏设置为 {NUM_PLAYERS} 人模式")
                init_game_state(NUM_PLAYERS)

            usernames[player_id] = init_msg.get("username", f"Player{player_id+1}")
            print(f"玩家 {player_id + 1} 加入游戏：{usernames[player_id]}")
        else:
            print("接收初始化失败")
            conn.close()
            return
    except Exception as e:
        print("初始化异常：", e)
        conn.close()
        return

    while True:
        try:
            data = conn.recv(1024)
            if not data: break
            new_dir = pickle.loads(data)
            directions[player_id] = new_dir
        except:
            break

    print(f"{usernames[player_id]} 已断开连接")
    conn.close()
    players_connected -= 1

def broadcast_waiting_status():
    while players_connected < NUM_PLAYERS:
        game_state = {
            "countdown": -1,
            "connected": players_connected,
            "expected": NUM_PLAYERS,
        }
        for conn in connections:
            try:
                send_with_header(conn, game_state)
            except:
                pass
        time.sleep(0.5)

def broadcast_game_state():
    global game_started, countdown, start_time
    global game_over, winner, end_reason

    clock = pygame.time.Clock()
    countdown_start = time.time()

    while True:
        clock.tick(10)
        now = time.time()

        if not game_started:
            elapsed = int(now - countdown_start)
            countdown = max(0, 3 - elapsed)
            if countdown == 0:
                game_started = True
                start_time = now

        elif not game_over:
            ate = [False] * NUM_PLAYERS

            # ✅ 检查撞到自己
            for i, snake in enumerate(snake_list):
                if i not in self_deaths and snake.body[0] in snake.body[1:]:
                    self_deaths.add(i)

            # 移动 + 吃食物
            for i, snake in enumerate(snake_list):
                if i in self_deaths:
                    continue

                snake.change_direction(directions[i])
                snake.move()

                for food in food_list:
                    if snake.body[0].colliderect(food.rect):
                        tail = snake.body[-1].copy()
                        snake.body.append(tail)
                        scores[i] += 10
                        food.refresh()
                        ate[i] = True
                        break

            # 游戏是否结束：所有人都死 or 时间到
            alive = [i for i in range(NUM_PLAYERS) if i not in self_deaths]
            if len(alive) == 0:
                game_over = True
                end_reason = "所有玩家均已撞到自己"
                winner = -1
            elif now - start_time >= 120:
                game_over = True
                max_score = max(scores)
                win_list = [i for i, s in enumerate(scores) if s == max_score]
                if len(win_list) == 1:
                    winner = win_list[0]
                    end_reason = "时间到，分数最高"
                else:
                    winner = -1
                    end_reason = "时间到，平局"

        # 🧠 构建游戏状态
        game_state = {
            "snakes": [[(b.x, b.y) for b in s.body] if i not in self_deaths else [] for i, s in enumerate(snake_list)],
            "foods": [(f.rect.x, f.rect.y) for f in food_list],
            "scores": scores,
            "ate": ate if game_started and not game_over else [False] * NUM_PLAYERS,
            "usernames": usernames,
            "countdown": countdown if not game_started else 0,
            "winner": winner,
            "end_reason": end_reason,
            "self_deaths": list(self_deaths),
        }

        for conn in connections:
            try:
                send_with_header(conn, game_state)
            except:
                pass

        if game_over:
            print("游戏结束：", end_reason)
            break

def start_server():
    global players_connected

    host = "192.168.1.119"
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(MAX_PLAYERS)

    print("服务器启动，等待玩家连接...")

    conn, addr = server_socket.accept()
    print(f"首位玩家连接：{addr}")
    connections.append(conn)
    usernames.append("Player1")
    players_connected += 1
    threading.Thread(target=client_handler, args=(conn, 0), daemon=True).start()

    time.sleep(0.5)
    threading.Thread(target=broadcast_waiting_status, daemon=True).start()

    while players_connected < NUM_PLAYERS:
        conn, addr = server_socket.accept()
        print(f"玩家连接：{addr}")
        player_id = players_connected
        connections.append(conn)
        usernames.append(f"Player{player_id + 1}")
        players_connected += 1
        threading.Thread(target=client_handler, args=(conn, player_id), daemon=True).start()

    print(f"{NUM_PLAYERS} 名玩家已连接，开始游戏倒计时...")
    broadcast_game_state()

if __name__ == "__main__":
    start_server()
