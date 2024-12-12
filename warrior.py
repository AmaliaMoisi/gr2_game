import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()
pygame.display.set_caption("Warrior")

restart_img = pygame.image.load("assets/menu1/restart_btn.png")
start_img = pygame.image.load("assets/menu1/start_btn.png")

WIDTH, HEIGHT = 900, 700
FPS = 60
PLAYER_VEL = 5
window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]  

    all_sprites = {}
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []  
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        base_name = image.replace(".png", "")  
        if direction:
            all_sprites[f"{base_name}_right"] = sprites
            all_sprites[f"{base_name}_left"] = flip(sprites)
        else:
            all_sprites[base_name] = sprites
    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 128 , size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface) 

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = [i * width, j * height]
            tiles.append(pos)
    return tiles, image

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
    
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1 
        if self.jump_count == 1: 
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

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
        self.y_vel += min(1, (self.fall_count/ fps) *self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        self.fall_count += 1
        self.update_sprite()
    
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet= "idle"
        if self.x_vel != 0:
            sprite_sheet= "run"
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height , name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Start(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "start")
        self.start = load_sprite_sheets("Items", "Start", width, height)
        self.image = self.start["Idle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Idle"

    def on(self):
        self.animation_name = "Moving"

    def off(self):
        self.animation_name = "Idle"

    def loop(self):
        sprites = self.start[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Stop(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "stop")
        self.stop = load_sprite_sheets("Items", "End", width, height)
        self.image = self.stop["Idle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Idle"

    def on(self):
        self.animation_name = "Moving"

    def off(self):
        self.animation_name = "Idle"

    def loop(self):
        sprites = self.stop[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def draw(window, background, bg_image, player, objects, offset_x, fruit_group):
    for tile in background:
        window.blit(bg_image, tile)
    for obj in objects:
        obj.draw(window,offset_x)
    for fruit in fruit_group:
        fruit.draw(window, offset_x)
    player.draw(window,offset_x)
    pygame.display.update()

def handle_move(player, objects):
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    collide_left= collide(player, objects, -PLAYER_VEL*2)
    collide_right= collide(player, objects, PLAYER_VEL*2)



    if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and not collide_left:
        player.move_left(PLAYER_VEL)
    if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and not collide_right:
        player.move_right(PLAYER_VEL)
   
    handle_vertical_collision(player, objects, player.y_vel)

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


def draw_menu(window):
    window.fill((0, 0, 0)) 

    start_button_rect = start_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    window.blit(start_img, start_button_rect)

    restart_button_rect = restart_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    window.blit(restart_img, restart_button_rect)

    pygame.display.update()

    return start_button_rect, restart_button_rect

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Saw(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "saw")
        self.saw = load_sprite_sheets("Traps", "Saw", width, height)
        self.image = self.saw["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.saw[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Fan(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fan")
        self.fan = load_sprite_sheets("Traps", "Fan", width, height)
        self.image = self.fan["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fan[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Fruit(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, fruit_name="Strawberry"):
        super().__init__(x, y, width, height, "fruit")
        self.fruit = load_sprite_sheets("Items", "Fruits", width, height)
        self.animation_name=fruit_name
        self.image = self.fruit[self.animation_name][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0

    def on(self):
        self.image=self.fruit[self.animation_name][0]
        self.mask = pygame.mask.from_surface(self.image)

    def loop(self):
        sprites = self.fruit[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0
    
    def draw(self, window, offset_x=0):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink.png")
    block_size = 96
    player = Player(100, 100, 50, 50)

    stop = Stop(4000,HEIGHT - block_size - (64*2), 64, 64)
    stop.on()
    start = Start(-20,HEIGHT - block_size - (64*4 -32), 64, 64)
    start.on()

    fire = Fire(180, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    saw = Saw(380, HEIGHT - block_size - 64, 32, 32)
    saw.on()
    fan = Fan(block_size * 8, HEIGHT - block_size * 4 - 16 , 24, 8)
    fan.on()

    fruit1 = Fruit(550, HEIGHT - block_size - 64, 32, 32, "Strawberry")
    fruit2 = Fruit(650, HEIGHT - block_size - 64, 32, 32, "Cherries")
    fruit3 = Fruit(750, HEIGHT - block_size - 64, 32, 32, "Apple")
    fruit1.on()
    fruit2.on()
    fruit3.on()
    fruit_group = pygame.sprite.Group(fruit1, fruit2, fruit3)

    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(- WIDTH//block_size, (WIDTH*5)//block_size) ]
    floor2 = [Block(i * block_size + 180, HEIGHT - block_size * 4, block_size) for i in range(5)]
    floor3 = [Block(i * block_size + 900, HEIGHT - block_size * 5, block_size) for i in range(3)]
    floor4 = [Block(i * block_size + 1450, HEIGHT - block_size * 3, block_size) for i in range(2)]
    floor5 = [Block(i * block_size + 1900, HEIGHT - block_size * 5, block_size) for i in range(4)]
    floor6 = [Block(i * block_size + 2300, HEIGHT - block_size * 6, block_size) for i in range(3)]
    floor7 = [Block(i * block_size + 2500, HEIGHT - block_size * 4, block_size) for i in range(5)]
    floor8 = [Block(i * block_size + 3300, HEIGHT - block_size * 6, block_size) for i in range(3)]
    #blocks = [Block(0, HEIGHT - block_size, block_size)]
    objects = [*floor, start, stop]
    in_menu = True
    objects = [*floor, *floor2, *floor3, *floor4, *floor5, *floor6, *floor7, *floor8, Block(0, HEIGHT - block_size * 2, block_size),
            Block(block_size * 8 , HEIGHT - block_size * 4 , block_size), Block(block_size * 12 , HEIGHT - block_size * 2 , block_size), 
            Block(block_size * 18 , HEIGHT - block_size * 4 , block_size), Block(block_size * 33 , HEIGHT - block_size * 5 , block_size), fire, saw, fan, start, stop]
    offset_x = 0
    scroll_area_width = 200


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

            if in_menu:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    start_rect, restart_rect = draw_menu(window)

                    if start_rect.collidepoint(mouse_pos):
                        in_menu = False  
                    elif restart_rect.collidepoint(mouse_pos):
                        print("Restart clicked")

        if in_menu:
            draw_menu(window)
        else:
            player.loop(FPS)
            fire.loop()
            saw.loop()
            fan.loop()
            stop.loop()
            start.loop()
            fruit1.loop()
            fruit2.loop()
            fruit3.loop()
            handle_move(player, objects)
            draw(window, background, bg_image, player, objects, offset_x, fruit_group)
            for fruit in fruit_group:
                if pygame.sprite.collide_rect(player, fruit):
                    fruit_group.remove(fruit)

            if ((player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel> 0) or (
                    (player.rect.left - offset_x <= scroll_area_width )and player.x_vel) <0):

                offset_x += player.x_vel



    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)