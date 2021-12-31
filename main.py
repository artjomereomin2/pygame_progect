import os
import sys
import random
from random import randint
import pygame

FPS = 50

# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
particles_sprites = pygame.sprite.Group()
stars_sprites = pygame.sprite.Group()
garbage_group = pygame.sprite.Group()

iss = True

G = 9.8 / FPS

pygame.init()

SIZE = WIDTH, HEIGHT = (1200, 600)

screen = pygame.display.set_mode(SIZE)

clock = pygame.time.Clock()

running = True


def load_image(name, colorkeylist=None, size=None, rotate=0):
    if isinstance(name, str):
        fullname = os.path.join('data', name)
        # если файл не существует, то выходим
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        image = pygame.transform.rotate(image, rotate)
    else:
        image = name
    if colorkeylist is not None:
        image = image.convert()
        if colorkeylist[0] == -1:
            colorkeylist[0] = image.get_at((0, 0))
        image.set_colorkey(colorkeylist[0])
        colorkeylist.pop()
        if len(colorkeylist) > 0:
            image = load_image(image, colorkeylist=colorkeylist, size=size)
    else:
        image = image.convert_alpha()
    if size is not None:
        image = pygame.transform.scale(image, size)
    return image


class Garbage(pygame.sprite.Sprite):
    image_small = load_image("garbage.png", [-1], (75, 75), 180)
    image_big = load_image("big_garbage.png", [-1], (200, 200))

    def __init__(self, pos, big=False):
        super().__init__(all_sprites, garbage_group)
        if big:
            self.image = Garbage.image_big
        else:
            self.image = Garbage.image_small
        self.big = big
        self.gravitate = 0
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        # self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update(self):
        self.rect.x -= 3 + int(self.gravitate)
        self.rect.y += +randint(-5, 5)
        if not self.rect.colliderect(screen_rect):
            self.kill()
        self.gravitate += G


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Название игры",
                  "Правила игры:",
                  "Нажмите пробел или левую кнопку мыши,", "чтобы подлететь вверх.",
                  "Избегайте препятствий, они могут сломать ваш двигатель.",
                  "Не падайте на землю - проиграете.",
                  "Нажмите что-нибудь для начала игры."]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 200
    mx_right = 0
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color(239, 239, 239))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        mx_right = max(mx_right, intro_rect.y)
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        # print(intro_rect.x, intro_rect.y)

    # (0, 0, 0,50), ((10, 200), (mx_right, text_coord - 200))
    image = pygame.Surface([WIDTH, text_coord - 200])
    image.fill((0, 0, 0))
    image.set_alpha(50)
    screen.blit(image, (0, 200))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return main_game(20)
        pygame.display.flip()
        clock.tick(FPS)


star_red_picture = load_image('star_red.png', [-1], size=(10, 10))
star_blue_picture = load_image('star_blue.png', [-1], size=(10, 10))


def main_game(level_max):
    global player, iss
    player = Player(100, HEIGHT // 2)
    particles = []
    sec = 0
    coeff = 0.5
    level = 0
    global level_x, level_y

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and iss:
                    player.move()
                if event.key == pygame.K_e:
                    iss = False
                if event.key == pygame.K_c:
                    iss = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT and iss:
                    player.move()
        screen.fill((0, 0, 0))

        # Астероиды
        if iss:
            sec += 1
        if sec == int(FPS / coeff):
            sec = 0
            level += 1
            big = randint(0, 10) == 0
            Garbage((WIDTH, randint(20 - 10 * big, HEIGHT - 110 * (1 + big))), big=big)
        # При увеличении порога level время растёт по закону 7.32 * level - 0.04 (в секундах)
        if level == level_max:
            level = 0
            coeff += 0.5
        if coeff >= FPS / 25:
            coeff = -1
            print(player.time / FPS)

        i = 0
        while i < len(particles) and iss:
            p = particles[i]
            if p.alive == -1:
                particles.pop(i)
            else:
                p.update()
                i += 1
        # Столкновение
        for m in garbage_group:
            if pygame.sprite.collide_mask(m, player):
                time = 400 + 200 * m.big
                particles.append(SpawnParticles((player.rect.centerx, player.rect.centery), 0, 0,
                                                [load_image('fallingsmoke.png', [-1], (x, x))
                                                 for x in (10, 20, 30)], change=lambda x: x % 5 == 0, times=time,
                                                follow_player=True, gravity=(-1, 0), count=40))
                if m.big == False:
                    player.de_baf(time)
                else:
                    player.de_baf(time, 2)
                m.kill()

        # Кометы
        star_picture = random.choice((star_red_picture, star_blue_picture, star_blue_picture))
        if randint(0, 1) and iss:
            for _ in range(3):
                Particle((randint((WIDTH // 3) * 2, WIDTH), randint(0, HEIGHT)), randint(-5, 0), randint(-5, 5),
                         [star_picture],
                         (-1, 0), dokill=False, groups=(stars_sprites, all_sprites))

        if iss:
            all_sprites.update()
        stars_sprites.draw(screen)
        player_group.draw(screen)
        particles_sprites.draw(screen)
        garbage_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def end_screen(time):
    intro_text = [f"Ваш счёт: {time}", "Нажмите что-нибудь, чтобы продолжить"]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 300
    mx_right = 0
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color(239, 239, 239))
        intro_rect = string_rendered.get_rect()
        mx_right = max(mx_right, intro_rect.x)
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    image = pygame.Surface([WIDTH, text_coord - 200])
    image.fill((0, 0, 0))
    image.set_alpha(50)
    screen.blit(image, (0, 300))
    timer = 0

    while True:
        timer += clock.tick() + 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN) and timer >= 100:
                return main_game(20)
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
        # (480, 384)
        super().__init__((player_group, all_sprites), load_image('fire.png', [-1], size=None, rotate=90), 4, 5,
                         pos_x,
                         pos_y,
                         switch=lambda x: x % 10 == 0, scale_to=(100, 100))
        self.speedy = 0
        self.acceleration = 4
        self.G = 9.8 / FPS
        self.slow = []
        self.other_image = load_image('hero.png', [-1], (500, 150))
        other_image = self.other_image.copy()
        self.image = other_image
        self.rect = self.image.get_rect()

        self.mask = pygame.mask.from_surface(self.image)

        self.rect.centerx = pos_x
        self.rect.centery = pos_y

        self.time = 0

    def move(self):
        # print(self.rect.x, self.rect.y)
        # self.speedy -= self.acceleration
        if len(self.slow) == 0:
            self.speedy -= self.acceleration
        else:
            value = 0
            for _, v in self.slow:
                value += v
            self.speedy -= self.acceleration - value

    def update(self):
        global coeff
        if self.rect.top <= -20:
            self.speedy = 1
        self.time += 1
        if self.rect.bottom >= HEIGHT + 20:
            for i in all_sprites:
                i.kill()
            coeff = 0.5
            end_screen(self.time / FPS)
        i = 0
        while i < len(self.slow):
            self.slow[i][0] -= 1
            if self.slow[i][0] == 0:
                self.slow.pop(i)
                i -= 1
            i += 1
        self.speedy += self.G
        self.rect.y += int(self.speedy)
        other_image = self.other_image.copy()
        other_image.blit(super().update(), (160, 30))
        self.image = other_image
        self.mask = pygame.mask.from_surface(self.image)
        # print(self.rect.x, self.rect.y)

    def de_baf(self, time=10 ** 3, value=1):
        self.slow.append([time, value])


screen_rect = (0, 0, WIDTH, HEIGHT)


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    '''fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))'''

    def __init__(self, pos, dx, dy, pictures, gravity=(0, 1), change=lambda x: x % 20 == 0, dokill=True,
                 groups=(all_sprites, particles_sprites)):
        super().__init__(*groups)
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

        self.dokill = dokill

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
            if self.image_ind == len(self.pictures) and self.dokill:
                self.kill()
                return
            self.image = self.pictures[self.image_ind % len(self.pictures)]
            x, y = self.rect.x, self.rect.y
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = x, y
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


class SpawnParticles:
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
        else:
            self.alive = -1


start_screen()
