# game_login.py
import pygame
import sys
import os

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
font_path = os.path.join(os.path.abspath("."), "fontEND.ttf")

def get_player_info():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("登录界面")
    clock = pygame.time.Clock()

    font = pygame.font.Font(font_path, 28)
    input_box = pygame.Rect(150, 120, 300, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    selected_mode = None

    # 按钮
    button_font = pygame.font.Font(font_path, 24)
    buttons = []
    for i in range(2, 10):  # 2~9人模式
        rect = pygame.Rect(80 + ((i - 2) % 4) * 120, 200 + ((i - 2) // 4) * 60, 100, 40)
        buttons.append((rect, f"{i}人模式"))

    while True:
        screen.fill((255, 255, 255))
        prompt = font.render("请输入你的用户名：", True, (0, 0, 0))
        screen.blit(prompt, (150, 80))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                for idx, (rect, label) in enumerate(buttons):
                    if rect.collidepoint(event.pos) and text.strip():
                        selected_mode = idx + 2
                        return selected_mode, None, text.strip()
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif len(text) < 15:
                    text += event.unicode

        color = color_active if active else color_inactive
        pygame.draw.rect(screen, color, input_box, 2)
        name_surface = font.render(text, True, (0, 0, 0))
        screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
        input_box.w = max(300, name_surface.get_width() + 10)

        for rect, label in buttons:
            pygame.draw.rect(screen, (0, 150, 200), rect)
            label_surf = button_font.render(label, True, (255, 255, 255))
            screen.blit(label_surf, (rect.x + 10, rect.y + 8))

        pygame.display.flip()
        clock.tick(30)
