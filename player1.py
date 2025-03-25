# player2.py

import pygame
import random

BLOCK_SIZE = 20
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

############################################################
####IKUN
############################################################

# player1的蛇
snake_head_img = pygame.image.load("ikun.png")
snake_head_img = pygame.transform.scale(snake_head_img, (BLOCK_SIZE, BLOCK_SIZE))
snake_body_img = pygame.image.load("ikun.png")
snake_body_img = pygame.transform.scale(snake_body_img, (BLOCK_SIZE, BLOCK_SIZE))
#player1吃食音效
eat = "eat.mp3"
eat_sound = pygame.mixer.Sound(eat)

class Snake:
    def __init__(self, x, y, direction=pygame.K_RIGHT):
        self.direction = direction
        self.body = []
        # 初始给蛇 5 节身体
        for i in range(5):
            node = pygame.Rect(x - i * BLOCK_SIZE, y, BLOCK_SIZE, BLOCK_SIZE)
            self.body.append(node)

    def move(self):
        # 每帧移动：在头部前进一格，尾部去掉一格
        head = self.body[0].copy()
        if self.direction == pygame.K_LEFT:
            head.x -= BLOCK_SIZE
        elif self.direction == pygame.K_RIGHT:
            head.x += BLOCK_SIZE
        elif self.direction == pygame.K_UP:
            head.y -= BLOCK_SIZE
        elif self.direction == pygame.K_DOWN:
            head.y += BLOCK_SIZE
        self.body.insert(0, head)
        self.body.pop()  # 去尾

    def change_direction(self, new_dir):
        # 简单防止 180 度转弯
        LR = [pygame.K_LEFT, pygame.K_RIGHT]
        UD = [pygame.K_UP, pygame.K_DOWN]
        if (new_dir in LR and self.direction in LR) or (new_dir in UD and self.direction in UD):
            return
        self.direction = new_dir

    def is_dead(self):
        # 撞墙
        head = self.body[0]
        if head.x < 0 or head.x >= SCREEN_WIDTH or head.y < 0 or head.y >= SCREEN_HEIGHT:
            return True
        # 撞自己
        if head in self.body[1:]:
            return True
        return False
