# -*- coding: utf-8 -*-

# TODO писать, что товар закончился
# TODO check if planet num changed

import os
import sys
import random
import datetime
from random import randint
import pygame
from classes import PlanetView, Tile, PlayerOnPlanet, Camera, Garbage, SpawnParticles, Particle, FlyingPlayer, \
    AnimatedSprite

FPS = 50

# основной персонаж
player = None

tile_width = tile_height = 40

# группы спрайтов
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
particles_sprites = pygame.sprite.Group()
stars_sprites = pygame.sprite.Group()
garbage_group = pygame.sprite.Group()
is_not_break = None

iss = True

G = 9.8 / FPS

pygame.init()

SIZE = WIDTH, HEIGHT = (1200, 600)

screen = pygame.display.set_mode(SIZE)

clock = pygame.time.Clock()

running = True

upgrades = [
    {'грузоподъёмность': 100000, 'КПД двигателя': 0.25, 'защита': 1, 'скорость': 1},
    {'грузоподъёмность': 200000, 'КПД двигателя': 0.25, 'защита': 1, 'скорость': 1},
    {'грузоподъёмность': 300000, 'КПД двигателя': 0.5, 'защита': 1, 'скорость': 1},
    {'грузоподъёмность': 400000, 'КПД двигателя': 0.5, 'защита': 2, 'скорость': 1},
    {'грузоподъёмность': 500000, 'КПД двигателя': 0.75, 'защита': 2, 'скорость': 2},
    {'грузоподъёмность': 600000, 'КПД двигателя': 0.75, 'защита': 2, 'скорость': 2},
    {'грузоподъёмность': 700000, 'КПД двигателя': 1, 'защита': 3, 'скорость': 2},
    {'грузоподъёмность': 800000, 'КПД двигателя': 1, 'защита': 3, 'скорость': 2},
    {'грузоподъёмность': 900000, 'КПД двигателя': 1.5, 'защита': 3, 'скорость': 3},
    {'грузоподъёмность': 1000000, 'КПД двигателя': 1.5, 'защита': 3, 'скорость': 4},
]

goods = ['GOLD', 'FUEL', 'WATER', 'FOOD', 'IRON', 'PLUTONIUM', 'OIL', 'PETROLEUM', 'ARTJOMEUM']
goods_translated = ['золото', 'топливо', 'вода', 'еда', 'железо', 'плутоний', 'нефть', 'петролеум', 'артёмиум']

DEFAULT_GOODS_COSTS = {'FUEL': 1, 'GOLD': 3, 'WATER': 0.01, 'FOOD': 0.1, 'IRON': 0.5, 'PLUTONIUM': 2, 'OIL': 0.9,
                       'PETROLEUM': 6, 'ARTJOMEUM': 6}
expensive = {
    'GREEN': ['GOLD', 'IRON', 'FUEL', 'OIL'],
    'FIRE': ['FOOD', 'WATER'],
    'DESERT': ['FOOD', 'WATER'],
    'MOUNTAIN': ['FOOD', 'ARTJOMEUM', 'PETROLEUM'],
    'ICE': ['FUEL', 'OIL']
}
cheap = {
    'GREEN': ['WATER', 'FOOD'],
    'FIRE': ['GOLD', 'PLUTONIUM', 'FUEL'],
    'DESERT': ['FUEL', 'OIL', 'PETROLEUM'],
    'MOUNTAIN': ['GOLD', 'IRON'],
    'ICE': ['WATER', 'ARTJOMEUM']
}
COSTS = {}
for planet_type in ['GREEN', 'FIRE', 'DESERT', 'MOUNTAIN', 'ICE']:
    COSTS[planet_type] = DEFAULT_GOODS_COSTS.copy()
    for x in expensive[planet_type]:
        COSTS[planet_type][x] *= 2
    for x in cheap[planet_type]:
        COSTS[planet_type][x] /= 2
    mn = min(COSTS[planet_type].values())
    for k in COSTS[planet_type].keys():
        COSTS[planet_type][k] = int(COSTS[planet_type][k] * 1 / mn)

planets = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_on_planet_group = pygame.sprite.Group()

weight = {'FOOD': 1, 'WATER': 1, 'FUEL': 1, 'OIL': 1.5, 'GOLD': 10, 'PLUTONIUM': 5000, 'IRON': 3, 'PETROLEUM': 10000,
          'ARTJOMEUM': 10000}

default_message = []

text_to_blit = []

screen_rect = (-100, 0, WIDTH + 100, HEIGHT)
screen_rect_for_planets = (0, 0, WIDTH, HEIGHT)


def load_image(name, color_key_list=None, size=None, rotate=0):
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
    if color_key_list is not None:
        image = image.convert()
        if color_key_list[0] == -1:
            color_key_list[0] = image.get_at((0, 0))
        image.set_colorkey(color_key_list[0])
        color_key_list.pop()
        if len(color_key_list) > 0:
            image = load_image(image, color_key_list=color_key_list, size=size)
    else:
        image = image.convert_alpha()
    if size is not None:
        image = pygame.transform.scale(image, size)
    return image


merchants_images = [load_image('merchant.png', [-1])]  # TODO make many pictures of merchants

mystery_merchants_images = [load_image('merchant.png', [-1], rotate=90)]

# TODO make cool planet images
planet_images = [load_image('garbage.png', rotate=i, color_key_list=[-1]) for i in range(0, 180, 30)]

player_x, player_y = None, None

tile_images = {
    '#': load_image('box.png'),
    '.': load_image('grass.png')
}

# TODO find picture for player on planet
player_image = load_image('player_on_planet.png', [-1])

exit_image = load_image('exit.png', size=(tile_width, tile_height))

pictures_of_goods = {x: pygame.transform.scale(load_image(f'{x.lower()}.png'), (65, 65)) for x in goods}

# TODO picture of upgrade
upgrade_image = load_image('upgrade.png', size=(65, 65))

star_red_picture = load_image('star_red.png', [-1], size=(10, 10))
star_blue_picture = load_image('star_blue.png', [-1], size=(10, 10))


def new_game():
    global PLANETS, PLANET_NAMES, PLANET_TYPE, MERCHANTS, ship_level, now_planet, have
    ship_level = 0
    planet_generator(7, 50, 50)
    now_planet = 0
    have = {x: 0 for x in goods}

    have['FUEL'] = 1000

    have['GOLD'] = 100


def save(name):
    with open(name, mode='w') as f:
        print(str(PLANETS))
        print(str(PLANET_NAMES))
        print(str(PLANET_TYPE))
        print(str(MERCHANTS))
        print(str(ship_level))
        print(str(now_planet))
        print(str(have))
        f.write(f'global PLANETS, PLANET_NAMES, PLANET_TYPE, MERCHANTS, ship_level, now_planet, have\n'
                f'PLANETS = {str(PLANETS)}\n'
                f'PLANET_NAMES = {str(PLANET_NAMES)}\n'
                f'PLANET_TYPE = {str(PLANET_TYPE)}\n'
                f'MERCHANTS = {str(MERCHANTS)}\n'
                f'ship_level = {ship_level}\n'
                f'now_planet = {now_planet}\n'
                f'have = {str(have)}\n')


def load(name):
    global PLANETS, PLANET_NAMES, PLANET_TYPE, MERCHANTS, ship_level, now_planet, have
    print(1213)
    with open(name, mode='r') as f:
        global PLANETS, PLANET_NAMES, PLANET_TYPE, MERCHANTS, ship_level, now_planet, have
        exec('\n'.join(f.readlines()))
    print(PLANETS, PLANET_NAMES, PLANET_TYPE, MERCHANTS, ship_level, now_planet, have, sep='\n')


# . is empty
# # is wall
# @ is player
# $ is merchant
# <... is goods for sale(player can buy them)
# >... is empty place that needs goods(player can sell them)
# s space ship
# l press enter to leave

# zone of player spawning on planet
'''
# # # # # # # # #
# . . . . . . . #
# . . s . . @ . #
# . . l . . . . #
# . . . . . . . #
# . . . . . . . #
'''


def arr_from_str(s):
    return [x.split(' ') for x in s.split('\n')]


def generate_name(k):
    letters1 = list('еэуиоа')
    letters2 = list('квртйсждфхлзцбнм')
    name = random.choice(letters1 + letters2)
    while len(name) < k:
        if name[-1] in letters1:
            name += random.choice(letters2)
        else:
            if randint(0, 1):
                name += random.choice(letters1)
            elif len(name) != k - 1:
                name += random.choice(letters1) + random.choice(letters1)
    return name


def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)


def optimize(a, b):
    d = gcd(a, b)
    return a // d, b // d


def generate_merchant(planet_type):
    res = []
    for _ in range(randint(2, 4)):
        x, y = random.choice(goods), random.choice(goods)
        if x != y:
            res.append((x, y, *optimize(COSTS[planet_type][y] + randint(0, 2), COSTS[planet_type][x] + randint(0, 10))))
    return res


def planet_generator(n, w, h):
    global PLANETS, PLANET_NAMES, PLANET_TYPE, MERCHANTS

    PLANETS = []
    PLANET_NAMES = []
    PLANET_TYPE = []
    MERCHANTS = []
    for i in range(n):
        name = generate_name(randint(3, 5))
        name += str(randint(10, 99))
        PLANET_NAMES.append(name.upper())
        PLANET_TYPE.append(['GREEN', 'FIRE', 'DESERT', 'MOUNTAIN', 'ICE'][randint(0, 4)])

    staring_zone = arr_from_str(
        '# # # # # # # # #\n'
        '# . . . . . . . #\n'
        '# . . s . . @ . #\n'
        '# . . l . . . . #\n'
        '# . . . . . . . #\n'
        '# . . . . . . . #'
    )
    small_shop_down = arr_from_str(
        '# # # # #\n'
        '# . $ . #\n'
        '# # # # #\n'
        '# . = . #\n'
        '# . . . #'
    )
    small_shop_up = small_shop_down[::-1]

    middle_shop1_down = arr_from_str(
        '# # # # # # #\n'
        '# . $ . $ . #\n'
        '# # # # # # #\n'
        '# . = . = . #\n'
        '# . . . . . #\n'
        '# # # . # # #'
    )

    middle_shop1_up = middle_shop1_down[::-1]

    middle_shop2_down = arr_from_str(
        '# # # # # # #\n'
        '# . $ . $ . #\n'
        '# # # # # # #\n'
        '# . = . = . #\n'
        '# . . . . . #\n'
        '# # # . # # #'
    )

    middle_shop2_up = middle_shop2_down[::-1]

    # TODO ask if anyone understand what is happening over here

    big_shop_down = arr_from_str(
        '# # # # # # # # #\n'
        '# $ # . . . # $ #\n'
        '# # = . . . = # #\n'
        '# . . . . . . . #\n'
        '# . . . . . . . #\n'
        '# . . . . . . . #\n'
        '# # = . . . = # #\n'
        '# $ # . . . # $ #\n'
        '# # # . . . # # #'
    )

    big_shop_up = big_shop_down[::-1]

    mystery_shop = arr_from_str(
        '# # #\n'
        '# ? #\n'
        '# # #\n'
        '# u #'
    )

    obstacles = [
        arr_from_str(
            '# # # # . .\n'
            '. # . # # #\n'
            '# # . # . .'
        ),
        arr_from_str(
            '# #\n'
            '# #'
        ),
        arr_from_str(
            '. # .\n'
            '# # #\n'
            '. # .'
        ),
        arr_from_str(
            '# # .\n'
            '. # #\n'
            '# . #'
        ),
        arr_from_str(
            '# . #\n'
            '# # .\n'
            '. # #'
        ),
        arr_from_str(
            '# #\n'
            '# .'
        ),
        arr_from_str(
            '#'
        )
    ]

    terrain = [small_shop_up, small_shop_down, middle_shop1_down, middle_shop2_down, middle_shop1_up, middle_shop2_up,
               big_shop_down, big_shop_up, mystery_shop] + obstacles

    for _ in range(n):
        field = [['' for i in range(w)] for j in range(h)]
        for i in range(len(staring_zone)):
            for j in range(len(staring_zone[i])):
                field[i][j] = staring_zone[i][j]

        problems = 0
        while problems < 20:
            obj = random.choice(terrain)
            i, j = randint(0, h), randint(0, w)
            ok = True
            for i1 in range(i - 2, i + len(obj) + 2):
                if not ok:
                    break
                for j1 in range(j - 1, j + len(obj[0]) + 2):
                    if field[i1 % h][j1 % w] != '':
                        problems += 1
                        ok = False
                        break
            else:
                problems = 0
                for i1 in range(i, i + len(obj)):
                    for j1 in range(j, j + len(obj[0])):
                        field[i1 % h][j1 % w] = obj[i1 - i][j1 - j]
                        if field[i1 % h][j1 % w] == '=':
                            merchant = {'name': generate_name(randint(3, 5)).capitalize(),
                                        'home planet': random.choice(PLANET_NAMES),
                                        'image_num': randint(0, len(merchants_images) - 1),
                                        'change': generate_merchant(PLANET_TYPE[_]),
                                        'last_trade': None}
                            MERCHANTS.append(merchant)
                            field[i1 % h][j1 % w] = f'={len(MERCHANTS) - 1}'
                        elif field[i1 % h][j1 % w] == 'u':
                            merchant = {'name': generate_name(randint(2, 2)).capitalize(),
                                        'home planet': random.choice(PLANET_NAMES),
                                        'image_num': randint(0, len(merchants_images) - 1),
                                        'change': 'UPGRADE',
                                        'last_trade': None}
                            MERCHANTS.append(merchant)
                            field[i1 % h][j1 % w] = f'u{len(MERCHANTS) - 1}'

        for i in range(len(field)):
            for j in range(len(field[i])):
                if field[i][j] == '':
                    field[i][j] = '.'
                if field[i][j][0] == '=':
                    for i2 in range(i - 2, i + 3):
                        for j2 in range(j - 2, j + 3):
                            print(field[i2 % h][j2 % w], end=' ')
                            if abs(i2 - i) + abs(j2 - j) <= 2:
                                if field[i2 % h][j2 % w] == '$':
                                    field[i2 % h][j2 % w] = f'${field[i][j][1:]}'
                        print()
                    print()
                if field[i][j][0] == 'u':
                    for i2 in range(i - 2, i + 3):
                        for j2 in range(j - 2, j + 3):
                            if abs(i2 - i) + abs(j2 - j) <= 2:
                                if field[i2 % h][j2 % w] == '?':
                                    field[i2 % h][j2 % w] = f'?{field[i][j][1:]}'
        PLANETS.append(field)
        for row in field:
            print(row)
        print()


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
                new_game()
                return map_selection(now_planet)
        pygame.display.flip()
        clock.tick(FPS)


def calculate_distance(x1, y1, x2, y2):
    return round(0.5 * ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)


# TODO planet images


# TODO save sometimes

def map_selection(player_planet_num):
    global player_planet
    player_planet = player_planet_num
    # TODO find space.png for background
    fon = pygame.Surface([WIDTH, HEIGHT])
    fon.fill((0, 0, 0))
    screen.blit(fon, (0, 0))
    # fon = pygame.transform.scale(load_image('space.png'), (WIDTH, HEIGHT))

    screen.blit(fon, (0, 0))
    # planets are spawning
    for i in range(len(PLANET_NAMES)):
        if i == player_planet:
            PlanetView((randint(0, WIDTH - 100), randint(0, HEIGHT - 100)), i, player_here=True)
        else:
            while True:
                self = PlanetView((randint(0, WIDTH - 100), randint(0, HEIGHT - 100)), i, player_here=False)
                for sprite in planets:
                    if self is not sprite:
                        if pygame.sprite.collide_rect(self, sprite):
                            is_kill = True
                            break
                else:
                    is_kill = False
                if is_kill:
                    self.kill()
                else:
                    break

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for planet in planets:
                    if planet.rect.collidepoint(*event.pos):
                        save('file.txt')
                        if planet.player_here:
                            planet_game(planet.num)
                            save('file.txt')
                        else:
                            # TODO check if player is sure

                            now_planet = None
                            for now_planet in planets:
                                if now_planet.player_here:
                                    break
                            wasted_fuel = calculate_distance(now_planet.rect.centerx, now_planet.rect.centery,
                                                             planet.rect.centerx,
                                                             int(planet.rect.centery) / upgrades[ship_level][
                                                                 'КПД двигателя'])

                            res = flight_game(20)
                            for start_planet in planets:
                                if start_planet.player_here:
                                    start_planet.player_here = False
                                    break
                            if res:
                                have['FUEL'] -= wasted_fuel
                            else:
                                planet = random.choice(list(planets))
                            planet.player_here = True
                            player_planet = planet.num
                            save('file.txt')
                            break
            elif event.type == pygame.KEYDOWN:
                print(123)
                if event.key == pygame.K_l:
                    print(56)
                    load('file.txt')
        # TODO show where we are(design)
        screen.blit(fon, (0, 0))
        planets.draw(screen)
        for planet in planets:
            if planet.player_here:
                pygame.draw.circle(screen, (0, 255, 0), planet.rect.center, 10)
                break
        show_parameters(screen)
        pygame.display.flip()
        clock.tick(FPS)


def generate_level(level, level_type):
    global player_x, player_y
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('.', x, y)
            elif level[y][x] == '#':
                Tile('#', x, y)
            elif level[y][x] == '@':
                Tile('.', x, y)
                new_player = PlayerOnPlanet(x, y)
                player_x = x
                player_y = y
            elif level[y][x][0] == '$':
                Tile('.', x, y)
                Tile(level[y][x], x, y)
            elif level[y][x][0] == '?':
                Tile('.', x, y)
                Tile(level[y][x], x, y)
            elif level[y][x] == 's':
                Tile('s', x, y)
            elif level[y][x] == 'l':
                Tile('l', x, y)
            elif level[y][x][0] == '=':
                Tile(level[y][x], x, y)
                if MERCHANTS[int(level[y][x][1:])]['last_trade'] is not None and datetime.datetime.now() - \
                        MERCHANTS[int(level[y][x][1:])]['last_trade'] > datetime.timedelta(minutes=10):
                    MERCHANTS[int(level[y][x][1:])]['change'] = generate_merchant(level_type)
                MERCHANTS[int(level[y][x][1:])]['last_trade'] = datetime.datetime.now()
            elif level[y][x][0] == 'u':
                Tile(level[y][x], x, y)

    # вернем игрока, а также размер поля в клетках
    return new_player, x + 1, y + 1


def calc_weight():
    return sum([weight[x] * have[x] for x in goods])


def blit_text(screen):
    while len(text_to_blit) > 2:
        text_to_blit.pop(0)
    font = pygame.font.Font(None, 25)
    text_top = 0
    res = []
    for message_ind in range(len(text_to_blit)):
        res.append('')
        if message_ind == len(text_to_blit) - 1:
            res.append('    Новое сообщение:')
        res.extend(text_to_blit[message_ind])
    message = default_message.copy()
    message.extend(res)
    for line in message:
        text = font.render(line, True, (255, 255, 255))
        text_x = WIDTH - 200
        text_y = text_top
        text_w = text.get_width()
        text_h = text.get_height()

        rect = pygame.Surface([text_w, text_h])
        rect.fill((0, 0, 0))
        rect.set_alpha(99)
        screen.blit(rect, (text_x, text_y))

        screen.blit(text, (text_x, text_y))
        text_top += 20


def line_text(text, line_size=20):
    lines = ['']
    i = 0
    for word in text.split():
        if len(lines[i]) + len(word) + 1 < line_size:
            if lines[i] != '':
                lines[i] += ' ' + word
            else:
                lines[i] += word
        else:
            lines.append(word)
            i += 1
    return lines


def send_message(text):
    lines = line_text(text)
    text_to_blit.append(lines)


def find_tile(player):
    for tile in tiles_group:
        if pygame.sprite.collide_rect(tile, player):
            return tile
    return None


def show_action(player):
    tile = find_tile(player)
    if tile.type == 'l':
        send_message('Улететь хочешь, Enter жми.')
    elif tile.type[0] == '=':
        send_message('Меняться будем, жми Enter.')
    elif tile.type[0] == 'u':
        send_message('Меняться будем, жми Enter.')


def get_info_about_goods_to_buy(good, planet):
    return [max(1, x + randint(-1, 1)) for x in info_about_goods_to_buy[goods[int(good)]][planet]]


def get_info_about_goods_to_sell(good, planet):
    return [max(1, x + randint(-1, 1)) for x in info_about_goods_to_sell[goods[int(good)]][planet]]


def show_parameters(screen):
    font = pygame.font.Font(None, 50)
    text = font.render('; '.join([f'{name}:{have[name]}' for name in have.keys()]), True, (255, 255, 255))
    text_x = WIDTH // 2 - text.get_width() // 2
    text_y = 0
    text_w = text.get_width()
    text_h = text.get_height()

    rect = pygame.Surface([text_w, text_h])
    rect.fill((0, 0, 0))
    rect.set_alpha(90)
    screen.blit(rect, (text_x, text_y))

    screen.blit(text, (text_x, text_y))


'''pictures_of_goods = {
    'GOLD': load_image('gold.png'),
    'FUEL': load_image('fuel.png'),
    'WATER': load_image('water.png'),
    'FOOD': load_image('food.png'),
    'IRON': load_image('iron.png'),
    'PLUTONIUM': load_image('plutonium.png'),
    'OIL': load_image('oil.png'),
    'PETROLEUM': load_image('petroleum.png'),
    'ARTJOMEUM': load_image('artjomeum.png')
}'''


def draw_text(x, y, text, color, screen, font, line_size=20, fon_color=None):
    Font = pygame.font.Font(None, font)
    message_top = y
    text_top = y
    text_x = x
    mxw = 0
    to_blit = []
    for line in line_text(text, line_size):
        text = Font.render(line, True, color)
        text_y = text_top
        text_w = text.get_width()
        text_h = text.get_height()
        # screen.blit(text, (text_x, text_y))
        to_blit.append((text, text_x, text_y))
        text_top += font // 2 + 8
    message_bottom = text_top + font // 4 - 10
    message_left = x
    message_right = Font.render('a' * line_size, True, color).get_width() + x
    if fon_color is not None:
        pygame.draw.rect(screen, fon_color,
                         ((message_left, message_top), (message_right - message_left, message_bottom - message_top)))
    for d in to_blit:
        screen.blit(d[0], (d[1], d[2]))
    return message_bottom + 5, Font.render('a' * line_size, True, color).get_width()


def trade_game(screen, merchant, player):
    print(have)
    print()
    print(merchant)
    # TODO show inventory
    window_w = 400
    window_h = 600

    buttons = []
    k, w = draw_text((WIDTH - window_w) // 2 + 10, 10,
                     f"Здравтсвуй, путник. Величать меня {merchant['name']} можешь."
                     f" С планеты {merchant['home planet']} я есть.",
                     (255, 255, 255), screen, 50, line_size=20, fon_color=(128, 128, 128))
    k, w = draw_text((WIDTH - window_w) // 2 + 10, k, "К лучшему меняемся:",
                     (255, 255, 255), screen, 50, line_size=20, fon_color=(128, 128, 128))
    if merchant['change'] != 'UPGRADE':
        for offer in merchant['change']:
            screen.blit(pictures_of_goods[offer[1]], ((WIDTH - window_w) // 2 + 10, k))
            screen.blit(pictures_of_goods[offer[0]], ((WIDTH + window_w) // 2 - 75, k))
            button = [(WIDTH - window_w) // 2 + 90, k]
            k, w = draw_text((WIDTH - window_w) // 2 + 90, k,
                             f"Мне ты давать {offer[3]} {goods_translated[goods.index(offer[1])]},"
                             f" тебе давать я {offer[2]} {goods_translated[goods.index(offer[0])]}",
                             (255, 255, 255), screen, 30, line_size=20, fon_color=(128, 128, 128))
            button.append(w)
            button.append(k - button[1])
            buttons.append(button)
    else:
        for x in ['PETROLEUM', 'ARTJOMEUM']:
            screen.blit(pictures_of_goods[x], ((WIDTH - window_w) // 2 + 10, k))
            screen.blit(upgrade_image, ((WIDTH + window_w) // 2 - 75, k))
            button = [(WIDTH - window_w) // 2 + 90, k]
            k, w = draw_text((WIDTH - window_w) // 2 + 90, k,
                             f"Мне ты давать {ship_level + 1} {goods_translated[goods.index(x)]},"
                             f" тебе давать я корабля улучшение.",
                             (255, 255, 255), screen, 30, line_size=20, fon_color=(128, 128, 128))
            button.append(w)
            button.append(k - button[1])
            buttons.append(button)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(len(buttons)):
                    if pygame.Rect((buttons[i][0], buttons[i][1]), (buttons[i][2], buttons[i][3])).collidepoint(
                            event.pos):
                        print(i)
                        if merchant['change'] != 'UPGRADE':
                            player.change(merchant['change'][i])
                        else:
                            player.change(['PETROLEUM', 'ARTJOMEUM'][i])
                        if randint(0, 5) == 0:
                            buttons.pop(-1)
                            merchant['change'].pop(i)
                        break

        screen.fill((0, 0, 0))

        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        particles_sprites.update()
        particles_sprites.draw(screen)
        show_parameters(screen)
        blit_text(screen)

        shadow = pygame.Surface([WIDTH, HEIGHT])
        shadow.fill((0, 0, 0))
        shadow.set_alpha(164)
        screen.blit(shadow, (0, 0))

        pygame.draw.rect(screen, (23, 23, 23), (((WIDTH - window_w) // 2, 0), (window_w, window_h)))

        k, w = draw_text((WIDTH - window_w) // 2 + 10, 10,
                         f"Здравтсвуй, путник. Величать меня {merchant['name']} можешь."
                         f" С планеты {merchant['home planet']} я есть.",
                         (255, 255, 255), screen, 50, line_size=20, fon_color=(128, 128, 128))
        k, w = draw_text((WIDTH - window_w) // 2 + 10, k, "К лучшему меняемся:",
                         (255, 255, 255), screen, 50, line_size=20, fon_color=(128, 128, 128))
        if merchant['change'] != 'UPGRADE':
            for offer in merchant['change']:
                screen.blit(pictures_of_goods[offer[1]], ((WIDTH - window_w) // 2 + 10, k))
                screen.blit(pictures_of_goods[offer[0]], ((WIDTH + window_w) // 2 - 75, k))
                k, w = draw_text((WIDTH - window_w) // 2 + 90, k,
                                 f"Мне ты давать {offer[3]} {goods_translated[goods.index(offer[1])]}"
                                 f", тебе давать я {offer[2]} {goods_translated[goods.index(offer[0])]}",
                                 (255, 255, 255), screen, 30, line_size=20, fon_color=(128, 128, 128))
        else:
            for x in ['PETROLEUM', 'ARTJOMEUM']:
                screen.blit(pictures_of_goods[x], ((WIDTH - window_w) // 2 + 10, k))
                screen.blit(upgrade_image, ((WIDTH + window_w) // 2 - 75, k))
                k, w = draw_text((WIDTH - window_w) // 2 + 90, k,
                                 f"Мне ты давать {ship_level + 1} {goods_translated[goods.index(x)]},"
                                 f" тебе давать я корабля улучшение.",
                                 (255, 255, 255), screen, 30, line_size=20, fon_color=(128, 128, 128))
        pygame.display.flip()
        clock.tick(FPS)


def planet_game(num):
    global default_message, text_to_blit
    planet = PLANETS[num]
    default_message = line_text(f'Приветствуем вас на планете {PLANET_NAMES[num]}')
    text_to_blit = []
    particles = []
    global level_x, level_y
    player, level_x, level_y = generate_level(planet, PLANET_TYPE[num])
    camera = Camera()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    pass
                elif event.key == pygame.K_RIGHT:
                    player.move(tile_width, 0)
                    show_action(player)
                elif event.key == pygame.K_LEFT:
                    player.move(-tile_width, 0)
                    show_action(player)
                elif event.key == pygame.K_DOWN:
                    player.move(0, tile_height)
                    show_action(player)
                elif event.key == pygame.K_UP:
                    player.move(0, -tile_height)
                    show_action(player)
                elif event.key == pygame.K_RETURN:
                    # TODO smarter system of finding tile player on
                    tile = find_tile(player)
                    if tile.type == 'l':
                        for sp in all_sprites:
                            sp.kill()
                        return
                    elif tile.type[0] == '=':
                        trade_game(screen, MERCHANTS[int(tile.type[1:])], player)
                    elif tile.type[0] == 'u':
                        trade_game(screen, MERCHANTS[int(tile.type[1:])], player)
        # изменяем ракурс камеры
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        screen.fill((0, 0, 0))
        for p in particles:
            p.update()

        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        particles_sprites.update()
        particles_sprites.draw(screen)
        show_parameters(screen)
        blit_text(screen)
        pygame.display.flip()
        clock.tick(FPS)


def flight_game(level_max):
    global player, iss
    player = FlyingPlayer(100, HEIGHT // 2)
    particles = []
    sec = 50
    ratio = 0.5
    level = 0

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
        if iss and ratio != -1:
            sec += 1
        if sec == int(FPS / ratio):
            sec = 0
            level += 1
            big = randint(0, 10) == 0
            Garbage((WIDTH, randint(20 - 10 * big, HEIGHT - 110 * (1 + big))), big=big)
        # При увеличении порога level время растёт по закону 7.32 * level - 0.04 (в секундах)
        if level == level_max:
            level = 0
            ratio += 0.5
        if ratio >= FPS / 25:
            ratio = -1
        if len(garbage_group) == 0 and ratio == -1:
            for sprite in all_sprites:
                sprite.kill()
            return True

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
                                                [load_image('falling_smoke.png', [-1], (x, x))
                                                 for x in (10, 20, 30)], change=lambda x: x % 5 == 0, times=time,
                                                follow_player=True, gravity=(-1, 0), count=40))
                if not m.big:
                    player.de_baf(time, 1 / upgrades[ship_level]['защита'])
                else:
                    player.de_baf(time, 2 / upgrades[ship_level]['защита'])
                m.kill()

        # Кометы
        star_picture = random.choice((star_red_picture, star_blue_picture, star_blue_picture))
        if randint(0, 1) and iss:
            for _ in range(3):
                Particle((randint((WIDTH // 3) * 2, WIDTH), randint(0, HEIGHT)), randint(-5, 0), randint(-5, 5),
                         [star_picture],
                         (-1, 0), do_kill=False, groups=(stars_sprites, all_sprites))

        if iss:
            all_sprites.update()
            if not is_not_break:
                for i in all_sprites:
                    i.kill()
                return False
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


# do not need this


start_screen()
