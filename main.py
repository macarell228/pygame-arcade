import sys

import pygame.mixer

from classes import *


def terminate():
    pygame.quit()
    sys.exit()


def market(screen, cursor_image):
    with open(f"{DATA_DIR}/{INFO_ABOUT_LEVELS_FILE_NAME}", 'r') as f:
        data = json.load(f)
        q_coins = data["coins"]
        bought_skins = data["boughtPlayerSkins"]
        current_ind = data["currentPlayerSkin"] - 1

    background = pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/background_mini_3.png"), WINDOW_SIZE)
    hero = AnimatedSprite(sheet=load_image(f"{SPRITES_SKIN_DIR}/player.png", color_key=-1),
                          skin_number=current_ind, columns=4, rows=2, x=50, y=50,
                          columns2=3, rows2=4)
    home_button = Button(
        image=pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/home.png", color_key=-1), (50, 50)),
        rect=pygame.rect.Rect(int(WIDTH * 0.05) - 25,
                              int(HEIGHT * 0.02), 50, 50))
    buttons = []
    font = pygame.font.Font(None, 45)
    text = font.render(str(PRICE_SKINS), True, pygame.color.Color("black"))

    dx = int(WIDTH * 0.05)
    dy = int(WIDTH * 0.1)
    skin_width = int(WIDTH * ((1 - 0.05 * (ROW_QUANTITY_SKINS + 1)) / ROW_QUANTITY_SKINS))
    skin_height = int(HEIGHT * 0.35)
    tmp = pygame.Surface((int(skin_width * 0.4), int(dy * 0.5)))
    tmp.fill(COLOR_MAIN)
    new_tmp = pygame.Surface((int(tmp.get_width() * 0.8), int(tmp.get_height() * 0.8)))
    new_tmp.fill(COLOR_OPTIONAL)
    tmp.blit(new_tmp, (int(tmp.get_width() * 0.1), int(tmp.get_height() * 0.1)))
    tmp.blit(text, (int(tmp.get_width() * 0.1), int(tmp.get_height() * 0.07)))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise AssertionError(EXIT_MESSAGE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, button in enumerate(buttons):
                    if button.check_pressed(event.pos) and i + 1 not in bought_skins and q_coins >= PRICE_SKINS:
                        q_coins -= PRICE_SKINS
                        bought_skins.append(i + 1)
                if home_button.check_pressed(event.pos):
                    running = False

        screen.blit(background, (0, 0))

        x, y = dx, dy
        for i, skin in enumerate(hero.frames):
            skin = skin[INDEX_MAIN_LOOK[0]][INDEX_MAIN_LOOK[1]]
            screen.blit(pygame.transform.scale(skin, (skin_width, int(skin_height * 0.8))), (x, y))

            if len(buttons) < ROW_QUANTITY_SKINS * COLUMN_QUANTITY_SKINS:
                buttons.append(Button(image=tmp,
                                      rect=pygame.rect.Rect(x + int(skin_width * 0.3), y + int(skin_height * 0.85),
                                                            *tmp.get_size())))
            x += skin_width + dx
            if i == ROW_QUANTITY_SKINS - 1:
                x = dx
                y += skin_height + dy

        for button in buttons:
            button.draw(screen)

        text1 = font.render(str(q_coins), True, (100, 255, 100))
        screen.blit(text1, (int(WIDTH * 0.8), int(HEIGHT * 0.05)))

        home_button.draw(screen)

        if pygame.mouse.get_focused():
            screen.blit(cursor_image, pygame.mouse.get_pos())

        pygame.display.flip()

    with open(f"{DATA_DIR}/{INFO_ABOUT_LEVELS_FILE_NAME}", 'w') as f:
        data["coins"] = q_coins
        data["boughtPlayerSkins"] = bought_skins
        json.dump(data, f)


def playing_process(level_name: str, screen, cursor_image):
    def move(hero, movement):
        x, y = hero.pos

        if movement and movement == 'up':
            if y - 1 >= 0 and level.get_tile_id((x, y - 1)) in level.free_tile_id:
                y -= 1
                hero.move(x, y, (x, y) in level.extension)
                bullets_group.update(hero, directory="up", dist=hero.rect.h // 2)
                player_group.update(directory="up")
            else:
                hero.directory = None
        elif movement and movement == 'down':
            m = y + 1
            if m + 1 < level.height and level.get_tile_id((x, m + 1)) in level.free_tile_id:
                m += 1
                y += 1
                hero.move(x, y, (x, y) in level.extension)
                bullets_group.update(hero, directory="down", dist=-(hero.rect.h // 2))
                player_group.update(directory="down")
            else:
                hero.directory = None
        elif movement and movement == 'left':
            if x - 1 >= 0 and level.get_tile_id((x - 1, y)) in level.free_tile_id:
                x -= 1
                hero.move(x, y, (x, y) in level.extension)
                bullets_group.update(hero, directory="right", dist=hero.rect.h // 2)
                player_group.update(directory="right")
            else:
                hero.directory = None
        elif movement and movement == 'right':
            m = x + 1
            if m + 1 < level.width and level.get_tile_id((m + 1, y)) in level.free_tile_id:
                m += 1
                x += 1
                hero.move(x, y, (x, y) in level.extension)
                bullets_group.update(hero, directory="left", dist=-(hero.rect.h // 2))
                player_group.update(directory="left")
            else:
                hero.directory = None

    def make_coins():
        x, y = level.player.pos
        tile_size = level.player.rect.w // 2
        w = (WIDTH // tile_size // 2)
        h = (HEIGHT // tile_size // 2)
        if level.get_tile_id((x - w, y)) in level.free_tile_id and random.randrange(0, 2) == 1:
            Coin(level.player.rect.x - w * tile_size, level.player.rect.y)
        if level.get_tile_id((x + w, y)) in level.free_tile_id and random.randrange(0, 2) == 1:
            Coin(level.player.rect.x + w * tile_size, level.player.rect.y)
        if level.get_tile_id((x, y - h)) in level.free_tile_id and random.randrange(0, 2) == 1:
            Coin(level.player.rect.x, level.player.rect.y - h * tile_size)
        if level.get_tile_id((x, y + h)) in level.free_tile_id and random.randrange(0, 2) == 1:
            Coin(level.player.rect.x, level.player.rect.y + h * tile_size)

    background = pygame.Surface(WINDOW_SIZE)
    for group in ALL_SPRITE_GROUPS:
        for item in group:
            item.kill()
            group.clear(screen, background)

    if sound_play:
        start_music(filename="background_main.mp3")

    gameover_window = GameoverWindow()
    restart_button = Button(
        image=pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/restart_button.png", color_key=-1), (50, 50)),
        rect=pygame.rect.Rect(int(gameover_window.size.w * 0.5) - 25 + gameover_window.size.x,
                              int(gameover_window.size.h * 0.7) + gameover_window.size.y, 50, 50))
    pause_button = Button(
        image=pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/pause_button.png", color_key=-1), (50, 50)),
        rect=pygame.rect.Rect(-WIDTH, -HEIGHT, 50, 50),
        size=pygame.rect.Rect(int(WIDTH * 0.1), int(HEIGHT * 0.1), 50, 50))
    home_button = Button(
        image=pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/home.png"), (50, 50)),
        rect=pygame.rect.Rect(int(gameover_window.size.w * 0.3) - 25 + gameover_window.size.x,
                              int(gameover_window.size.h * 0.7) + gameover_window.size.y, 50, 50))
    play_button = Button(
        image=pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/play.png", color_key=-1), (50, 50)),
        rect=pygame.rect.Rect(int(gameover_window.size.w * 0.7) - 25 + gameover_window.size.x,
                              int(gameover_window.size.h * 0.7) + gameover_window.size.y, 50, 50))
    buttons = [restart_button, pause_button, home_button, play_button]

    level = Level(level_name)
    pygame.time.set_timer(ANIMATION_EVENTTYPE, 500)
    pygame.time.set_timer(FIRINGBULLET_EVENTTYPE, 1000)
    pygame.time.set_timer(COIN_EVENTTYPE, 1200)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise AssertionError(EXIT_MESSAGE)
            elif event.type == ANIMATION_EVENTTYPE:
                fliers_group.update(level.player, animation=True)
            elif event.type == FIRINGBULLET_EVENTTYPE and level.state != 'done':
                mobs_group.update(level.player, shoot=True)
            elif event.type == COIN_EVENTTYPE and level.state != 'done':
                if random.randrange(0, 2) == 1 and coins_group.__len__() < 5:
                    make_coins()
            elif event.type == pygame.KEYDOWN and not level.player.directory:
                if event.key == pygame.K_DOWN:
                    level.player.directory = "down"
                    level.player.last_direction = level.player.directory
                elif event.key == pygame.K_UP:
                    level.player.directory = "up"
                    level.player.last_direction = level.player.directory
                elif event.key == pygame.K_LEFT:
                    level.player.directory = "left"
                    level.player.last_direction = level.player.directory
                elif event.key == pygame.K_RIGHT:
                    level.player.directory = "right"
                    level.player.last_direction = level.player.directory
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.check_pressed(event.pos):
                    return True
                if pause_button.check_pressed(event.pos):
                    level.state = 'done'
                    gameover_window.timer = 100
                    gameover_window.state = 'showing'
                    level.picture_filename = PAUSE_FILENAME
                if home_button.check_pressed(event.pos):
                    running = False
                if play_button.check_pressed(event.pos) and level.player.last_direction != "killed :)":
                    level.state = 'working'
                    gameover_window.timer = None
                    gameover_window.state = 'not showing'

        move(level.player, level.player.directory)

        level.render(screen)
        somesprites_group.update(level.player)
        particle_group.update()
        gameover_group.update(level.state, level.picture_filename)
        all_sprites.draw(screen)
        gameover_group.draw(screen)
        [button.draw(screen, showing=bool(gameover_window.state == 'showing')) for button in buttons]

        if pygame.mouse.get_focused():
            screen.blit(cursor_image, pygame.mouse.get_pos())

        clock.tick(FPS)
        pygame.display.flip()

    with open(f"{DATA_DIR}/{INFO_ABOUT_LEVELS_FILE_NAME}", 'r') as f:
        data = json.load(f)
    data["coins"] = level.coins
    with open(f"{DATA_DIR}/{INFO_ABOUT_LEVELS_FILE_NAME}", 'w') as f:
        json.dump(data, f)

    return False


def main():
    def upp(object, event_list):
        selected_option = object.update(event_list)
        if selected_option >= 0:
            object.main = object.options[selected_option]
            return object.main

    pygame.init()

    size = WINDOW_SIZE
    screen = pygame.display.set_mode(size)

    background = pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/background_menu.jpg"), WINDOW_SIZE)
    computer_images = {key: pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/lvl{i}.png"), (110, 90)) for
                       i, key in
                       zip(range(1, 4), LEVELS_NAMES)}
    level_name = 'UndergrounD'

    with open(f"{DATA_DIR}/{INFO_ABOUT_LEVELS_FILE_NAME}", 'r') as f:
        skins = json.load(f)["boughtPlayerSkins"]

    level_chooser = DropDown(
        [COLOR_INACTIVE, COLOR_ACTIVE],
        [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
        int(WIDTH * 0.75) - 25, HEIGHT // 2 - 50, 150, 25 * 2,
        pygame.font.SysFont(name='arialblack', size=20),
        "Select Level", LEVELS_NAMES)

    skin_chooser = DropDown(
        [COLOR_INACTIVE, COLOR_ACTIVE],
        [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
        int(WIDTH * 0.5) - 10, HEIGHT * 0.1, 80, 20,
        pygame.font.SysFont(name='arialblack', size=10),
        "Select Skin", list(map(str, skins)))

    play_btn = Button(
        image=pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/start_button.png", color_key=-1), (150, 70)),
        rect=pygame.rect.Rect(int(WIDTH * 0.5) - 150 // 2, int(HEIGHT * 0.8), 150, 70),
        image2=pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/start_button2.png", color_key=-1), (150, 70)))
    sound_btn = Button(
        image=pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/sound_off_button.png", color_key=-1), (70, 70)),
        rect=pygame.rect.Rect(int(WIDTH * 0.1) - 70 // 2, int(HEIGHT * 0.8), 70, 70),
        image2=pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/sound_off_button2.png", color_key=-1), (70, 70)))
    market_btn = Button(
        image=pygame.transform.scale(load_image(f"{BACKGROUNDS_DIR}/dollar.png", color_key=-1), (70, 70)),
        rect=pygame.rect.Rect(int(WIDTH * 0.3) - 70 // 2, int(HEIGHT * 0.8), 70, 70))

    pygame.mouse.set_visible(False)
    cursor_image = load_image(f"{BACKGROUNDS_DIR}/cursor.png", color_key=-1)

    global sound_play

    start_music(filename="background_menu.mp3")

    try:

        running = True
        while running:
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    play_btn.check_pressed(event.pos)
                    if sound_btn.check_pressed(event.pos):
                        if sound_play:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
                        sound_play = not sound_play
                    if market_btn.check_pressed(event.pos):
                        market(screen, cursor_image)

                        with open(f"{DATA_DIR}/{INFO_ABOUT_LEVELS_FILE_NAME}", 'r') as f:
                            skins = json.load(f)["boughtPlayerSkins"]
                        skin_chooser = DropDown(skin_chooser.color_menu,
                                                skin_chooser.color_option,
                                                skin_chooser.rect.x, skin_chooser.rect.y, skin_chooser.rect.w,
                                                skin_chooser.rect.h,
                                                skin_chooser.font,
                                                "Select Skin", list(map(str, skins)))

            a = upp(level_chooser, event_list)
            level_name = a if a is not None else level_name

            a = upp(skin_chooser, event_list)
            if a is not None:
                with open(f"{DATA_DIR}/{INFO_ABOUT_LEVELS_FILE_NAME}", 'r') as f:
                    data = json.load(f)
                data["currentPlayerSkin"] = int(a)
                with open(f"{DATA_DIR}/{INFO_ABOUT_LEVELS_FILE_NAME}", 'w') as f:
                    json.dump(data, f)

            if play_btn.update():
                result = True
                while result:
                    result = playing_process(str(LEVELS_NAMES.index(level_name) + 1), screen, cursor_image)
                start_music(filename="background_menu.mp3")
                if not sound_play:
                    pygame.mixer.music.pause()

            screen.blit(background, (0, 0))
            screen.blit(computer_images[level_name], (128, 120))
            level_chooser.draw(screen)
            skin_chooser.draw(screen)
            play_btn.draw(screen)
            sound_btn.draw(screen)
            market_btn.draw(screen)

            if pygame.mouse.get_focused():
                screen.blit(cursor_image, pygame.mouse.get_pos())

            pygame.display.flip()
    except Exception as error:
        print(error)
    finally:
        terminate()


if __name__ == '__main__':
    main()
