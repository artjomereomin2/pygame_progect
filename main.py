'''главный герой + анимация
пробел - + скорость к верху
столкновение - замедляем подлёт
проигрываем - упали в самый низ'''

import pygame
import sys
import os
import random

FPS = 50

# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
particles_sprites = pygame.sprite.Group()
musor = pygame.sprite.Group()

pygame.init()

SIZE = WIDTH, HEIGHT = (440, 440)

screen = pygame.display.set_mode(SIZE)

clock = pygame.time.Clock()

running = True


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 512
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color((32, 32, 32)))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return main_game()
        pygame.display.flip()
        clock.tick(FPS)


def main_game():
    global player
    player = Player(100, HEIGHT // 2)
    particles = []
    global level_x, level_y

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.move()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_RIGHT:
                    # то, что происходит при столкновении с мусором
                    '''particles.append(SpawnParticles((player.rect.centerx, player.rect.centery), 0, 0,
                                                    [pygame.transform.scale(load_image('fallingsmoke.png', -1), (x, x))
                                                     for
                                                     x in (10, 20, 30)], change=lambda x: x % 5 == 0, times=20,
                                                    follow_player=True, gravity=(-1, 0), count=40))
                    player.de_baf(10 ** 2 * 3)'''
                if event.button == pygame.BUTTON_LEFT:
                    player.move()

        screen.fill((0, 0, 0))
        i = 0
        while i < len(particles):
            p = particles[i]
            if p.alive == -1:
                particles.pop(i)
            else:
                p.update()
                i += 1

        if pygame.sprite.spritecollideany(player, musor):
            particles.append(SpawnParticles((player.rect.centerx, player.rect.centery), 0, 0,
                                            [pygame.transform.scale(load_image('fallingsmoke.png', -1), (x, x))
                                             for
                                             x in (10, 20, 30)], change=lambda x: x % 5 == 0, times=20,
                                            follow_player=True, gravity=(-1, 0), count=40))
            player.de_baf(10 ** 2 * 3)

        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        particles_sprites.update()
        particles_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, groups, sheet, columns, rows, x, y, scale_to=None, switch=lambda x: True):
        super().__init__(*groups)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        if scale_to is not None:
            for i in range(len(self.frames)):
                self.frames[i] = pygame.transform.scale(self.frames[i], scale_to)
        self.time = 0
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.switch = switch

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.time += 1
        if self.switch(self.time):
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        return self.frames[self.cur_frame]


class Player(AnimatedSprite):
    def __init__(self, pos_x, pos_y):
        super().__init__((player_group, all_sprites), pygame.transform.rotate(load_image('fire.png', -1), 90), 4, 5,
                         pos_x,
                         pos_y,
                         switch=lambda x: x % 10 == 0, scale_to=(100, 100))
        self.speedy = 0
        self.acceleration = 4
        self.G = 9.8 / FPS
        self.other_image = pygame.transform.scale(load_image('hero.png', -1), (500, 150))
        other_image = self.other_image.copy()
        self.image = other_image
        self.rect = self.image.get_rect()

        self.rect.centerx = pos_x
        self.rect.centery = pos_y

        self.slow_timer = 0

    def move(self):
        # print(self.rect.x, self.rect.y)
        self.speedy -= self.acceleration if self.slow_timer == 0 else self.acceleration // 2

    def update(self):
        self.slow_timer = max(0, self.slow_timer - 1)
        self.speedy += self.G
        self.rect.y += self.speedy
        other_image = self.other_image.copy()
        other_image.blit(super().update(), (160, 30))
        self.image = other_image

        # print(self.rect.x, self.rect.y)

    def de_baf(self, value=10 ** 3):
        self.slow_timer += value


screen_rect = (0, 0, WIDTH, HEIGHT)


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    '''fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))'''

    def __init__(self, pos, dx, dy, pictures, gravity=(0, 1), change=lambda x: x % 20 == 0):
        super().__init__(particles_sprites)
        self.pictures = pictures
        self.image_ind = random.choice(list(range(len(pictures))))
        self.image = self.pictures[self.image_ind]
        self.rect = self.image.get_rect()

        self.time = 0

        self.change = change

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx + random.randrange(-4, 5), dy + random.randrange(-4, 5)]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = gravity

    def update(self):
        self.time += 1

        # print(self.rect.x, self.rect.y, self.velocity, self.gravity)

        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[0] += self.gravity[0]
        self.velocity[1] += self.gravity[1]
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # print(self.image_ind)

        if self.change(self.time):
            self.image_ind += 1
            if self.image_ind == len(self.pictures):
                self.kill()
                return
            self.image = self.pictures[self.image_ind]
            x, y = self.rect.x, self.rect.y
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = x, y
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


class SpawnParticles():
    def __init__(self, pos, dx, dy, pictures, count=10, times=1, gravity=(0, 1), change=lambda x: x % 10 == 0,
                 split=10, follow_player=False):
        self.alive = 1
        self.pos = pos
        self.speed = [dx, dy]
        self.gravity = gravity
        self.pictures = pictures
        self.count = count
        self.times = times
        self.split = split
        self.change = change
        self.time = 0
        self.follow_player = follow_player

    def update(self):
        if self.times > 0:
            if self.time % self.split == 0:
                if self.follow_player:
                    self.pos = player.rect.centerx, player.rect.centery
                # print(self.time, self.times)
                for _ in range(self.count):
                    Particle(self.pos, *self.speed, self.pictures, self.gravity, self.change)
                self.times -= 1
            self.time += 1


start_screen()
