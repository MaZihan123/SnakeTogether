import snake
import pygame

############################################################
####科比
############################################################

# player2的蛇
snake_head_img = pygame.image.load("牢信.jpg")
snake_head_img = pygame.transform.scale(snake_head_img, (snake.BLOCK_SIZE, snake.BLOCK_SIZE))
snake_body_img = pygame.image.load("牢信.jpg")
snake_body_img = pygame.transform.scale(snake_body_img, (snake.BLOCK_SIZE, snake.BLOCK_SIZE))
#player2吃食音效
eat = "man.mp3"
eat_sound = pygame.mixer.Sound(eat)



