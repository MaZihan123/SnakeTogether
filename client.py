# client.py

import socket
import pickle
import pygame
import time
from game_login import get_player_info

# 获取登录信息
mode, player_id, username = get_player_info()

# 动态导入 player1 ~ player9
import importlib
player_module_name = f"player{player_id + 1}"
player = importlib.import_module(player_module_name)

BLOCK_SIZE = 20
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

font_path = "fontEND.ttf"
foodImg = pygame.image.load("baskteball.png")
foodImg = pygame.transform.scale(foodImg, (BLOCK_SIZE, BLOCK_SIZE))
font = pygame.font.Font(font_path, 32)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def draw_waiting_screen(screen, font, width, height, joined, expected):
    msg1 = font.render("等待其他玩家加入...", True, (0, 0, 0))
    msg2 = font.render(f"已连接玩家：{joined}/{expected}", True, (50, 50, 150))
    screen.blit(msg1, ((width - msg1.get_width()) // 2, height // 2 - 40))
    screen.blit(msg2, ((width - msg2.get_width()) // 2, height // 2 + 10))


def main():
    server_ip = "192.168.1.119"  # ⚠️ 修改为你的服务器 IP
    server_port = 12345

    print(f"Connecting to server {server_ip}:{server_port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    print("Connected to server.")

    # 发送初始化信息（requested_mode 只有第一个玩家有效，其他玩家也发送但服务器会忽略）
    init_info = {
        "type": "init",
        "requested_mode": mode,
        "player_id": player_id,
        "username": username
    }
    init_bytes = pickle.dumps(init_info)
    sock.sendall(len(init_bytes).to_bytes(4, 'big') + init_bytes)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"Snake Client - Player {player_id + 1}")
    clock = pygame.time.Clock()

    current_direction = pygame.K_RIGHT
    running = True
    game_ended = False
    game_start_time = None
    usernames = []


    while running:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                current_direction = event.key
                try:
                    sock.sendall(pickle.dumps(current_direction))
                except:
                    print("发送方向失败")
                    running = False

        try:
            header = recvall(sock, 4)
            if not header:
                print("服务器断开连接")
                break
            length = int.from_bytes(header, 'big')
            body = recvall(sock, length)
            if not body:
                break

            game_state = pickle.loads(body)

            countdown = game_state.get("countdown", -1)

            # 等待界面处理（提前 continue 掉，不再往下读游戏数据）
            if countdown == -1:
                connected = game_state.get("connected", len(usernames))
                expected = game_state.get("expected", mode)
                draw_waiting_screen(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT, connected, expected)
                pygame.display.flip()
                continue

            snakes = game_state["snakes"]
            food_positions = game_state.get("foods", [])
            scores = game_state["scores"]
            ate = game_state.get("ate", [])
            usernames = game_state.get("usernames", [])
            countdown = game_state.get("countdown", -1)  # 倒计时可能未开始
            winner = game_state.get("winner", None)
            end_reason = game_state.get("end_reason", "")

            screen.fill((255, 255, 255))

            # 👇 等待其他玩家加入界面
            if countdown == -1:
                connected = game_state.get("connected", len(usernames))
                expected = game_state.get("expected", mode)
                draw_waiting_screen(screen, font, SCREEN_WIDTH, SCREEN_HEIGHT, connected, expected)
                pygame.display.flip()
                continue

            # 游戏计时开始
            if countdown == 0 and game_start_time is None:
                game_start_time = time.time()

            if game_start_time:
                time_left = max(0, 120 - int(time.time() - game_start_time))
                timer_surf = font.render(f"剩余时间: {time_left}s", True, (0, 0, 200))
                screen.blit(timer_surf, (SCREEN_WIDTH - 240, 20))

            # 倒计时
            if countdown > 0:
                countdown_text = pygame.font.Font(font_path, 80).render(str(countdown), True, (255, 0, 0))
                screen.blit(countdown_text, ((SCREEN_WIDTH - countdown_text.get_width()) // 2, SCREEN_HEIGHT // 2 - 40))
            elif winner is not None:
                result = "平局！" if winner == -1 else f"用户：{usernames[winner]} 获胜！"
                msg = pygame.font.Font(font_path, 60).render(result, True, (0, 128, 255))
                screen.blit(msg, ((SCREEN_WIDTH - msg.get_width()) // 2, SCREEN_HEIGHT // 2 - 50))
                reason = pygame.font.Font(font_path, 30).render(end_reason, True, (128, 128, 128))
                screen.blit(reason, ((SCREEN_WIDTH - reason.get_width()) // 2, SCREEN_HEIGHT // 2 + 10))
                game_ended = True
            else:
                # 播放吃食音效
                if isinstance(ate, list) and 0 <= player_id < len(ate):
                    if ate[player_id]:
                        player.eat_sound.play()

                # 绘制所有蛇
                for i, snake_body in enumerate(snakes):
                    try:
                        snake_module = importlib.import_module(f"player{i+1}")
                        head_img = snake_module.snake_head_img
                    except:
                        head_img = player.snake_head_img  # 默认用当前的资源

                    for j, (x, y) in enumerate(snake_body):
                        rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
                        if j == 0:
                            if i == player_id:
                                pygame.draw.rect(screen, (255, 255, 0), rect.inflate(4, 4))
                            screen.blit(head_img, rect)
                            if isinstance(usernames, list) and i < len(usernames):
                                name_surf = pygame.font.SysFont(font_path, 20).render(usernames[i], True, (0, 0, 0))
                                screen.blit(name_surf, (x, y - 20))
                        else:
                            screen.blit(head_img, rect)

                # 绘制食物
                for fx, fy in food_positions:
                    food_rect = pygame.Rect(fx, fy, BLOCK_SIZE, BLOCK_SIZE)
                    screen.blit(foodImg, food_rect)

                # 显示分数
                for idx in range(min(len(usernames), len(scores))):
                    label = font.render(f"{usernames[idx]}: {scores[idx]}", True, (0, 100 + idx * 15, 50))
                    screen.blit(label, (20, 20 + idx * 30))

            pygame.display.flip()

            if game_ended:
                pygame.time.delay(5000)
                running = False

        except Exception as e:
            print("游戏循环异常:", e)
            break

    pygame.quit()
    sock.close()

if __name__ == "__main__":
    main()