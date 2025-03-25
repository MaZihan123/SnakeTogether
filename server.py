# server.py
import socket
import threading
import pickle
import time
import pygame
import random
import player1
import player2

BLOCK_SIZE = 20
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Food:
    def __init__(self):
        self.rect = pygame.Rect(0,0,BLOCK_SIZE,BLOCK_SIZE)
        self.refresh()

    def refresh(self):
        self.rect.x = random.randrange(0, SCREEN_WIDTH, BLOCK_SIZE)
        self.rect.y = random.randrange(0, SCREEN_HEIGHT, BLOCK_SIZE)


# 两个全局玩家方向
directions = [pygame.K_RIGHT, pygame.K_RIGHT]  # 初始化都向右
num_players = 2
players_connected = 0

# 创建游戏对象
snake_list = [
    player1.Snake(100, 300, pygame.K_RIGHT),  # 玩家0的蛇
    player2.Snake(700, 300, pygame.K_LEFT)  # 玩家1的蛇，初始向左
]
food = Food()

# 简单的“分数”记录
scores = [0, 0]


def client_handler(conn, player_id):
    global directions, players_connected

    # 接收客户端方向并存到 directions[player_id]
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            new_dir = pickle.loads(data)  # 反序列化
            directions[player_id] = new_dir
        except:
            break
    conn.close()
    print(f"Player {player_id} disconnected.")
    players_connected -= 1


def broadcast_game_state(server_socket, conns):
    """
    每帧更新游戏状态、广播给所有客户端
    """
    global snake_list, food, directions, scores

    # 每秒 10 帧
    clock = pygame.time.Clock()
    while True:
        clock.tick(10)

        # 更新两个蛇的方向、移动
        for i, snake in enumerate(snake_list):
            snake.change_direction(directions[i])
            snake.move()

            # 如果吃到食物
            if snake.body[0].colliderect(food.rect):
                # 长度 +1（实际上是“尾巴不pop”）
                tail = snake.body[-1].copy()
                snake.body.append(tail)
                scores[i] += 10
                food.refresh()

            # 判断死亡
            if snake.is_dead():
                print(f"Player {i} died. Game Over.")
                # 这里只是简单处理：蛇死了就重置
                snake_list[0] = player1.Snake(100, 300, pygame.K_RIGHT)
                snake_list[1] = player2.Snake(700, 300, pygame.K_LEFT)
                scores[0], scores[1] = 0, 0
                food.refresh()
                # 也可以选择只让这个玩家退出，或重开房间等

        # 整理要发送给客户端的数据
        # 包括：每条蛇的 body 列表、食物位置、分数等
        game_state = {
            "snakes": [[(node.x, node.y) for node in s.body] for s in snake_list],
            "food": (food.rect.x, food.rect.y),
            "scores": scores
        }

        data_bytes = pickle.dumps(game_state)

        # 广播给所有客户端
        for c in conns:
            c.sendall(data_bytes)


def start_server():
    host = "192.168.95.8"  # 本机IP
    port = 12345  # 随意选个端口

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)

    print("Server listening on port:", port)

    conns = []
    global players_connected

    # 等待连接
    while players_connected < num_players:
        conn, addr = server_socket.accept()
        print("Connected from:", addr)
        player_id = players_connected
        players_connected += 1
        conns.append(conn)
        # 每个客户端独立一个线程，接收按键方向
        threading.Thread(target=client_handler, args=(conn, player_id)).start()

    print("2 Players connected. Start game broadcast.")
    # 游戏开始后，启动广播线程
    broadcast_game_state(server_socket, conns)


if __name__ == "__main__":
    start_server()
