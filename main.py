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
is_not_break = None

iss = True

G = 9.8 / FPS

pygame.init()

SIZE = WIDTH, HEIGHT = (1200, 600)

screen = pygame.display.set_mode(SIZE)

clock = pygame.time.Clock()

running = True

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


def planet_generator(n, w, h):
    global PLANETS, PLANET_NAMES
    letters1 = list('eyuioa')
    letters2 = list('qwrtpsjdfghklzxcvbnm')
    PLANETS = []
    PLANET_NAMES = []
    for i in range(n):
        name = random.choice(letters1)
        k = randint(5, 10)
        while len(name) < k:
            if name[-1] in letters1:
                name += random.choice(letters2)
            else:
                if randint(0, 1):
                    name += random.choice(letters1)
                elif len(name) != k - 1:
                    name += random.choice(letters1) + random.choice(letters1)
        name += str(randint(100, 999))
        PLANET_NAMES.append(name.upper())
    print(PLANET_NAMES)
    # TODO generate maps
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
        '# <;1 . >;1 #\n'
        '# . . . #'
    )
    small_shop_up = small_shop_down[::-1]

    middle_shop1_down = arr_from_str(
        '# # # # # # #\n'
        '# . $ . $ . #\n'
        '# # # # # # #\n'
        '# <;1 . >;1 . <;1 #\n'
        '# . . . . . #\n'
        '# # # . # # #'
    )

    middle_shop1_up = middle_shop1_down[::-1]

    middle_shop2_down = arr_from_str(
        '# # # # # # #\n'
        '# . $ . $ . #\n'
        '# # # # # # #\n'
        '# >;1 . <;1 . >;1 #\n'
        '# . . . . . #\n'
        '# # # . # # #'
    )

    middle_shop2_up = middle_shop2_down[::-1]

    big_shop_down = arr_from_str(
        '# # # # # # # # #\n'
        '# $ # . <;1 . # $ #\n'
        '# # # . . . # # #\n'
        '# . . <;1 . <;1 . . #\n'
        '# >;1 . . . . . >;1 #\n'
        '# . . . >;1 . . . #\n'
        '# # # . . . # # #\n'
        '# $ # . . . # $ #\n'
        '# # # . . . # # #'
    )

    big_shop_up = big_shop_down[::-1]

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
               big_shop_down, big_shop_up] + obstacles

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
                for j1 in range(j - 1, j + len(obj[0]) + 1):
                    print(field[i1 % h][j1 % w], end='\t')
                    if field[i1 % h][j1 % w] != '':
                        problems += 1
                        ok = False
                        break
                print()
            else:
                print(obj)
                print(i, j)
                print(*[row for row in field], sep='\n')
                # input()
                problems = 0
                for i1 in range(i, i + len(obj)):
                    for j1 in range(j, j + len(obj[0])):
                        field[i1 % h][j1 % w] = obj[i1 - i][j1 - j]
        for i in range(len(field)):
            for j in range(len(field[i])):
                if field[i][j] == '':
                    field[i][j] = '.'
        PLANETS.append(field)
        print(*[row for row in field], sep='\n')
        print()

    # TODO generate costs


planet_generator(7, 50, 50)


# TODO add more different planets


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


# TODO add more goods
goods = {
    0: 'GOLD',
    1: 'FUEL',
    2: 'WATER',
    3: 'IRON',
    4: 'PLUTONIUM',
    5: 'OIL',
    6: 'PETROLEUM',
    7: 'ARTJOMEUM',
    8: 'FOOD'
}

# TODO add pictures of goods when player is buying them
pictures_of_goods = {
    'GOLD': load_image('gold.png'),
    'FUEL': load_image('fuel.png'),
    'IRON': load_image('iron.png'),
    'PLUTONIUM': load_image('plutonium.png'),
    'OIL': load_image('oil.png'),
    'PETROLEUM': load_image('petroleum.png'),
    'ARTJOMEUM': load_image('artjomeum.png'),
    'WATER': load_image('water.png'),
    'FOOD': load_image('food.png')
}

# TODO set adecvatic cost and count for goods on each planet
info_about_goods_to_buy = {
    'GOLD': {i: [1, 20] for i in range(len(PLANETS))},
    'FUEL': {i: [1, 1] for i in range(len(PLANETS))},
    'IRON': {i: [3, 10] for i in range(len(PLANETS))},
    'PLUTONIUM': {i: [1, 1] for i in range(len(PLANETS))},
    'OIL': {i: [3, 10] for i in range(len(PLANETS))},
    'PETROLEUM': {i: [1, 1] for i in range(len(PLANETS))},
    'ARTJOMEUM': {i: [1, 1] for i in range(len(PLANETS))},
    'WATER': {i: [3, 10] for i in range(len(PLANETS))},
    'FOOD': {i: [3, 10] for i in range(len(PLANETS))}
}

info_about_goods_to_sell = {
    'GOLD': {i: [1, 30] for i in range(len(PLANETS))},
    'FUEL': {i: [1, 3] for i in range(len(PLANETS))},
    'IRON': {i: [3, 30] for i in range(len(PLANETS))},
    'PLUTONIUM': {i: [1, 1] for i in range(len(PLANETS))},
    'OIL': {i: [3, 30] for i in range(len(PLANETS))},
    'PETROLEUM': {i: [1, 1] for i in range(len(PLANETS))},
    'ARTJOMEUM': {i: [1, 1] for i in range(len(PLANETS))},
    'WATER': {i: [3, 30] for i in range(len(PLANETS))},
    'FOOD': {i: [3, 30] for i in range(len(PLANETS))}
}

# TODO find picture of a table where player puts goods if he wants to sell them
table = load_image('table.png')


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
        self.rect.y += +randint(-4, 4)
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
                return map_selection()
        pygame.display.flip()
        clock.tick(FPS)


planets = pygame.sprite.Group()

# TODO make cool planet images
planet_images = [load_image('garbage.png', rotate=i, colorkeylist=[-1]) for i in range(0, 210, 30)]


class PlanetView(pygame.sprite.Sprite):
    def __init__(self, pos, num, player_here=False, **other):
        super().__init__(planets)
        self.image = pygame.transform.scale(planet_images[num], (100, 100))
        self.rect = self.image.get_rect()
        self.num = num
        self.rect.x, self.rect.y = pos[0], pos[1]
        self.player_here = player_here


def map_selection():
    # TODO find space.png for background
    fon = pygame.Surface([WIDTH, HEIGHT])
    fon.fill((0, 0, 0))
    screen.blit(fon, (0, 0))
    # fon = pygame.transform.scale(load_image('space.png'), (WIDTH, HEIGHT))

    screen.blit(fon, (0, 0))
    # planets are spawning
    for i in range(7):
        if i == 0:
            PlanetView((randint(0, WIDTH - 20), randint(0, HEIGHT - 20)), i, player_here=True)
        else:
            while True:
                self = PlanetView((randint(0, WIDTH - 20), randint(0, HEIGHT - 20)), i, player_here=False)
                for sprite in planets:
                    if pygame.sprite.collide_rect(self, sprite) and not self.rect.colliderect(screen_rect_for_planets):
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
                        if planet.player_here:
                            planet_game(planet.num)
                        else:
                            res = flight_game(20)
                            for start_planet in planets:
                                if start_planet.player_here:
                                    start_planet.player_here = False
                                    break
                            if res:
                                planet.player_here = True
                            else:
                                random.choice(list(planets)).player_here = True
                            break
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


player_x, player_y = None, None


def generate_level(level):
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
            elif level[y][x] == '$':
                Tile('.', x, y)
                Tile('$', x, y)
            elif level[y][x] == 's':
                Tile('s', x, y)
            elif level[y][x] == 'l':
                Tile('l', x, y)
            else:
                s = level[y][x]
                Tile(s, x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x + 1, y + 1


tile_images = {
    '#': load_image('box.png'),
    '.': load_image('grass.png')
}

# TODO find picture for player on planet
player_image = load_image('player_on_planet.png', [-1])

tile_width = tile_height = 40

tiles_group = pygame.sprite.Group()
player_on_planet_group = pygame.sprite.Group()

exit_image = load_image('exit.png', size=(tile_width, tile_height))
merchants = [load_image('merchant.png', [-1])]  # TODO make many pictures of merchants


# TODO tile.save and empty tiles transforming into < or >

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        self.type = tile_type
        self.pos_x, self.pos_y = pos_x, pos_y
        super().__init__(tiles_group, all_sprites)
        if tile_type == 's':
            # TODO show to player that ship is here(design)
            self.image = load_image('hero.png', [-1], (3 * tile_width, 3 * tile_height))
            self.rect = self.image.get_rect()
            self.rect.bottom = tile_height * pos_y + tile_height
            self.rect.centerx = tile_width * pos_x + tile_width // 2
        elif tile_type == 'l':
            self.image = exit_image
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)
        elif tile_type == '$':
            self.image = pygame.transform.scale(merchants[randint(0, len(merchants) - 1)], (tile_width, tile_height))
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)
        elif tile_type[0] not in '<>':
            self.image = pygame.transform.scale(tile_images[tile_type], (tile_width, tile_height))
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)
        elif tile_type[0] == '<':
            if tile_type[1] == ';':
                self.type = self.type[:1] + ';' + str(int(self.type[2:]) - 1)
                if self.type == '<;0':
                    self.type = '<' + str(randint(0, len(goods) - 1))
                    self.image = pygame.transform.scale(pictures_of_goods[goods[int(self.type[1:])]],
                                                        (tile_width, tile_height))
                    self.rect = self.image.get_rect().move(
                        tile_width * pos_x, tile_height * pos_y)
                else:
                    self.image = pygame.transform.scale(table, (tile_width, tile_height))
                    self.rect = self.image.get_rect().move(
                        tile_width * pos_x, tile_height * pos_y)
            else:
                self.image = pygame.transform.scale(pictures_of_goods[goods[int(tile_type[1:])]],
                                                    (tile_width, tile_height))
                self.rect = self.image.get_rect().move(
                    tile_width * pos_x, tile_height * pos_y)
        elif tile_type[0] == '>':
            if tile_type[1] == ';':
                self.type = self.type[:1] + ';' + str(int(self.type[2:]) - 1)
                if self.type == '>;0':
                    self.type = '>' + str(randint(0, len(goods) - 1))
                    self.image = pygame.transform.scale(table, (tile_width, tile_height))
                    self.rect = self.image.get_rect().move(
                        tile_width * pos_x, tile_height * pos_y)
                else:
                    self.image = pygame.transform.scale(table, (tile_width, tile_height))
                    self.rect = self.image.get_rect().move(
                        tile_width * pos_x, tile_height * pos_y)
            else:
                self.image = pygame.transform.scale(table, (tile_width, tile_height))
                self.rect = self.image.get_rect().move(
                    tile_width * pos_x, tile_height * pos_y)

    def save(self, num):
        if PLANETS[num][self.pos_y][self.pos_x] != '@':
            PLANETS[num][self.pos_y][self.pos_x] = self.type


have = {'FUEL': 1000, 'GOLD': 0, 'WATER': 0}


class PlayerOnPlanet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        global have
        super().__init__(player_group, all_sprites)
        self.image = pygame.transform.scale(player_image, (
            tile_width, tile_height))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y
        if len([1 for q in pygame.sprite.spritecollide(self, all_sprites, False) if
                type(q) == Tile and q.type == '#']):
            self.rect.x -= x
            self.rect.y -= y

    def buy(self, name, cost, count):
        global have
        name = goods[int(name)]
        if cost <= have['FUEL']:
            have['FUEL'] -= cost
            have[name] += count
        else:
            send_message(f'You have not enough FUEL to buy {count} {name} for {cost} FUEL')

    def sell(self, name, cost, count):
        global have
        name = goods[int(name)]
        if count <= have[name]:
            have[name] -= count
            have['FUEL'] += cost
        else:
            send_message(f'You have not enough {name} to sell {count} {name} for {cost} FUEL')


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        obj.rect.x = obj.rect.x % (level_x * tile_width)
        obj.rect.y = obj.rect.y % (level_y * tile_height)

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


default_message = []

text_to_blit = []


def blit_text(screen):
    while len(text_to_blit) > 2:
        text_to_blit.pop(0)
    font = pygame.font.Font(None, 25)
    text_top = 0
    res = []
    for message_ind in range(len(text_to_blit)):
        res.append('')
        if message_ind == len(text_to_blit) - 1:
            res.append('    New message:')
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


def line_text(text):
    lines = ['']
    i = 0
    for word in text.split():
        if len(lines[i]) + len(word) + 1 < 20:
            lines[i] += ' ' + word
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


def show_action(player, num):
    tile = find_tile(player)
    if tile.type == 'l':
        send_message('If you want to exit the planet, press Enter')
        return None, None
    elif tile.type[0] == '<':
        cost, count = None, None
        if tile.type[:2] == '<;':
            send_message("There isn't anything to buy here.")
        else:
            count, cost = get_info_about_goods_to_buy(tile.type[1:], num)
            send_message(f'If you want to buy {count} {goods[int(tile.type[1:])]} for {cost} FUEL, press Enter')
        return cost, count
    elif tile.type[0] == '>':
        count, cost = None, None
        if tile.type[:2] == '>;':
            send_message("You can't sell anything here.")
        else:
            count, cost = get_info_about_goods_to_sell(tile.type[1:], num)
            send_message(f'If you want to sell {count} {goods[int(tile.type[1:])]} for {cost} FUEL, press Enter')

        return cost, count
    return None, None


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


def planet_game(num):
    # TODO change trade places randomly
    global default_message, text_to_blit
    planet = PLANETS[num]
    default_message = line_text(f'Now you are on the planet {PLANET_NAMES[num]}')
    text_to_blit = []
    particles = []
    global level_x, level_y
    player, level_x, level_y = generate_level(planet)
    camera = Camera()
    count, cost = None, None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for _tile in tiles_group:
                    _tile.save(num)
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    pass
                elif event.key == pygame.K_RIGHT:
                    player.move(tile_width, 0)
                    cost, count = show_action(player, num)
                elif event.key == pygame.K_LEFT:
                    player.move(-tile_width, 0)
                    cost, count = show_action(player, num)
                elif event.key == pygame.K_DOWN:
                    player.move(0, tile_height)
                    cost, count = show_action(player, num)
                elif event.key == pygame.K_UP:
                    player.move(0, -tile_height)
                    cost, count = show_action(player, num)
                elif event.key == pygame.K_RETURN:
                    # TODO smarter system of finding tile player on
                    tile = find_tile(player)
                    if tile.type == 'l':
                        for _tile in tiles_group:
                            _tile.save(num)
                        for sp in all_sprites:
                            sp.kill()
                        return
                    elif tile.type[0] == '<':
                        if cost is not None and count is not None:
                            player.buy(tile.type[1:], cost, count)
                        if randint(1, 10) == 1:
                            tile.type = '<;4'
                            tile.image = pygame.transform.scale(table, (tile_width, tile_height))
                            # PLANETS[num][player_x][player_y] = '<'
                        cost, count = show_action(player, num)
                    elif tile.type[0] == '>':
                        if cost is not None and count is not None:
                            player.sell(tile.type[1:], cost, count)
                        if randint(1, 10) == 1:
                            tile.type = '>;4'
                            tile.image = pygame.transform.scale(table, (tile_width, tile_height))
                            # PLANETS[num][player_x][player_y] = '>'
                        cost, count = show_action(player, num)
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


star_red_picture = load_image('star_red.png', [-1], size=(10, 10))
star_blue_picture = load_image('star_blue.png', [-1], size=(10, 10))


def flight_game(level_max):
    global player, iss
    player = FlyingPlayer(100, HEIGHT // 2)
    particles = []
    sec = 0
    coeff = 0.5
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
        if iss and coeff != -1:
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
        if len(garbage_group) == 0 and coeff == -1:
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


'''def end_screen(time):
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
        clock.tick(FPS)'''


# do not need this

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


class FlyingPlayer(AnimatedSprite):
    def __init__(self, pos_x, pos_y):
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
        # self.speedy -= self.acceleration
        if len(self.slow) == 0:
            self.speedy -= self.acceleration
        else:
            value = 0
            for _, v in self.slow:
                value += v
            self.speedy -= self.acceleration - value

    def update(self):
        global is_not_break
        if self.rect.top <= -20:
            self.speedy = 1
        self.time += 1
        if self.rect.bottom >= HEIGHT + 100:
            is_not_break = False
            return
        i = 0
        while i < len(self.slow):
            self.slow[i][0] -= 1
            if self.slow[i][0] == 0:
                self.slow.pop(i)
                i -= 1
            i += 1
        self.speedy += self.G
        self.rect.y += self.speedy
        other_image = self.other_image.copy()
        other_image.blit(super().update(), (160, 30))
        self.image = other_image
        self.mask = pygame.mask.from_surface(self.image)
        is_not_break = True

    def de_baf(self, time=10 ** 3, value=1):
        self.slow.append([time, value])


screen_rect = (-50, 0, WIDTH + 50, HEIGHT)
screen_rect_for_planets = (0, 0, WIDTH, HEIGHT)


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

        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[0] += self.gravity[0]
        self.velocity[1] += self.gravity[1]
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

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
                for _ in range(self.count):
                    Particle(self.pos, *self.speed, self.pictures, self.gravity, self.change)
            self.times -= 1
            self.time += 1
        else:
            self.alive = -1


start_screen()
