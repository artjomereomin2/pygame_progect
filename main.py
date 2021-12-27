import os
import sys
import random
from random import randint
import pygame
from math import atan, degrees

pygame.init()
size = width, height = 700, 700
screen = pygame.display.set_mode(size)
FPS = 50
GRAVITY = 0.1


def load_image(name, colorkey=None, size=None, rotate=0):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    image = pygame.transform.rotate(image, rotate)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    if size is not None:
        image = pygame.transform.scale(image, size)
    return image


class Garbage(pygame.sprite.Sprite):
    image = load_image("garbage.png", -1, None, 180)

    def __init__(self, pos):
        super().__init__(all_sprites, group_garbage)
        self.image = Garbage.image
        self.gravitate = 0
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update(self):
        self.rect.x -= 3
        self.rect.y += int(self.gravitate)
        if self.rect.y >= height or self.rect.x < -36:
            self.kill()
        self.gravitate += GRAVITY
        self.image = load_image("garbage.png", -1, None, degrees(atan(self.gravitate / 3)) + 180)


def draw(screen):
    screen.fill((0, 0, 0))
    for _ in range(20000):
        pygame.draw.circle(screen, (255, 255, 255), (randint(0, 800), randint(0, 800)), 1, width=0)


all_sprites = pygame.sprite.Group()
group_garbage = pygame.sprite.Group()
player = pygame.sprite.Group()
clock = pygame.time.Clock()
running = True
sec = 0
coeff = 2
level = 0
iss = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            iss = True
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    all_sprites.update()
    if iss:
        sec += 1
        if sec == FPS // int(coeff):
            sec = 0
            level += 1
            Garbage((width, randint(-2 * height, 0)))
            Garbage((width, randint(0, height // 2)))
        if level == 20:
            level = 0
            coeff += 0.5
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()
