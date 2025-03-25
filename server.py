# server.py
import socket
import threading
import pickle
import time
import pygame
from game_logic import Snake, Food, SCREEN_WIDTH, SCREEN_HEIGHT

# 游戏配置
BLOCK_SIZE = 20
NUM_PLAYERS = 2
directions = [pygame.K_RIGHT] * NUM_PLAYERS  # 初始方向
players_connected = 0
scores = [0] * NUM_PLAYERS
usernames = ["Player1", "Player2"]

# 游戏对象初始化
snake_list = [
    Snake(200, 300, pygame.K_RIGHT),
    Snake(600, 300, pygame.K_LEFT)
]
directions[0] = pygame.K_RIGHT
directions[1] = pygame.K_LEFT


food = Food()

# 游戏状态控制
game_started = False
countdown = 3
start_time = None
game_over = False
winner = None
end_reason = ""

# 网络通信工具函数
def send_with_header(conn, data_dict):
    """通过头部信息发送结构化数据"""
    body = pickle.dumps(data_dict)
    header = len(body).to_bytes(4, 'big')
    conn.sendall(header + body)

def recv_with_header(conn):
    """接收带头部信息的数据"""
    try:
        header = conn.recv(4)
        if not header: return None
        length = int.from_bytes(header, 'big')
        body = b""
        while len(body) < length:
            chunk = conn.recv(length - len(body))
            if not chunk: return None
            body += chunk
        return pickle.loads(body)
    except:
        return None

# 客户端处理线程
def client_handler(conn, player_id):
    global directions, players_connected, usernames
    try:
        # 接收玩家初始化信息
        init_msg = recv_with_header(conn)
        if isinstance(init_msg, dict) and init_msg.get("type") == "init":
            usernames[player_id] = init_msg.get("username", f"Player{player_id+1}")
            print(f"Player {player_id} connected as: {usernames[player_id]}")
        else:
            print(f"Player {player_id} 初始化失败")
    except Exception as e:
        print(f"接收初始化信息失败: {e}")
        conn.close()
        return

    # 持续接收方向指令
    while True:
        try:
            data = conn.recv(1024)
            if not data: break
            new_dir = pickle.loads(data)
            directions[player_id] = new_dir
        except:
            break
    conn.close()
    print(f"{usernames[player_id]} 断开连接")
    players_connected -= 1

# 游戏状态广播核心
def broadcast_game_state(conns):
    ate = [False, False]
    global snake_list, food, directions, scores
    global game_started, countdown, start_time, game_over, winner, end_reason

    clock = pygame.time.Clock()
    countdown_start = time.time()

    # 初始化随机方向（仅一次）
    import random
    for i in range(NUM_PLAYERS):
        directions[i] = random.choice([pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN])

    while True:
        clock.tick(10)
        now = time.time()

        # 游戏开始前的倒计时
        if not game_started:
            elapsed = int(now - countdown_start)
            countdown = max(0, 3 - elapsed)
            if countdown == 0 and not game_started:
                start_time = now
                game_started = True

        # 游戏进行中
        elif not game_over:
            ate = [False, False]

            # 更新蛇的位置
            for i, snake in enumerate(snake_list):
                snake.change_direction(directions[i])
                snake.move()

                # 检测食物
                if snake.body[0].colliderect(food.rect):
                    tail = snake.body[-1].copy()
                    snake.body.append(tail)
                    scores[i] += 10
                    food.refresh()
                    ate[i] = True

            # 检测游戏结束条件
            dead = [s.is_dead() for s in snake_list]
            if any(dead):
                game_over = True
                winner = 1 - dead.index(True)
                end_reason = f"{usernames[dead.index(True)]} 死亡"
            elif now - start_time >= 120:  # 2分钟限时
                game_over = True
                if scores[0] > scores[1]:
                    winner = 0
                    end_reason = "时间到，分数更高"
                elif scores[1] > scores[0]:
                    winner = 1
                    end_reason = "时间到，分数更高"
                else:
                    winner = -1
                    end_reason = "平局"

        # 构建游戏状态数据
        game_state = {
            "snakes": [ [(node.x, node.y) for node in s.body] for s in snake_list ],
            "food": (food.rect.x, food.rect.y),
            "scores": scores,
            "ate": ate if game_started and not game_over else [False, False],
            "usernames": usernames,
            "countdown": countdown if not game_started else 0,
            "winner": winner,
            "end_reason": end_reason
        }

        # 广播给所有客户端
        for c in conns:
            try:
                send_with_header(c, game_state)
            except:
                pass

        if game_over:
            print(f"游戏结束：{end_reason}")
            break

# 服务器启动函数
def start_server():
    host = "0.0.0.0"
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(NUM_PLAYERS)

    print("服务器启动，等待玩家连接...")
    conns = []
    global players_connected

    # 等待两个玩家连接
    while players_connected < NUM_PLAYERS:
        conn, addr = server_socket.accept()
        print(f"接收连接：{addr}")
        player_id = players_connected
        players_connected += 1
        conns.append(conn)
        threading.Thread(target=client_handler, args=(conn, player_id), daemon=True).start()

    print("两个玩家已连接，开始倒计时...")
    broadcast_game_state(conns)

if __name__ == "__main__":
    start_server()