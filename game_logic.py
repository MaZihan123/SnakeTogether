# game_logic.py
# 提供纯逻辑版本的 Snake 和 Food 类，供服务器端使用，不依赖图像、音效、渲染

import pygame
import random

import sys
import os

def resource_path(relative_path):
    """兼容 PyInstaller 打包路径和本地开发路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


BLOCK_SIZE = 20
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

class Snake:
    def __init__(self, x, y, direction=pygame.K_RIGHT):
        self.direction = direction
        self.body = []
        for i in range(5):
            node = pygame.Rect(x - i * BLOCK_SIZE, y, BLOCK_SIZE, BLOCK_SIZE)
            self.body.append(node)

#不穿墙
    # def move(self):
    #     head = self.body[0].copy()
    #     if self.direction == pygame.K_LEFT:
    #         head.x -= BLOCK_SIZE
    #     elif self.direction == pygame.K_RIGHT:
    #         head.x += BLOCK_SIZE
    #     elif self.direction == pygame.K_UP:
    #         head.y -= BLOCK_SIZE
    #     elif self.direction == pygame.K_DOWN:
    #         head.y += BLOCK_SIZE
    #     self.body.insert(0, head)
    #     self.body.pop()

    #穿墙
    def move(self):
        head = self.body[0].copy()

        if self.direction == pygame.K_LEFT:
            head.x -= BLOCK_SIZE
        elif self.direction == pygame.K_RIGHT:
            head.x += BLOCK_SIZE
        elif self.direction == pygame.K_UP:
            head.y -= BLOCK_SIZE
        elif self.direction == pygame.K_DOWN:
            head.y += BLOCK_SIZE

        # 穿墙处理
        head.x %= SCREEN_WIDTH
        head.y %= SCREEN_HEIGHT

        self.body.insert(0, head)
        self.body.pop()

    def change_direction(self, new_dir):
        LR = [pygame.K_LEFT, pygame.K_RIGHT]
        UD = [pygame.K_UP, pygame.K_DOWN]
        if (new_dir in LR and self.direction in LR) or (new_dir in UD and self.direction in UD):
            return
        self.direction = new_dir

    def is_dead(self):
        # head = self.body[0]
        # if head.x < 0 or head.x >= SCREEN_WIDTH or head.y < 0 or head.y >= SCREEN_HEIGHT:
        #     return True
        #撞自己
        #if head in self.body[1:]:
        #    return True
        return False

class Food:
    foodImg=resource_path("assets/baskteball.png")
    def __init__(self):
        self.rect = pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE)
        self.refresh()

    def refresh(self):
        self.rect.x = random.randrange(0, SCREEN_WIDTH, BLOCK_SIZE)
        self.rect.y = random.randrange(0, SCREEN_HEIGHT, BLOCK_SIZE)