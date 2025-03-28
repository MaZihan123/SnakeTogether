# client.py
import socket
import pickle
import pygame
import time
import importlib
from game_login import get_player_info
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

BLOCK_SIZE = 20
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
font_path = resource_path("assets/fontEND.ttf")
foodImg = pygame.image.load(resource_path("assets/food.png"))
foodImg = pygame.transform.scale(foodImg, (BLOCK_SIZE, BLOCK_SIZE))

def get_server_ip():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("请输入服务器 IP")
    font = pygame.font.Font(font_path, 32)
    clock = pygame.time.Clock()

    input_box = pygame.Rect(100, 80, 400, 40)
    color = pygame.Color('lightskyblue3')
    active = True

    #读取上次 IP（默认值）
    text = ""
    if os.path.exists("last_ip.txt"):
        with open("last_ip.txt", "r") as f:
            text = f.read().strip()

    while True:
        screen.fill((255, 255, 255))

        #提示信息
        prompt_text = f"请输入服务器 IP 地址：" if not text else f"使用默认 IP：{text}"
        prompt = font.render(prompt_text, True, (0, 0, 0))
        screen.blit(prompt, (100, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if text.strip():
                        # 保存为最新 IP
                        with open("last_ip.txt", "w") as f:
                            f.write(text.strip())
                        return text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif len(text) < 20:
                    text += event.unicode

        # 绘制输入框
        pygame.draw.rect(screen, color, input_box, 2)
        txt_surface = font.render(text, True, (0, 0, 0))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        input_box.w = max(400, txt_surface.get_width() + 10)

        pygame.display.flip()
        clock.tick(30)


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
    pygame.init()
    font = pygame.font.Font(font_path, 32)

    server_ip = get_server_ip()
    server_port = 12345
    mode, _, username = get_player_info()
    player_id = None  #初始化为空，后续从服务器获得
    player = None     #后续加载对应 player 模块

    print(f"Connecting to server {server_ip}:{server_port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    print("Connected to server.")

    init_info = {
        "type": "init",
        "requested_mode": mode,
        "player_id": None,  #不再传递 player_id
        "username": username
    }
    init_bytes = pickle.dumps(init_info)
    sock.sendall(len(init_bytes).to_bytes(4, 'big') + init_bytes)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Client")
    clock = pygame.time.Clock()

    current_direction = pygame.K_RIGHT
    running = True
    game_ended = False
    game_start_time = None

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
            usernames = game_state.get("usernames", [])

            #自动分配 player_id
            if player_id is None and username in usernames:
                player_id = usernames.index(username)
                print(f"当前玩家编号为 {player_id}")
                # 加载对应样式
                player_module_name = f"player{player_id + 1}"
                player = importlib.import_module(player_module_name)

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
            winner = game_state.get("winner", None)
            end_reason = game_state.get("end_reason", "")
            self_deaths = game_state.get("self_deaths", [])
            death_reasons = game_state.get("death_reasons", [])

            screen.fill((255, 255, 255))

            if countdown == 0 and game_start_time is None:
                game_start_time = time.time()

            if game_start_time:
                time_left = max(0, 120 - int(time.time() - game_start_time))
                timer_surf = font.render(f"剩余时间: {time_left}s", True, (0, 0, 200))
                screen.blit(timer_surf, (SCREEN_WIDTH - 240, 20))

            if countdown > 0:
                countdown_text = pygame.font.Font(font_path, 80).render(str(countdown), True, (255, 0, 0))
                screen.blit(countdown_text, ((SCREEN_WIDTH - countdown_text.get_width()) // 2, SCREEN_HEIGHT // 2 - 40))
            elif winner is not None:
                title = pygame.font.Font(font_path, 50).render("游戏结束 - 最终得分", True, (0, 128, 255))
                screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 80))

                sorted_scores = sorted(
                    [(usernames[i], scores[i]) for i in range(len(scores))],
                    key=lambda x: x[1],
                    reverse=True
                )
                for idx, (name, score) in enumerate(sorted_scores):
                    line = font.render(f"{idx + 1}. {name} - {score}", True, (0, 0, 0))
                    screen.blit(line, (SCREEN_WIDTH // 2 - 100, 160 + idx * 40))

                reason = pygame.font.Font(font_path, 24).render(f"{end_reason}", True, (128, 128, 128))
                screen.blit(reason, ((SCREEN_WIDTH - reason.get_width()) // 2, SCREEN_HEIGHT - 100))
                game_ended = True
            else:
                if player_id is not None and player_id < len(ate) and ate[player_id]:
                    player.eat_sound.play()

                # 蛇
                for i, snake_body in enumerate(snakes):
                    if not snake_body:
                        continue
                    try:
                        snake_module = importlib.import_module(f"player{i+1}")
                        head_img = snake_module.snake_head_img
                    except:
                        head_img = player.snake_head_img

                    for j, (x, y) in enumerate(snake_body):
                        rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
                        if j == 0:
                            if i == player_id:
                                pygame.draw.rect(screen, (255, 255, 0), rect.inflate(4, 4))
                            screen.blit(head_img, rect)
                            if i < len(usernames):
                                name_surf = pygame.font.SysFont(font_path, 20).render(usernames[i], True, (0, 0, 0))
                                screen.blit(name_surf, (x, y - 18))
                        else:
                            screen.blit(head_img, rect)

                # 食物
                for fx, fy in food_positions:
                    food_rect = pygame.Rect(fx, fy, BLOCK_SIZE, BLOCK_SIZE)
                    screen.blit(foodImg, food_rect)

                # 分数
                for idx in range(min(len(usernames), len(scores))):
                    label = font.render(f"{usernames[idx]}: {scores[idx]}", True, (0, 100 + idx * 15, 50))
                    screen.blit(label, (20, 20 + idx * 30))

                if player_id is not None and player_id in self_deaths:
                    reason = death_reasons.get(player_id, "")
                    if reason == "self":
                        msg = "你撞到了自己的身体，已被淘汰！"
                    elif reason:
                        msg = f"你{reason}，已被淘汰！"
                    else:
                        msg = "你已被淘汰！"

                    warn_font = pygame.font.Font(font_path, 24)
                    warn = warn_font.render(msg, True, (200, 50, 50))
                    screen.blit(warn, ((SCREEN_WIDTH - warn.get_width()) // 2, 20))  # 显示在顶部

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
