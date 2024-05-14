import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("Platformer")               # Заголовок окна

WIDTH, HEIGHT = 1000, 800                              # Ширина и высота окна
FPS = 60                                               # Фэпусы
PLAYER_VEL = 5                                         # Скорость игрока

window = pygame.display.set_mode((WIDTH, HEIGHT))      #Создать окно с указанными размерами 


def flip(sprites):                                                                          # Отражение спрайтов по горизонтали 
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]               # True - отражает False - не отражает      # Всё это для направления движения персонажа в игре


def load_sprite_sheets(dir1, dir2, width, height, direction=False):                        # Функция загружает спрайты из заданной директории и разбивает на отдельные изображения; dir - это параметры для указания пути, direction - должны ли спрайты разделяться на направления 
    path = join("assets", dir1, dir2)                                                      # Создает путь к директории
    images = [f for f in listdir(path) if isfile(join(path, f))]                           # Создать список файлов в указанной директории 

    all_sprites = {}                                                                       # Словарь для хранени загруженных спрайтов

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()                # Загрузить изображение в файловую переменную. Альфа-канал - это для пнг, надотдля преобразования изображения в формате с прозрачностью

        sprites = []                                                                       # Список для отдельных изображений спрайтов 
        for i in range(sprite_sheet.get_width() // width):                                 # Этот цикл перебирает все кадры (спрайты) в изображении спрайтов, вычисляя количество кадров по горизонтали, чтобы разделить спрайт-лист на отдельные изображения.
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)                 # Создается поверхность для отдельного кадра спрайта. Формат pygame.SRCALPHA используется для создания поверхности с альфа-каналом, что позволяет управлять прозрачностью.
            rect = pygame.Rect(i * width, 0, width, height)                                # Создается прямоугольник (Rect), который определяет область изображения текущего кадра на изображении спрайтов.
            surface.blit(sprite_sheet, (0, 0), rect)                                       # Отдельный кадр спрайта копируется с изображения спрайтов на созданную поверхность для того, чтобы вырезать отдельный кадр изображения спрайтов.
            sprites.append(pygame.transform.scale2x(surface))                              # Скопированный кадр спрайта увеличивается в два раза и добавляется в список для увеличения размера спрайтов для более крупного отображения на экране.

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites                    # Ключи на правосторонние и левосторонние файлы 
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):                                                                       # Это всё дело для текстуров блоков
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)                                                  # Создается прямоугольник, который определяет область изображения блока на изображении "Terrain.png". Тут блок начинается с координаты x=96 и y=0 на изображении, и его размеры равны size x size.
    surface.blit(image, (0, 0), rect)                                                      # Отдельный блок изображения блока копируется с изображения "Terrain.png" на созданную поверхность для вырезания отдельного блока изображения блока и его размещения на созданной поверхности
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Character", "Kitty", 32, 32, True)
    ANIMATION_DELAY = 3                                                                   # Задержка анимации (в кадрах)

    def __init__(self, x, y, width, height):                                              # Установить начальное состояние игрока и его атрибуты
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)                                      # Прямоугольник, представляющий положение и размеры игрока на экране
        self.x_vel = 0                                                                    # Скорости по горизонтали 
        self.y_vel = 0                                                                    # И вертикали
        self.mask = None
        self.direction = "left"                                                           # Направление движения
        self.animation_count = 0                                                          # Переменные для управления анимацией и состоянием игрока
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8                                                    # (Умножение на -1 для того, чтбы прыгал вверх, на 8 для регулировки прыжка)
        self.animation_count = 0
        self.jump_count += 1                                                              # Счетчик нужен для падения перед следущим прыжком
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)                     # Обновляет вертикальную скорость игрока, чтобы он двигался вниз под воздействием гравитации. (скорость увеличивается на величину, которая является минимумом между 1 и (self.fall_count / fps) * self.GRAVITY. fall_count увеличивается с каждой итерацией цикла, что приводит к увеличению воздействия гравитации с течением времени)
        self.move(self.x_vel, self.y_vel)                                                # Обновляет положение игрока на основе его текущих скоростей

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:                                                     # Кд 2 секунды перед следущим ударом
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1                                                             # Скорость падения
        self.update_sprite()

    def landed(self):                                                                    # Функция для приземления
        self.fall_count = 0                                                              # Игрок больше не падает, поэтому счетчик сбрасывается
        self.y_vel = 0                                                                   # Больше не двигается вверх или вниз
        self.jump_count = 0                                                              # Игрок больше не прыгает, поэтому счетчик сбрасывается

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1                                                                 # Отскочить от потолка

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //                                        # Рассчитывается индекс текущего спрайта на основе счетчика анимации
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]                                            # Устанавливается текущий спрайт игрока из списка спрайтов, используя рассчитанный индекс. Таким образом, на каждой итерации анимации используется новый спрайт.
        self.animation_count += 1                                                      # Увеличивается счетчик анимации на единицу для корректного переключения спрайтов на следующем кадре
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))           # Обновить прямоугольник, определяющий положение и размеры спрайта. get_rect() вызывается для получения прямоугольника, соответствующего текущему спрайту, а параметр topleft устанавливает его положение в соответствии с текущим положением спрайта.
        self.mask = pygame.mask.from_surface(self.sprite)                              # Создается маска для определения коллизий. Маска - это бинарное изображение, которое представляет форму спрайта. Она используется для определения столкновений между спрайтами

    def draw(self, win, offset_x):                                                     # метод отображает спрайт на экране. Функция blit() копирует изображение self.sprite на указанную поверхность win (которая представляет экран игры) в указанную позицию
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))                   # Позиция определяется как (self.rect.x - offset_x, self.rect.y). Здесь offset_x используется для смещения спрайта на экране. Спрайт отображается на экране в его текущем положении, учитывая смещение по оси X.


class Object(pygame.sprite.Sprite):                                                    # Представление объектов
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):                                                     # Отрисовка на экран
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def get_start(size):                                                                       
    path = join("assets", "Checkpoint", "Start.png")                                   # Все функции ниже с припиской get для взятия спрайтов объектов
    image = pygame.image.load(path).convert_alpha()                                    # Классы ниже - это сами объекты
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)                                                  
    surface.blit(image, (0, 0), rect)                                                      
    return pygame.transform.scale2x(surface)


def get_finish(size):                                                                       
    path = join("assets", "Checkpoint", "Finish.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)                                                  
    surface.blit(image, (0, 0), rect)                                                      
    return pygame.transform.scale2x(surface)

class Start(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        start = get_start(size)
        self.image.blit(start, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Finish(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        finish = get_finish(size)
        self.image.blit(finish, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

def get_thorn(size):                                                                       
    path = join("assets", "Enemies", "Thorn.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)                                                  
    surface.blit(image, (0, 0), rect)                                                      
    return pygame.transform.scale2x(surface)

class Thorn(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        thorn = get_thorn(size)
        self.image.blit(thorn, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def get_background(name):                                                               # Это фон, он состоит из множетсва фрагментов изображения
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()                                              # Прямоугольник, который описывает границы изображения, в _ назначаются другие координаты
    tiles = []                                                                          # Список для позиций фрагментов

    for i in range(WIDTH // width + 1):                                                 # Цикл проходит через диапазон горизонтальных фрагментов
        for j in range(HEIGHT // height + 1):                                           # Вертикальных
            pos = (i * width, j * height)                                               # Вычисляет позицию каждого фрагмента на основе его ширины и высоты
            tiles.append(pos)                                                           # Добавить каждую позицию в список

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):                      # Отрисовка всего на экран
    for tile in background:
        window.blit(bg_image, tile)                                                     # Эффект плавного движения фона

    for obj in objects:
        obj.draw(window, offset_x)                                                      # offset_x для смещения объектов при прокрутке экрана

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "thorn":
            player.make_hit()


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size)]

    offset_x = 0
    scroll_area_width = 200


    start = Start(200, HEIGHT - block_size * 1.5, block_size) 
    finish = Finish(WIDTH - block_size * 3, HEIGHT - block_size * 1.5, block_size) 

    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), start, finish] 
    
    thorn = Thorn(WIDTH // 2, HEIGHT - block_size * 1.6 , block_size)

    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), start, finish, thorn]

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
