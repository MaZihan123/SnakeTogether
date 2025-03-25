# client.py
import socket
import pickle
import pygame
import player1
import player2
import random

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


def main():
    # 1. 连接服务器
    #server_ip = "192.168.95.8"  # 改成服务器的局域网IP
    server_ip = "192.168.1.108"#IMUDGES 115
    server_port = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    print("Connected to server.")

    # 2. 初始化pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Client")
    clock = pygame.time.Clock()




    # 用于记录当前方向，默认向右
    current_direction = pygame.K_RIGHT

    running = True

    while running:
        clock.tick(10)

        # 2.1 处理玩家输入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    current_direction = event.key
                    # 把方向发送给服务器
                    sock.sendall(pickle.dumps(current_direction))

        # 2.2 接收来自服务器的游戏状态
        #    这里要考虑粘包问题，示例中简化处理
        data = b""
        sock.setblocking(False)
        try:
            chunk = sock.recv(4096)
            if chunk:
                data += chunk
        except:
            pass
        sock.setblocking(True)

        if data:
            try:
                game_state = pickle.loads(data)
                # 绘制
                screen.fill((255, 255, 255))
                # 取出两条蛇数据
                snakes = game_state["snakes"]  # list of list, e.g. [[(x1,y1)...], [(x2,y2)...]]
                food_pos = game_state["food"]  # (fx, fy)
                scores = game_state["scores"]

                # 画蛇
                for i, snake_body in enumerate(snakes):
                    for x, y in snake_body:
                        rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
                        if i == 0:
                            screen.blit(player1.snake_head_img, rect)
                        else:
                            screen.blit(player2.snake_head_img, rect)

                # 画食物
                rect = pygame.Rect(food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE)
                screen.blit(player1.food_img, rect)


                # 显示分数
                font = pygame.font.SysFont(None, 30)
                score_text = font.render(f"Scores: {scores}", True, (0,0,0))
                screen.blit(score_text, (10, 10))

                pygame.display.flip()
            except:
                pass

    pygame.quit()
    sock.close()

if __name__ == "__main__":
    main()
