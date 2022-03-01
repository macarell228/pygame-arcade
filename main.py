import sys

import pygame

from classes import *


def terminate():
    pygame.quit()
    sys.exit()


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

    background = pygame.Surface(WINDOW_SIZE)
    for group in ALL_SPRITE_GROUPS:
        for item in group:
            item.kill()
            group.clear(screen, background)

    start_music(filename="background_main.mp3")

    gameover_window = GameoverWindow()
    restart_button = Button(
        pygame.transform.scale(load_image(f"{SOUNDS_BACKGROUNDS_DIR}/restart_button.png", color_key=-1), (50, 50)),
        pygame.rect.Rect(int(WIDTH * 0.5) - 25, int(HEIGHT * 0.6), 50, 50))

    level = Level(level_name)
    pygame.time.set_timer(ANIMATION_EVENTTYPE, 100)
    pygame.time.set_timer(FIRINGBULLET_EVENTTYPE, 1000)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise AssertionError('exit button was pressed :)')
            elif event.type == ANIMATION_EVENTTYPE:
                pass
            elif event.type == FIRINGBULLET_EVENTTYPE and level.state != 'done':
                mobs_group.update(level.player, shoot=True)
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
                    running = False

        move(level.player, level.player.directory)

        level.render(screen)
        somesprites_group.update(level.player)
        particle_group.update()
        gameover_group.update(level.state)
        all_sprites.draw(screen)
        gameover_group.draw(screen)
        restart_button.draw(screen, showing=bool(gameover_window.state == 'showing'))

        if pygame.mouse.get_focused():
            screen.blit(cursor_image, pygame.mouse.get_pos())

        clock.tick(FPS)
        pygame.display.flip()


def main():
    def upp(object, event_list):
        selected_option = object.update(event_list)
        if selected_option >= 0:
            object.main = object.options[selected_option]
            return object.main

    pygame.init()

    size = WINDOW_SIZE
    pygame.display.set_caption('dead inside')
    screen = pygame.display.set_mode(size)

    background = pygame.transform.scale(load_image(f"{SOUNDS_BACKGROUNDS_DIR}/background_menu.jpg"), WINDOW_SIZE)
    computer_images = {key: pygame.transform.scale(load_image(f"{SOUNDS_BACKGROUNDS_DIR}/lvl{i}.png"), (110, 90)) for
                       i, key in
                       zip(range(1, 4), LEVELS_NAMES)}
    level_name = 'UndergrounD'

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
        "Select Skin", list(map(str, range(1, 8 + 1))))

    play_btn = Button(
        pygame.transform.scale(load_image(f"{SOUNDS_BACKGROUNDS_DIR}/start_button.png", color_key=-1), (150, 70)),
        pygame.rect.Rect(int(WIDTH * 0.5) - 150 // 2, int(HEIGHT * 0.8), 150, 70))

    pygame.mouse.set_visible(False)
    cursor_image = load_image(f"{SOUNDS_BACKGROUNDS_DIR}/cursor.png", color_key=-1)

    start_music(filename="background_menu.mp3")

    try:
        running = True
        while running:
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_btn.check_pressed(event.pos):
                        playing_process(str(LEVELS_NAMES.index(level_name) + 1), screen, cursor_image)
                        start_music(filename="background_menu.mp3")

            a = upp(level_chooser, event_list)
            level_name = a if a is not None else level_name

            a = upp(skin_chooser, event_list)
            if a is not None:
                with open(f"{DATA_DIR}/{INFO_ABOUT_LEVELS_FILE_NAME}", 'r') as f:
                    data = json.load(f)
                data["currentPlayerSkin"] = int(a)
                with open(f"{DATA_DIR}/{INFO_ABOUT_LEVELS_FILE_NAME}", 'w') as f:
                    json.dump(data, f)

            screen.blit(background, (0, 0))
            screen.blit(computer_images[level_name], (128, 120))
            level_chooser.draw(screen)
            skin_chooser.draw(screen)
            play_btn.draw(screen)

            if pygame.mouse.get_focused():
                screen.blit(cursor_image, pygame.mouse.get_pos())

            pygame.display.flip()
    except Exception as error:
        print(error)
    finally:
        terminate()


if __name__ == '__main__':
    main()
