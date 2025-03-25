# player2.py

import pygame
import snake



############################################################
####IKUN
############################################################

# player1的蛇
snake_head_img = pygame.image.load("ikun.png")
snake_head_img = pygame.transform.scale(snake_head_img, (snake.BLOCK_SIZE,snake. BLOCK_SIZE))
snake_body_img = pygame.image.load("ikun.png")
snake_body_img = pygame.transform.scale(snake_body_img, (snake.BLOCK_SIZE, snake.BLOCK_SIZE))
#player1吃食音效
pygame.mixer.init()
eat = "eat.mp3"
eat_sound = pygame.mixer.Sound(eat)


