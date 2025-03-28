# server.py
import socket
import threading
import pickle
import time
import pygame
import random
from game_logic import Snake, Food, SCREEN_WIDTH, SCREEN_HEIGHT
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)



pygame.init()
BLOCK_SIZE = 20
MAX_PLAYERS = 9
NUM_PLAYERS = None  # 默认模式，后续由客户端传来控制


death_reasons = {}  # key: player_id, value: 死亡原因字符串
snake_list = []
# directions = []
# scores = []
# usernames = []
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
font_path = resource_path("assets/fontEND.ttf")

directions = [pygame.K_RIGHT] * MAX_PLAYERS
scores = [0] * MAX_PLAYERS
usernames = [None] * MAX_PLAYERS


def recvall(conn, n):
    data = b''
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

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
    snake_list.clear()
    self_deaths.clear()

    # 初始化蛇
    for _ in range(num):
        x = random.randint(100, SCREEN_WIDTH - 100)
        y = random.randint(100, SCREEN_HEIGHT - 100)
        dir = random.choice([pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN])
        snake = Snake(x, y, dir)
        snake_list.append(snake)

    #打印状态
    for idx, snake in enumerate(snake_list):
        print(f"🐍 蛇{idx + 1} 初始方向: {snake.direction}")
        print(f"🐍 蛇{idx + 1} 身体: {[(b.x, b.y) for b in snake.body]}")

    food_list = [Food() for _ in range(max(1, num - 1))]

def client_handler(conn, player_id):
    global players_connected, usernames, NUM_PLAYERS

    try:
        # 📨 接收初始信息（用户名、请求的玩家总数）
        header = recvall(conn, 4)
        if not header:
            return
        length = int.from_bytes(header, 'big')
        body = recvall(conn, length)
        init_msg = pickle.loads(body)

        if isinstance(init_msg, dict) and init_msg.get("type") == "init":
            username = init_msg.get("username", f"Player{player_id + 1}")
            usernames[player_id] = username
            print(f"玩家 {player_id + 1} 加入游戏：{username}")

            # 第一个玩家设置玩家总数
            if player_id == 0 and "requested_mode" in init_msg:
                NUM_PLAYERS = int(init_msg["requested_mode"])
                print(f"设置本局玩家人数为：{NUM_PLAYERS}")

    except Exception as e:
        print(f"处理玩家 {player_id + 1} 时出错:", e)

    # 🎮 接收方向输入
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
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

        if game_started and not game_over:
            ate = [False] * NUM_PLAYERS

            # ✅ 1. 检查撞到自己
            if game_started and not game_over and (time.time() - start_time) > 0.3:
                # ✅ 撞到自己
                for i, snake in enumerate(snake_list):
                    if i not in self_deaths and snake.body[0] in snake.body[1:]:
                        self_deaths.add(i)
                        death_reasons[i] = "self"
                        print(f"玩家{i + 1} 撞到了自己的身体！")

                # ✅ 撞到其他蛇
                for i, snake in enumerate(snake_list):
                    if i in self_deaths:
                        continue
                    head = snake.body[0]
                    for j, other_snake in enumerate(snake_list):
                        if j == i or j in self_deaths:
                            continue
                        if any(head.colliderect(seg) for seg in other_snake.body):
                            self_deaths.add(i)
                            death_reasons[i] = f"撞到了玩家{j + 1} 的身体"
                            print(f"玩家{i + 1} 撞到了玩家{j + 1} 的身体！")
                            break

            # ✅ 3. 移动蛇并检查食物
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

            # ✅ 4. 游戏结束判断
            alive = [i for i in range(NUM_PLAYERS) if i not in self_deaths]
            if len(alive) == 0:
                game_over = True
                winner = -1
                end_reason = "所有玩家均已撞到自己或其他人"
            elif now - start_time >= 120:
                game_over = True
                max_score = max(scores)
                win_list = [i for i, s in enumerate(scores) if s == max_score]
                if len(win_list) == 1:
                    winner = win_list[0]
                    end_reason = "时间到，分数最高者胜出"
                else:
                    winner = -1
                    end_reason = "时间到，平局"

        # ✅ 构造并广播游戏状态
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
            "death_reasons": death_reasons,  # ✅ 发送死亡原因到客户端

        }

        for conn in connections:
            try:
                send_with_header(conn, game_state)
            except:
                pass

        # ✅ 游戏结束后重置状态
        if game_over:
            print("游戏结束：", end_reason)
            time.sleep(5)
            init_game_state(NUM_PLAYERS)
            game_started = False
            game_over = False
            countdown_start = time.time()
            winner = None
            end_reason = ""
            death_reasons.clear()

def start_server():
    global players_connected

    host = "192.168.1.106"
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(MAX_PLAYERS)

    print("服务器启动，等待玩家连接...")

    time.sleep(0.5)
    threading.Thread(target=broadcast_waiting_status, daemon=True).start()

    while players_connected < NUM_PLAYERS:
        conn, addr = server_socket.accept()
        print(f"玩家连接：{addr}")
        player_id = players_connected
        connections.append(conn)
        usernames.append(f"Player{player_id + 1}")
        threading.Thread(target=client_handler, args=(conn, player_id), daemon=True).start()
        players_connected += 1

    print(f"{NUM_PLAYERS} 名玩家已连接，开始初始化并倒计时...")
    init_game_state(NUM_PLAYERS)
    broadcast_game_state()

if __name__ == "__main__":
    start_server()
