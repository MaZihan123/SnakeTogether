# game_login.py
import pygame
import sys

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("选择玩家身份")

font_path = "fontEND.ttf"

font = pygame.font.Font(font_path, 32)
small_font = pygame.font.Font(font_path, 24)


clock = pygame.time.Clock()

input_box = pygame.Rect(150, 80, 300, 40)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
username = ""

button1 = pygame.Rect(80, 200, 180, 60)
button2 = pygame.Rect(340, 200, 180, 60)

def draw_button(rect, text):
    pygame.draw.rect(screen, (100, 200, 100), rect)
    label = small_font.render(text, True, (0, 0, 0))
    screen.blit(label, (rect.x + (rect.width - label.get_width()) // 2,
                        rect.y + (rect.height - label.get_height()) // 2))

def get_player_choice():
    global active, color, username
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                    color = color_active
                else:
                    active = False
                    color = color_inactive
                if button1.collidepoint(event.pos) and username.strip():
                    return 0, username.strip()
                if button2.collidepoint(event.pos) and username.strip():
                    return 1, username.strip()
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    active = False
                    color = color_inactive
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 12:
                        username += event.unicode

        screen.fill((255, 255, 255))

        title = font.render("请输入你的昵称并选择角色", True, (0, 0, 0))
        screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 20))

        pygame.draw.rect(screen, color, input_box, 2)
        txt_surface = font.render(username, True, (0, 0, 0))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        input_box.w = max(300, txt_surface.get_width() + 10)

        draw_button(button1, "选择 IKUN (Player 1)")
        draw_button(button2, "选择 KOBE (Player 2)")

        pygame.display.flip()
        clock.tick(30)

def get_player_id():
    player_id, _ = get_player_choice()
    return player_id

def get_player_info():
    return get_player_choice()