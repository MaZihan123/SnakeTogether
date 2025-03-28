
import pygame
import random

BLOCK_SIZE = 20
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

class Snake:
    def __init__(self, x, y, direction):
        self.direction = direction
        self.body = []

        dx, dy = 0, 0
        if direction == pygame.K_RIGHT:
            dx, dy = -1, 0
        elif direction == pygame.K_LEFT:
            dx, dy = 1, 0
        elif direction == pygame.K_UP:
            dx, dy = 0, 1
        elif direction == pygame.K_DOWN:
            dx, dy = 0, -1

        for i in range(5):
            node = pygame.Rect(x + dx * i * BLOCK_SIZE, y + dy * i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
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
