import pygame
import random

pygame.init()

# Initial screen size
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Traffic vs Zombie")
clock = pygame.time.Clock()

# Load images
car_img = pygame.image.load('bjj.png')
truck_img = pygame.image.load('truck.png')
small_car_img = pygame.image.load('small_car.png')
sports_car_img = pygame.image.load('sports_car.png')
zombie_walk_images_raw = [pygame.image.load(f'walk {i}.png') for i in range(1, 5)]
bg_img_raw = pygame.image.load('background.jpg')

# Load sounds
hit_sound = pygame.mixer.Sound('monster-10.wav')
crash_sound = pygame.mixer.Sound('crash.mp3')
pygame.mixer.music.load('background_music.wav')
pygame.mixer.music.play(-1)

# Fonts
font = pygame.font.SysFont("comicsans", 30)

def scale_assets():
    global car_img, truck_img, small_car_img, sports_car_img, zombie_walk_images, bg
    car_img = pygame.transform.scale(pygame.image.load('bjj.png'), (80, 120))
    truck_img = pygame.transform.scale(pygame.image.load('truck.png'), (100, 140))
    small_car_img = pygame.transform.scale(pygame.image.load('small_car.png'), (80, 100))
    sports_car_img = pygame.transform.scale(pygame.image.load('sports_car.png'), (100, 130))
    zombie_walk_images = [pygame.transform.scale(img, (60, 80)) for img in zombie_walk_images_raw]
    bg = pygame.transform.scale(bg_img_raw, (WIDTH, HEIGHT))

scale_assets()

class PlayerCar:
    def __init__(self):
        self.x = WIDTH // 2 - 40
        self.y = HEIGHT - 150
        self.speed = 0
        self.max_speed = 10
        self.rect = pygame.Rect(self.x, self.y, 80, 120)

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= 5
        if keys[pygame.K_RIGHT] and self.x < WIDTH - 80:
            self.x += 5

        if keys[pygame.K_UP] and self.speed < self.max_speed:
            self.speed += 0.2
        elif keys[pygame.K_DOWN] and self.speed > -5:
            self.speed -= 0.2
        else:
            if self.speed > 0:
                self.speed -= 0.1
            elif self.speed < 0:
                self.speed += 0.1

        self.y -= self.speed
        self.y = max(0, min(self.y, HEIGHT - 120))
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        screen.blit(car_img, (self.x, self.y))

    def get_center(self):
        return (self.x + self.rect.width // 2, self.y + self.rect.height // 2)

class TrafficCar:
    def __init__(self, car_type):
        self.x = self.get_non_overlapping_x()
        self.y = -random.randint(150, 400)
        self.speed = random.uniform(5, 10)  # Increased speed range
        self.type = car_type
        self.rect = pygame.Rect(self.x, self.y, 80, 120)

    def get_non_overlapping_x(self):
        x_positions = [WIDTH // 2 - 150, WIDTH // 2 - 50, WIDTH // 2 + 50, WIDTH // 2 + 150]
        existing_x = [car.x for car in cars]
        available_x = list(set(x_positions) - set(existing_x))
        return random.choice(available_x) if available_x else random.choice(x_positions)

    def move(self, player_speed):
        self.y += self.speed + player_speed
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        if self.type == "truck":
            screen.blit(truck_img, (self.x, self.y))
        elif self.type == "small_car":
            screen.blit(small_car_img, (self.x, self.y))
        elif self.type == "sports_car":
            screen.blit(sports_car_img, (self.x, self.y))

    def get_center(self):
        return (self.x + self.rect.width // 2, self.y + self.rect.height // 2)

    def is_collision(self, player_car):
        dist_x = abs(self.get_center()[0] - player_car.get_center()[0])
        dist_y = abs(self.get_center()[1] - player_car.get_center()[1])
        return dist_x < 40 and dist_y < 40

class Zombie:
    def __init__(self):
        self.x = random.randint(0, WIDTH - 60)
        self.y = -random.randint(80, 300)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(1, 3)
        self.walk_index = 0
        self.rect = pygame.Rect(self.x, self.y, 60, 80)

    def move(self, player_speed):
        self.x += self.speed_x
        self.y += self.speed_y + player_speed
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        image = zombie_walk_images[self.walk_index // 5]
        screen.blit(image, (self.x, self.y))
        self.walk_index = (self.walk_index + 1) % (len(zombie_walk_images) * 5)

def display_start_screen():
    screen.fill((0, 0, 0))
    title = font.render("Traffic vs Zombie", True, (0, 255, 0))
    prompt = font.render("Press ENTER to Start", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2))
    pygame.display.update()

def display_pause_screen():
    pause_text = font.render("Game Paused. Press ENTER to Resume", True, (255, 255, 0))
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()

# Game state
player = PlayerCar()
cars = []
zombies = []
score = 0
lives = 3
spawn_car_timer = 0
spawn_zombie_timer = 0
bg_y1 = 0
bg_y2 = -HEIGHT

game_started = False
paused = False
running = True

# Start Menu
while not game_started:
    display_start_screen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            game_started = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                game_started = True

# Main Game Loop
while running:
    clock.tick(30)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            scale_assets()
            bg_y1 = 0
            bg_y2 = -HEIGHT
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = True

    while paused:
        display_pause_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    paused = False

    # Background scroll
    bg_y1 += player.speed
    bg_y2 += player.speed
    if bg_y1 >= HEIGHT:
        bg_y1 = -HEIGHT
    if bg_y2 >= HEIGHT:
        bg_y2 = -HEIGHT
    screen.blit(bg, (0, bg_y1))
    screen.blit(bg, (0, bg_y2))

    player.move(keys)
    player.draw()

    # Traffic cars
    spawn_car_timer += 1
    if spawn_car_timer > 50:
        car_type = random.choice(["truck", "small_car", "sports_car"])
        cars.append(TrafficCar(car_type))
        spawn_car_timer = 0

    for car in cars[:]:
        car.move(player.speed)
        car.draw()
        if car.is_collision(player):
            crash_sound.play()
            lives -= 1
            cars.remove(car)
        elif car.y > HEIGHT + 150:
            cars.remove(car)

    # Zombies
    spawn_zombie_timer += 1
    if spawn_zombie_timer > 30:
        zombies.append(Zombie())
        spawn_zombie_timer = 0

    for zombie in zombies[:]:
        zombie.move(player.speed)
        zombie.draw()
        if zombie.rect.colliderect(player.rect):
            hit_sound.play()
            score += 1
            zombies.remove(zombie)
        elif zombie.y > HEIGHT + 100 or zombie.x < -100 or zombie.x > WIDTH + 100:
            zombies.remove(zombie)

    # UI
    screen.blit(font.render(f"Score: {int(score)}", True, (255, 255, 255)), (10, 10))
    screen.blit(font.render(f"Lives: {lives}", True, (255, 0, 0)), (10, 40))

    if lives <= 0:
        over_text = font.render("Game Over! Press Q to Quit", True, (255, 255, 255))
        screen.blit(over_text, (WIDTH // 2 - 150, HEIGHT // 2))
        pygame.display.update()
        pygame.time.wait(3000)
        running = False

    pygame.display.update()

pygame.quit()
