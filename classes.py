import pygame.transform
import pytmx
import json
import os
import random

from constants import *

pygame.mixer.init()


def start_music(filename):
    pygame.mixer.music.load(f"{DATA_DIR}/{SOUNDS_DIR}/{filename}")
    pygame.mixer.music.play(loops=-1)


def load_image(name=None, color_key=None, image=None):
    if name is not None:
        fullname = os.path.join('data', name)
        try:
            image = pygame.image.load(fullname).convert()
        except pygame.error as message:
            print('Cannot load image:', name)
            raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_sound(name, volume=1.0):
    sound = pygame.mixer.Sound(f"{DATA_DIR}/{SOUNDS_DIR}/{name}")
    sound.set_volume(volume)
    return sound


def res_decrease(in_extension):
    if in_extension:
        return TILE_SIZES["further"]
    return TILE_SIZES["close"]


def make_visible_range(tile_size, position):
    x, y = position

    step_to_deep = round(HEIGHT / tile_size)
    h_range = range(y - step_to_deep // 2 + 1, (y + 2) + step_to_deep // 2)

    step_to_breath = round(WIDTH / tile_size)
    w_range = range(x - step_to_breath // 2 + 1, (x + 2) + step_to_breath // 2)

    return h_range, w_range


def rotate_image(directory, image):
    if directory == 'up':
        angle = -90
    elif directory == 'down':
        angle = 90
    elif directory == 'right':
        angle = 180
    else:
        angle = 0
    return pygame.transform.rotate(image, angle)


def make_particles(filename, object, sizes):
    # сгенерируем частицы разного размера
    img = load_image(f"{SPRITES_SKIN_DIR}/{filename}", color_key=-1)
    fire = []
    for scale in sizes:
        fire.append(pygame.transform.scale(img, (scale, scale)))
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle((object.rect.centerx, object.rect.centery), random.choice(numbers), random.choice(numbers),
                 random.choice(fire))


player_group = pygame.sprite.Group()
jumper_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()
mobs_group = pygame.sprite.Group()
particle_group = pygame.sprite.Group()
fliers_group = pygame.sprite.Group()
somesprites_group = pygame.sprite.Group()
gameover_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
ALL_SPRITE_GROUPS = [player_group,
                     jumper_group,
                     bullets_group,
                     coins_group,
                     mobs_group,
                     particle_group,
                     fliers_group,
                     somesprites_group,
                     all_sprites]


class Level:
    def __init__(self, level_num):
        def make_jumpers_boards(jumpers_id, boards_ids):
            used = set()
            for x, i in enumerate(range(self.map.height)):
                for y, j in enumerate(range(self.map.width)):
                    tile_size = res_decrease((j, i) in self.extension)
                    if self.get_tile_id((j, i)) == jumpers_id:
                        Jumper(load_image(
                            image=pygame.transform.scale(self.map.get_tile_image(j, i, 0), (tile_size, tile_size)),
                            color_key=-1), (j, i), f_get_tile_id=self.get_tile_id, free_tiles_id=self.free_tile_id,
                            height=self.height, width=self.width)
                    if self.get_tile_id((j, i)) in boards_ids and (j, i) not in used:
                        def f_vertical(j, i):
                            return j < self.height and self.get_tile_id((j, i)) in boards_ids

                        def f_horizontal(j, i):
                            return i < self.width and self.get_tile_id((j, i)) in boards_ids

                        coordinates = set()
                        pos = (j, i)
                        if j + 1 < self.height and self.get_tile_id((j + 1, i)) in boards_ids:
                            function = f_vertical
                            dj, di = 1, 0
                        else:
                            function = f_horizontal
                            dj, di = 1, 0

                        while function(j, i):
                            coordinates.add((j, i))
                            i += di
                            j += dj

                        ElectricBoard(pos, pos in self.extension)
                        used = used.union(coordinates)

        def convert_extension_data(data):
            result = []
            for i in range(0, len(data), 4):
                left = data[i]
                top = data[i + 1]
                w = data[i + 2]
                h = data[i + 3]

                tmp = []
                for y in range(top, top + h):
                    for x in range(left, left + w):
                        tmp.append((x, y))

                result.extend(tmp)
            return result

        def make_mobs(directories):
            for key, value in directories.items():
                BulletMob(tuple(map(int, key.split())), *value)

        def make_fliers(dictionary):
            for key in dictionary:
                hor = dictionary[key]
                for i in range(0, len(hor), 2):
                    x, y = hor[i], hor[i + 1]
                    FlyingThing(position=(x, y), in_extension=(x, y) in self.extension, directory=key,
                                free_tiles_id=self.free_tile_id, get_f=self.get_tile_id)

        with open(f'{DATA_DIR}/{INFO_ABOUT_LEVELS_FILE_NAME}', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            skin_num = data["currentPlayerSkin"] - 1
            coins = data["coins"]
            data = data[level_num]

        self.extension = convert_extension_data(data["extension"])
        self.map = pytmx.load_pygame(f'{DATA_DIR}/{LEVELS_DIR}/{data["mapName"]}')
        self.state = 'working'
        self.height = self.map.height
        self.width = self.map.width
        self.picture_filename = None
        self.coins = coins
        self.free_tile_id = data["freeTilesId"]
        self.tile_sizes = TILE_SIZES
        self.player = Player(data["playerPosition"], data["playerPosition"] in self.extension, skin_num, parent=self)
        EndLists(tuple(data["endPlace"]), tuple(data["endPlace"]) in self.extension)
        make_jumpers_boards(data["jumperID"], data["boardID"])
        make_mobs(data["bulletMobs"])
        make_fliers(data["fliers"])

    def render(self, screen):
        """ Чтобы работало быстрее, прорисовываю только ту часть карты, что умещается в размеры окна """

        x, y = self.player.pos

        tile_size = res_decrease((x, y) in self.extension)

        h_range, w_range = make_visible_range(tile_size, (x, y))

        for x, i in enumerate(h_range):
            for y, j in enumerate(w_range):
                image = self.map.get_tile_image(j, i, 1)
                if not image:
                    image = self.map.get_tile_image(j, i, 0)
                image = pygame.transform.scale(image, (tile_size, tile_size))
                screen.blit(image, (y * tile_size, x * tile_size))

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)] - 1


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, skin_number, columns, rows, x, y, columns2, rows2):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows, columns2, rows2)
        self.cur_frame = 0
        self.rect = self.rect.move(x, y)
        self.skin_number = skin_number
        self.window_now = 0  # depend on directory of player's move
        self.orig_image = self.frames[self.skin_number][self.window_now][self.cur_frame]

    def cut_sheet(self, sheet, columns, rows, x, y):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for m in range(rows):
            for k in range(columns):
                self.frames.append([])
                the_screen = sheet.subsurface(pygame.Rect((self.rect.w * k, self.rect.h * m), self.rect.size))
                rect = pygame.Rect(0, 0, the_screen.get_width() // x, the_screen.get_height() // y)
                for j in range(y):
                    self.frames[-1].append([])
                    for i in range(x):
                        frame_location = (rect.w * i, rect.h * j)
                        self.frames[-1][-1].append(the_screen.subsurface(pygame.Rect(
                            frame_location, rect.size)))

    def update(self, directory=None):
        if directory is not None:
            if directory == 'up':
                self.window_now = 3
            elif directory == 'down':
                self.window_now = 0
            elif directory == 'right':
                self.window_now = 1
            else:
                self.window_now = 2
        self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.skin_number][self.window_now])
        self.orig_image = self.frames[self.skin_number][self.window_now][self.cur_frame]


class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, dx, dy, image):
        super().__init__(particle_group, all_sprites)
        self.image = image
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        self.gravity = GRAVITY

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(SCREEN_RECT):
            self.kill()


class Player(AnimatedSprite):
    def __init__(self, pos, in_extension, skin_num, parent):
        super(Player, self).__init__(sheet=load_image(f"{SPRITES_SKIN_DIR}/player.png", color_key=-1),
                                     skin_number=skin_num, columns=4, rows=2, x=50, y=50,
                                     columns2=3, rows2=4)
        tile_size = res_decrease(in_extension)
        self.pos = pos
        self.image = pygame.transform.scale(self.orig_image,
                                            (tile_size * SPRITES_INCREASE, tile_size * SPRITES_INCREASE))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(WIDTH // 2 - tile_size, HEIGHT // 2 - tile_size,
                                tile_size * SPRITES_INCREASE, tile_size * SPRITES_INCREASE)
        self.parent = parent
        self.directory = None
        self.last_direction = None

    def move(self, x, y, in_extension):
        self.pos = (x, y)
        self.update()
        tile_size = res_decrease(in_extension)
        self.image = pygame.transform.scale(self.orig_image,
                                            (tile_size * SPRITES_INCREASE, tile_size * SPRITES_INCREASE))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(WIDTH // 2 - tile_size, HEIGHT // 2 - tile_size,
                                tile_size * SPRITES_INCREASE, tile_size * SPRITES_INCREASE)

    def start_killing_process(self, filename, picture_filename, sound=load_sound("silent.wav")):
        self.directory = self.last_direction = 'killed :)'
        make_particles(filename=filename, object=self, sizes=(20, 40, 60))
        sound.play()
        pygame.mixer.music.stop()
        self.parent.state = 'done'
        self.parent.picture_filename = picture_filename
        self.kill()


class FlyingThing(pygame.sprite.Sprite):
    def __init__(self, position, in_extension, directory, get_f, free_tiles_id):
        super(FlyingThing, self).__init__(fliers_group, somesprites_group, all_sprites)

        self.tile_size = res_decrease(in_extension)
        self.rect = pygame.rect.Rect(WIDTH + 1, HEIGHT + 1, self.tile_size * SPRITES_INCREASE, self.tile_size)
        self.images = [
            pygame.transform.scale(load_image(f"{SPRITES_SKIN_DIR}/mouse1.png", color_key=-1), self.rect.size),
            pygame.transform.scale(load_image(f"{SPRITES_SKIN_DIR}/mouse2.png", color_key=-1), self.rect.size)]
        self.index = 0
        self.image = self.images[self.index]
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = position
        self.directory = directory
        self.direction = 1
        self.get_id_f = get_f
        self.free_tiles_id = free_tiles_id

    def update(self, player, animation=False):
        h_range, w_range = make_visible_range(self.rect.width // 2, player.pos)
        i, j = self.pos
        if i in w_range and j in h_range:
            self.rect.top = (j - next(iter(h_range))) * self.rect.height
            self.rect.left = (i - next(iter(w_range))) * (self.rect.width // 2)
            if animation:
                self.index = (self.index + 1) % len(self.images)
                self.image = pygame.transform.scale(self.images[self.index],
                                                    (self.tile_size * SPRITES_INCREASE, self.tile_size))
                self.mask = pygame.mask.from_surface(self.image)
                if self.directory == "horizontal":
                    if self.direction:
                        if self.get_id_f((i + 2, j)) in self.free_tiles_id:
                            self.pos = (i + 1, j)
                        else:
                            self.pos = (i - 1, j)
                            self.direction = 0
                    else:
                        if self.get_id_f((i - 1, j)) in self.free_tiles_id:
                            self.pos = (i - 1, j)
                        else:
                            self.pos = (i + 1, j)
                            self.direction = 1
                else:
                    if self.direction:
                        if self.get_id_f((i, j + 1)) in self.free_tiles_id:
                            self.pos = (i, j + 1)
                        else:
                            self.pos = (i, j - 1)
                            self.direction = 0
                    else:
                        if self.get_id_f((i, j - 1)) in self.free_tiles_id:
                            self.pos = (i, j - 1)
                        else:
                            self.pos = (i, j + 1)
                            self.direction = 1
        else:
            self.rect.top = HEIGHT + 1
            self.rect.left = WIDTH + 1

        if pygame.sprite.collide_mask(self, player) and player.directory != 'killed :)':
            self.kill()
            player.start_killing_process(filename="death.png", sound=load_sound("failed.mp3", 0.7),
                                         picture_filename=GAMEOVER_FILENAME)


class BulletMob(pygame.sprite.Sprite):
    def __init__(self, position, directory, bullet_distance):
        super(BulletMob, self).__init__(mobs_group, somesprites_group, all_sprites)
        self.images = [rotate_image(directory, pygame.transform.scale(load_image(f"{SPRITES_SKIN_DIR}/mob1.png"), (
            TILE_SIZES['further'] * SPRITES_INCREASE, TILE_SIZES['further'] * SPRITES_INCREASE))),
                       rotate_image(directory, pygame.transform.scale(load_image(f"{SPRITES_SKIN_DIR}/mob2.png"), (
                           TILE_SIZES['further'] * SPRITES_INCREASE, TILE_SIZES['further'] * SPRITES_INCREASE)))]
        self.image = self.images[0]
        self.rect = pygame.rect.Rect(WIDTH + 1, HEIGHT + 1, self.image.get_width(), self.image.get_height())
        self.pos = position
        self.bullet_directory = directory
        self.bullet_distance = (bullet_distance - 1) * (self.rect.w // 2)
        self.timer_for_animation = 0
        self.sound = load_sound("bullet_sound.mp3", 0.5)

    def update(self, player, shoot=False):
        # меняется анимация моба и смотрим, стоит ли его прорисовывать
        h_range, w_range = make_visible_range(self.rect.width // 2, player.pos)
        i, j = self.pos
        if i in w_range and j in h_range:
            self.rect.top = (j - next(iter(h_range))) * (self.rect.height // 2)
            self.rect.left = (i - next(iter(w_range))) * (self.rect.width // 2)
            if shoot:
                self.shoot()
                self.image = self.images[1]
                self.timer_for_animation = 0
            else:
                if self.timer_for_animation < 20:
                    self.timer_for_animation += 1
                else:
                    self.image = self.images[0]
        else:
            self.rect.top = HEIGHT + 1
            self.rect.left = WIDTH + 1

    def shoot(self):
        if self.bullet_directory == "up":
            x, y = self.rect.centerx - SMALL_SIZE // 2, self.rect.top - SMALL_SIZE
        elif self.bullet_directory == "down":
            x, y = self.rect.centerx - SMALL_SIZE // 2, self.rect.bottom
        elif self.bullet_directory == "right":
            x, y = self.rect.right, self.rect.centery - SMALL_SIZE // 2
        else:
            x, y = self.rect.left - SMALL_SIZE, self.rect.centery - SMALL_SIZE // 2
        Bullet(x, y, self.bullet_directory, self.bullet_distance)
        self.sound.play()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, left, top, directory, distance):
        pygame.sprite.Sprite.__init__(self, bullets_group, somesprites_group, all_sprites)

        def set_speed(directory):
            speed = 10
            if directory in "up left":
                return -speed
            return speed

        self.image = pygame.transform.scale(load_image(f"{SPRITES_SKIN_DIR}/bullet.png", color_key=-1),
                                            (SMALL_SIZE, SMALL_SIZE))
        self.rect = pygame.rect.Rect(left, top, SMALL_SIZE, SMALL_SIZE)
        self.mask = pygame.mask.from_surface(self.image)
        self.directory = directory
        self.distance = distance
        self.counter = 0
        self.speedy = set_speed(self.directory)

    def update(self, player, dist=0, directory=None):
        if directory:
            if directory in "up down":
                self.rect.y += dist
            else:
                self.rect.x += dist
        else:
            if self.directory in "up down":
                self.rect.y += self.speedy
            else:
                self.rect.x += self.speedy
            self.counter += abs(self.speedy)
        if self.rect.bottom < 0 or self.rect.top < 0 or self.rect.w > WIDTH or self.rect.height > HEIGHT or self.counter >= self.distance:
            self.kill()
        if pygame.sprite.collide_mask(self, player) and player.directory != 'killed :)':
            self.kill()
            player.start_killing_process(filename="death.png", sound=load_sound("failed.mp3", 0.7),
                                         picture_filename=GAMEOVER_FILENAME)


class Coin(pygame.sprite.Sprite):
    def __init__(self, left, top):
        pygame.sprite.Sprite.__init__(self, coins_group, bullets_group, somesprites_group, all_sprites)

        self.image = pygame.transform.scale(load_image(f"{SPRITES_SKIN_DIR}/coin_10.png", color_key=-1),
                                            (SMALL_SIZE, SMALL_SIZE))
        self.rect = pygame.rect.Rect(left, top, SMALL_SIZE, SMALL_SIZE)
        self.mask = pygame.mask.from_surface(self.image)
        self.sound = load_sound("money_sound.mp3", 0.1)

    def update(self, player, dist=0, directory=None):
        if directory:
            if directory in "up down":
                self.rect.y += dist
            else:
                self.rect.x += dist

        if self.rect.bottom < 0 or self.rect.top < 0 or self.rect.w > WIDTH or self.rect.height > HEIGHT:
            self.kill()
        elif pygame.sprite.collide_mask(self, player) and player.directory != 'killed :)':
            self.kill()
            self.sound.play()
            player.parent.coins += 1


class InvisibleSprite(pygame.sprite.Sprite):
    def __init__(self, sprites_group, pos, tile_size, image, particle_image_name):
        super(InvisibleSprite, self).__init__(*sprites_group, all_sprites)
        self.pos = pos
        self.tile_size = tile_size
        self.image = image
        self.particle_image_name = particle_image_name
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.rect.Rect(WIDTH + 1, HEIGHT + 1, *self.image.get_size())
        self.sound_here = load_sound("silent.wav")
        self.sound = load_sound("silent.wav")

    def update(self, player):
        h_range, w_range = make_visible_range(self.rect.width // 2, player.pos)
        i, j = self.pos
        if i in w_range and j in h_range:
            self.rect.top = (j - next(iter(h_range))) * self.tile_size
            self.rect.left = (i - next(iter(w_range))) * self.tile_size
        else:
            self.rect.top = HEIGHT + 1
            self.rect.left = WIDTH + 1

        self.optional_update(player)

    def optional_update(self, player):
        pass


class Jumper(InvisibleSprite):
    def __init__(self, image, pos, f_get_tile_id, free_tiles_id, height, width):
        super(Jumper, self).__init__(sprites_group=(jumper_group, somesprites_group), image=image, pos=pos,
                                     particle_image_name="jumpers_kids.png", tile_size=image.get_width())
        self.sound = load_sound("jumper_sound.mp3", 0.7)
        self.directions = [{"up": lambda x, y: y - 1 >= 0 and f_get_tile_id((x, y - 1)) in free_tiles_id,
                            "down": lambda x, y: y + 2 < height and f_get_tile_id((x, y + 2)) in free_tiles_id},
                           {"right": lambda x, y: x + 2 < width and f_get_tile_id((x + 2, y)) in free_tiles_id,
                            "left": lambda x, y: x - 1 >= 0 and f_get_tile_id((x - 1, y)) in free_tiles_id}]

    def optional_update(self, player):
        x, y = player.pos
        i, j = self.pos
        if (x + 1 == i and y + 1 == j) or (x + 1 == i and y == j) or (x == i and y == j) or (x == i and y + 1 == j):
            make_particles(filename=self.particle_image_name, object=self, sizes=(10, 20, 30))
            for key, function in (
                    self.directions[1] if player.last_direction in "up down" else self.directions[0]).items():
                if function(x, y):
                    player.directory = key
                    player.last_direction = key
                    break
            self.sound.play(maxtime=500)


class EndLists(InvisibleSprite):
    def __init__(self, pos, in_extension):
        tile_size = res_decrease(in_extension)
        super(EndLists, self).__init__(sprites_group=(somesprites_group,), particle_image_name="star.png", pos=pos,
                                       image=pygame.transform.scale(
                                           load_image(f"{SPRITES_SKIN_DIR}/end.jpg", color_key=-1),
                                           (tile_size * SPRITES_INCREASE, tile_size * SPRITES_INCREASE)),
                                       tile_size=tile_size)
        self.sound = load_sound("win.mp3")

    def optional_update(self, player):
        if pygame.sprite.collide_mask(self, player):
            player.start_killing_process(filename=self.particle_image_name, sound=self.sound,
                                         picture_filename=WIN_FILENAME)
            self.kill()


class ElectricBoard(InvisibleSprite):
    def __init__(self, pos, in_extension):
        super(ElectricBoard, self).__init__(sprites_group=(somesprites_group,), particle_image_name="death.png",
                                            pos=pos,
                                            image=pygame.Surface((10, 10)), tile_size=res_decrease(in_extension))
        self.sound_here = load_sound("sheep.mp3", 0.5)

    def optional_update(self, player):
        x, y = player.pos
        i, j = self.pos
        if (x + 1 == i and y + 1 == j) or (x + 1 == i and y == j) or (x == i and y == j) or (x == i and y + 1 == j):
            player.start_killing_process(filename=self.particle_image_name, sound=load_sound("failed.mp3", 0.7),
                                         picture_filename=GAMEOVER_FILENAME)
            self.kill()


class GameoverWindow(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, gameover_group)

        def make_image(size, board):
            image = pygame.Surface(size.size)
            image.fill((255, 60, 0))
            image2 = pygame.Surface((size.w - 2 * board, size.h - 2 * board))
            image2.fill((255, 200, 0))
            image.blit(image2, (board, board))
            return image

        self.size = pygame.rect.Rect(int(WIDTH * 0.25), int(HEIGHT * 0.25), int(WIDTH * 0.5), int(HEIGHT * 0.5))
        self.board = int(self.size.h * 0.05)
        self.image = make_image(self.size, self.board)
        self.image2 = self.image.copy()
        self.rect = pygame.rect.Rect(WIDTH + 1, HEIGHT + 1, 0, 0)
        self.timer = None
        self.state = 'not showing'

    def update(self, state, filename):
        if state == 'done':
            if self.timer is None:
                self.timer = 1
            elif self.timer == 100:
                self.image.blit(pygame.transform.scale(load_image(filename, color_key=-1),
                                                       (self.size.width - 2 * self.board,
                                                        int((self.size.h - self.board) * 0.75))),
                                (self.board, self.board))
                self.rect = self.size
                self.state = 'showing'
            elif self.timer < 100:
                self.timer += 1
        else:
            self.rect = pygame.rect.Rect(WIDTH + 1, HEIGHT + 1, 0, 0)
            self.image = self.image2.copy()


class Button:
    def __init__(self, rect, image, image2=None, size=pygame.rect.Rect(-WIDTH, -HEIGHT, 10, 10)):
        self.image = image
        self.image2 = image2
        self.rect = rect
        self.size = size
        self.timer = None
        self.size_using = False

    def check_pressed(self, pos):
        if (not self.size_using and self.rect.collidepoint(pos)) or (self.size_using and self.size.collidepoint(pos)):
            if self.image2 is not None:
                self.image, self.image2 = self.image2, self.image
            self.timer = 1 if self.image2 is not None else 100
            return True
        return False

    def draw(self, screen, showing=True):
        if showing:
            screen.blit(self.image, (self.rect.x, self.rect.y))
            self.size_using = False
        else:
            screen.blit(self.image, (self.size.x, self.size.y))
            self.size_using = True

    def update(self):
        if self.timer is not None:
            if self.timer < 50:
                self.timer += 1
                return False
            self.timer = None
            return True


class DropDown:
    def __init__(self, color_menu, color_option, x, y, w, h, font, main, options):
        self.color_menu = color_menu
        self.color_option = color_option
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.main = main
        self.options = options
        self.draw_menu = False
        self.menu_active = False
        self.active_option = 0

    def draw(self, surf):
        pygame.draw.rect(surf, self.color_menu[self.menu_active], self.rect, 0)
        msg = self.font.render(self.main, 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.options):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.color_option[1 if i == self.active_option else 0], rect, 0)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        for i in range(len(self.options)):
            rect = self.rect.copy()
            rect.y += (i + 1) * self.rect.height
            if rect.collidepoint(mpos):
                self.active_option = i
                break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.draw_menu = False
                    return self.active_option
        return -1
