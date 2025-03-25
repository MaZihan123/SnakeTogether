# game_login.py
import pygame
import sys

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("登录界面")

font_path = "fontEND.ttf"
font = pygame.font.Font(font_path, 32)
small_font = pygame.font.Font(font_path, 24)
clock = pygame.time.Clock()

color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')

def draw_button(rect, text):
    pygame.draw.rect(screen, (100, 200, 100), rect)
    label = small_font.render(text, True, (0, 0, 0))
    screen.blit(label, (rect.x + (rect.width - label.get_width()) // 2,
                        rect.y + (rect.height - label.get_height()) // 2))

def choose_game_mode():
    buttons = []
    modes = list(range(2, 10))  # 支持 2~9 人
    gap = 20
    btn_width = 100
    total_width = len(modes) * (btn_width + gap) - gap
    start_x = (SCREEN_WIDTH - total_width) // 2
    y = 150

    for i, m in enumerate(modes):
        rect = pygame.Rect(start_x + i * (btn_width + gap), y, btn_width, 60)
        buttons.append((rect, m))

    while True:
        screen.fill((255, 255, 255))
        title = font.render("请选择玩家人数", True, (0, 0, 0))
        screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, m in buttons:
                    if rect.collidepoint(event.pos):
                        return m

        for rect, m in buttons:
            draw_button(rect, f"{m}人模式")

        pygame.display.flip()
        clock.tick(30)

def choose_identity(max_players):
    input_box = pygame.Rect(250, 80, 300, 40)
    color = color_inactive
    active = False
    username = ""
    buttons = []

    for i in range(max_players):
        x = 80 + (i % 3) * 220
        y = 180 + (i // 3) * 80
        rect = pygame.Rect(x, y, 180, 50)
        buttons.append((rect, i))

    while True:
        screen.fill((255, 255, 255))
        title = font.render("输入昵称并选择角色", True, (0, 0, 0))
        screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                    color = color_active
                else:
                    active = False
                    color = color_inactive

                for rect, pid in buttons:
                    if rect.collidepoint(event.pos) and username.strip():
                        return pid, username.strip()
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.key == pygame.K_RETURN:
                    active = False
                    color = color_inactive
                elif len(username) < 12:
                    username += event.unicode

        pygame.draw.rect(screen, color, input_box, 2)
        txt_surface = font.render(username, True, (0, 0, 0))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        input_box.w = max(300, txt_surface.get_width() + 10)

        for rect, pid in buttons:
            draw_button(rect, f"选择角色 {pid + 1}")

        pygame.display.flip()
        clock.tick(30)

# 对外接口
def get_player_info():
    """
    返回三元组：选择的最大玩家数、当前玩家编号（0~8）、昵称
    """
    selected_mode = choose_game_mode()
    player_id, username = choose_identity(selected_mode)
    return selected_mode, player_id, username
