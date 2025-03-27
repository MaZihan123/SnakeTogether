# player2.py

import pygame
import snake

import sys
import os

def resource_path(relative_path):
    """兼容 PyInstaller 打包路径和本地开发路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)



############################################################
####IKUN
############################################################

# player1的蛇
snake_head_img = pygame.image.load(resource_path("ikun.png"))
snake_head_img = pygame.transform.scale(snake_head_img, (snake.BLOCK_SIZE,snake. BLOCK_SIZE))
snake_body_img = pygame.image.load(resource_path("ikun.png"))
snake_body_img = pygame.transform.scale(snake_body_img, (snake.BLOCK_SIZE, snake.BLOCK_SIZE))
#player1吃食音效
pygame.mixer.init()
eat = resource_path("eat.mp3")
eat_sound = pygame.mixer.Sound(eat)


