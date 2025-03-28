import snake
import pygame

############################################################
####科比
############################################################


import sys
import os

def resource_path(relative_path):
    """兼容 PyInstaller 打包路径和本地开发路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# player2的蛇
snake_head_img = pygame.image.load("assets/牢橘.jpg")
snake_head_img = pygame.transform.scale(snake_head_img, (snake.BLOCK_SIZE, snake.BLOCK_SIZE))
snake_body_img = pygame.image.load("assets/牢橘.jpg")
snake_body_img = pygame.transform.scale(snake_body_img, (snake.BLOCK_SIZE, snake.BLOCK_SIZE))
#player2吃食音效
eat = resource_path("eat.mp3")
#eat = "man.mp3"
eat_sound = pygame.mixer.Sound(eat)



