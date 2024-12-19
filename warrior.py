import random
import math
import pygame
import time 
from os import listdir
from os.path import isfile, join
from pygame import mixer

pygame.init()
pygame.display.set_caption("Warrior")

mixer.music.load("assets/Songs/Platformer_song.mp3")
mixer.music.play(-1)

FONT = pygame.font.Font(None, 74)
restart_img = pygame.image.load("assets/menu1/restart_btn.png")
start_img = pygame.image.load("assets/menu1/start_btn.png")
exit_img = pygame.image.load('assets/menu1/exit_btn.png')

WIDTH, HEIGHT = 900, 700
FPS = 60
PLAYER_VEL = 5
window = pygame.display.set_mode((WIDTH, HEIGHT))

start_time = pygame.time.get_ticks()
timer = 60
font = pygame.font.SysFont("Arial", 24)


bonus_time = 0

def show_tutorial(window):
    window.fill((0, 0, 0))  # Black background
    tutorial_font = pygame.font.Font(None, 36)
    instructions = [
        "Welcome to Warrior!",
        "Controls:",
        "- Move Left: A or Left Arrow",

        
        "- Move Right: D or Right Arrow",
        "- Jump: Space (Double jump allowed)",
        "",
        "Avoid traps and reach the end before the timer runs out!",
        
        
    ]
    y_offset = 100
    for line in instructions:
        text_surface = tutorial_font.render(line, True, (255, 0, 0))
        window.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset))
        y_offset += 40

    pygame.display.update()

def update_timer(increment=0):
    global start_time, bonus_time
    bonus_time += increment 

def calculate_timer():
    global timer
    current_time = pygame.time.get_ticks()  # Get the current time in milliseconds
    elapsed_seconds = (current_time - start_time) // 1000  # Convert milliseconds to seconds
    timer = max(0, 60 + (bonus_time // 1000) - elapsed_seconds)

def display_timer(window):
    global timer
    calculate_timer()  # Ensure the timer is updated before displaying
    time_text = font.render(f"Time: {timer}s", True, (255, 255, 255))
    window.blit(time_text, (10, 10))


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
        self.hit = False
        self.hit_count = 0
        self.rect = pygame.Rect(x, y, width, height)
    
    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1 
        if self.jump_count == 1: 
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
    
    def make_hit(self):
        self.hit = True
        self.hit_count = 0

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
        if self.hit:
            self.hit_count +=1
        if self.hit_count > fps*2:
            self.hit = False
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
        if self.hit:
            sprite_sheet = "hit"
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

    def reset_position(self, x, y):
       
        self.rect.x = x
        self.rect.y = y
        self.x_vel = 0  
        self.y_vel = 0 
    

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
    display_timer(window)
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
   
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]


    for obj in to_check:
        if obj and (obj.name == "fire" or obj.name == "saw" or obj.name == "fan"):
            player.make_hit()
            update_timer(-100)


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
    background_menu = pygame.image.load('assets/background_menu.png')
    window.blit(background_menu, (0, 0))
    start_button_rect = start_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    window.blit(start_img, start_button_rect)
    exit_button_rect = exit_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    window.blit(exit_img, exit_button_rect)
    pygame.display.update()
    return start_button_rect, exit_button_rect

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
        super().__init__(x, y, width, height, "Fan")
        self.fan = load_sprite_sheets("Traps", "Fan", width, height)
        print("Fan sprites loaded:", self.fan.keys()) 
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
    global timer, start_time
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink.png")
    block_size = 96
    player = Player(100, 100, 50, 50)

    # Show tutorial if in menu state
    in_menu = True  # Assuming in_menu is True at the start
    if in_menu:
        show_tutorial(window)
        time.sleep(5)  # Pause for a few seconds to let the player read the tutorial
        in_menu = False  

    # Initialize all objects
    stop = Stop(4000, HEIGHT - block_size - (64 * 2), 64, 64)
    stop.on()
    start = Start(-20, HEIGHT - block_size - (64 * 4 - 32), 64, 64)
    start.on()
    fire = Fire(180, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    saw = Saw(380, HEIGHT - block_size - 64, 32, 32)
    saw.on()
    fan = Fan(block_size * 8, HEIGHT - block_size * 4 - 16, 24, 8)
    fan.on()

    fruit1 = Fruit(550, HEIGHT - block_size - 64, 32, 32, "Strawberry")
    fruit2 = Fruit(650, HEIGHT - block_size - 64, 32, 32, "Cherries")
    fruit3 = Fruit(750, HEIGHT - block_size - 64, 32, 32, "Apple")
    fruit1.on()
    fruit2.on()
    fruit3.on()
    fruit_group = pygame.sprite.Group(fruit1, fruit2, fruit3)

    # Platforms and floors
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(- WIDTH // block_size, (WIDTH * 5) // block_size)]
    floor2 = [Block(i * block_size + 180, HEIGHT - block_size * 4, block_size) for i in range(5)]
    floor3 = [Block(i * block_size + 900, HEIGHT - block_size * 5, block_size) for i in range(3)]
    floor4 = [Block(i * block_size + 1450, HEIGHT - block_size * 3, block_size) for i in range(2)]
    floor5 = [Block(i * block_size + 1900, HEIGHT - block_size * 5, block_size) for i in range(4)]
    floor6 = [Block(i * block_size + 2300, HEIGHT - block_size * 6, block_size) for i in range(3)]
    floor7 = [Block(i * block_size + 2500, HEIGHT - block_size * 4, block_size) for i in range(5)]
    floor8 = [Block(i * block_size + 3300, HEIGHT - block_size * 6, block_size) for i in range(3)]
    
    objects = [
        *floor, *floor2, *floor3, *floor4, *floor5, *floor6, *floor7, *floor8, 
        Block(0, HEIGHT - block_size * 2, block_size),
        Block(block_size * 8, HEIGHT - block_size * 4, block_size),
        Block(block_size * 12, HEIGHT - block_size * 2, block_size),
        Block(block_size * 18, HEIGHT - block_size * 4, block_size),
        Block(block_size * 33, HEIGHT - block_size * 5, block_size),
        fire, saw, fan, start, stop
    ]
    offset_x = 0
    scroll_area_width = 200

    # Game state
    in_menu = True
    game_over = False
    game_over_time = 0
    run = True

    while run:
        clock.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and player.jump_count < 2:
                        player.jump()

        if game_over:
            # Handle "Game Over" screen
            if pygame.time.get_ticks() - game_over_time > 5000:  # 5 seconds elapsed
                # Reset game state after 5 seconds
                game_over = False
                timer = 60  # Reset timer
                player.reset_position(100, 100)  # Reset player position
                player.x_vel, player.y_vel = 0, 0  # Reset velocities
                offset_x = 0  # Reset scrolling
            else:
                # Show "Game Over" message
                game_over_text = FONT.render("Game Over", True, (255, 0, 0))
                window.fill((0, 0, 0))  # Clear screen
                window.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
                pygame.display.update()
                continue  # Skip the rest of the loop
        
        # Update game state if not in menu or game over
        if not in_menu and not game_over:
            update_timer(-1)
            player.loop(FPS)
            fire.loop()
            saw.loop()
            fan.loop()
            stop.loop()
            start.loop()

            # Check collisions with fruits
            for fruit in fruit_group:
                if pygame.sprite.collide_rect(player, fruit):
                    fruit_group.remove(fruit)
                    update_timer(2000)

            # Handle movement
            handle_move(player, objects)

            # Check if the timer ran out
            if timer <= 0:
                game_over = True
                game_over_time = pygame.time.get_ticks()

            # Draw game elements
            draw(window, background, bg_image, player, objects, offset_x, fruit_group)

            # Adjust scrolling
            if ((player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or 
                (player.rect.left - offset_x <= scroll_area_width and player.x_vel < 0)):
                offset_x += player.x_vel

        else:
            # Display menu
            start_rect, exit_rect = draw_menu(window)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_rect.collidepoint(mouse_pos):
                    in_menu = False
                elif exit_rect.collidepoint(mouse_pos):
                    run = False

        pygame.display.update()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)

