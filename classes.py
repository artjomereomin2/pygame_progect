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
        self.rect.y += round(self.speedy)
        other_image = self.other_image.copy()
        other_image.blit(super().update(), (160, 30))
        self.image = other_image
        self.mask = pygame.mask.from_surface(self.image)
        is_not_break = True

    def de_baf(self, time=10 ** 3, value=1):
        self.slow.append([time, value])


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    '''fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))'''

    def __init__(self, pos, dx, dy, pictures, gravity=(0, 1), change=lambda x: x % 20 == 0, do_kill=True,
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

        self.do_kill = do_kill

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
            if self.image_ind == len(self.pictures) and self.do_kill:
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

    def change(self, offer):
        global ship_level
        print(offer)
        if type(offer) == tuple:
            if have[offer[1]] >= offer[3] and calc_weight() + offer[2] * weight[offer[0]] - offer[3] - weight[offer[1]] \
                    <= upgrades[ship_level]['грузоподъёмность']:
                have[offer[1]] -= offer[3]
                have[offer[0]] += offer[2]
            else:
                if not have[offer[1]] >= offer[3]:
                    send_message("В долг не даю.")
                else:
                    send_message('А как ты это понесёшь?')
        else:
            if have[offer] >= ship_level + 1:
                have[offer] -= ship_level + 1
                ship_level += 1
            else:
                send_message('В долг не даю.')
        ship_level = min(ship_level, 9)


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
        elif tile_type[0] == '$':
            self.image = pygame.transform.scale(merchants_images[MERCHANTS[int(tile_type[1:])]['image_num']],
                                                (tile_width * 2, tile_height * 2))
            self.rect = self.image.get_rect()
            self.rect.center = (round(tile_width * (pos_x + 0.5)), round(tile_height * (pos_y + 0.5)))
        elif tile_type[0] == '?':
            self.image = pygame.transform.scale(mystery_merchants_images[MERCHANTS[int(tile_type[1:])]['image_num']],
                                                (tile_width * 2, tile_height * 2))
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)
        elif tile_type[0] == 'u':
            self.image = pygame.transform.scale(tile_images['.'], (tile_width, tile_height))
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)
        elif tile_type[0] == '=':
            self.image = pygame.transform.scale(tile_images['.'], (tile_width, tile_height))
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)
        elif tile_type[0] in tile_images.keys():
            self.image = pygame.transform.scale(tile_images[tile_type], (tile_width, tile_height))
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)


class PlanetView(pygame.sprite.Sprite):
    def __init__(self, pos, num, player_here=False, **other):
        super().__init__(planets)
        self.image = pygame.transform.scale(planet_images[0], (100, 100))
        self.rect = self.image.get_rect()
        self.num = num
        self.rect.x, self.rect.y = pos[0], pos[1]
        self.player_here = player_here
