# client.py
import socket
import pickle
import pygame
from game_login import get_player_info
import player1
import player2

# 获取玩家身份与昵称
player_id, username = get_player_info()
if player_id == 0:
    import player1 as player
else:
    import player2 as player

BLOCK_SIZE = 20
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

font_path = "fontEND.ttf"

font = pygame.font.Font(font_path, 32)

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def main():
    server_ip = "192.168.1.108"  # 修改为你的服务器实际 IP
    #server_ip = "10.102.51.4"
    server_port = 12345
    print(f"Connecting to server {server_ip}:{server_port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    print("Connected to server.")

    # 注册身份信息
    init_info = {
        "type": "init",
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

    while running:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    current_direction = event.key
                    try:
                        sock.sendall(pickle.dumps(current_direction))
                    except Exception as e:
                        print("发送方向失败:", e)
                        running = False

        try:
            header = recvall(sock, 4)
            if not header:
                print("服务器断开连接")
                break
            length = int.from_bytes(header, 'big')
            body = recvall(sock, length)
            if not body:
                print("未接收到完整数据")
                break
            game_state = pickle.loads(body)

            screen.fill((255, 255, 255))

            snakes = game_state["snakes"]
            food_pos = game_state["food"]
            scores = game_state["scores"]
            ate = game_state.get("ate", [False, False])
            usernames = game_state.get("usernames", ["Player1", "Player2"])
            countdown = game_state.get("countdown", 0)
            winner = game_state.get("winner", None)
            end_reason = game_state.get("end_reason", "")

            font = pygame.font.SysFont(font_path, 28)

            if countdown > 0:
                # 显示倒计时
                countdown_text = pygame.font.SysFont(font_path, 80).render(str(countdown), True, (255, 0, 0))
                screen.blit(countdown_text, ((SCREEN_WIDTH - countdown_text.get_width()) // 2, SCREEN_HEIGHT // 2 - 40))
            elif winner is not None:
                # 显示游戏结束信息
                if winner == -1:
                    result_text = f"平局！"
                else:
                    result_text = f"{usernames[winner]} 获胜！"
                msg = pygame.font.SysFont(font_path, 60).render(result_text, True, (0, 128, 255))
                screen.blit(msg, ((SCREEN_WIDTH - msg.get_width()) // 2, SCREEN_HEIGHT // 2 - 50))
                reason = pygame.font.SysFont(font_path, 30).render(f"原因：{end_reason}", True, (128, 128, 128))
                screen.blit(reason, ((SCREEN_WIDTH - reason.get_width()) // 2, SCREEN_HEIGHT // 2 + 10))
                game_ended = True
            else:
                # 播放吃食音效
                if ate[player_id]:
                    player.eat_sound.play()

                #渲染不同蛇
                for i, snake_body in enumerate(snakes):
                    if i == 0:
                        img = player1.snake_head_img
                        name = usernames[0]
                    else:
                        img = player2.snake_head_img
                        name = usernames[1]

                    for idx, (x, y) in enumerate(snake_body):
                        rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)

                        # 加标识：在玩家自己控制的蛇头上添加高亮边框
                        if idx == 0:
                            if i == player_id:
                                pygame.draw.rect(screen, (255, 255, 0), rect.inflate(4, 4))  # 黄色描边
                            screen.blit(img, rect)

                            # 加昵称文字
                            font_user = pygame.font.SysFont(font_path, 20)
                            name_surf = font_user.render(name, True, (0, 0, 0))
                            screen.blit(name_surf, (x, y - 18))
                        else:
                            screen.blit(img, rect)

                # 绘制食物
                food_rect = pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE)
                screen.blit(player.snake_body_img, food_rect)

                # 显示分数和昵称
                label1 = font.render(f"{usernames[0]}: {scores[0]}", True, (0, 128, 0))
                label2 = font.render(f"{usernames[1]}: {scores[1]}", True, (128, 0, 0))
                screen.blit(label1, (20, 20))
                screen.blit(label2, (20, 50))

            pygame.display.flip()

            if game_ended:
                pygame.time.delay(5000)
                running = False

        except Exception as e:
            print("游戏循环错误:", e)
            break

    pygame.quit()
    sock.close()

if __name__ == "__main__":
    main()