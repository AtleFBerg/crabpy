from collections import defaultdict
import pygame
from entities.crab import Crab
from entities.crab_pot import CrabPot
from entities.food import *
import utils

# Initialize the game
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((1024, 800))
pygame.display.set_caption('Crabpy')
clock = pygame.time.Clock()

pygame.font.init()
font = pygame.font.SysFont('Arial', 24)

# Set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

timer = 0

# Set up the crabs
crabs: list[Crab] = []
crab_sprites = []
for i in range(5):
    crab = Crab()
    crabs.append(crab)
    crab_sprite = pygame.image.load(crab.sprite())
    crab_sprites.append(crab_sprite)

# Set up the crab pot
crab_pot = CrabPot(x=500, y=400, bait=None, width=100, height=100)
# crab_pot_sprite = pygame.image.load("sprites/crab_pot.png").convert_alpha()

bait_images = {
    'Seaweed': pygame.transform.scale(pygame.image.load('sprites/seaweed.png').convert_alpha(), (32, 32)),
    'Shrimp': pygame.transform.scale(pygame.image.load('sprites/shrimp.png').convert_alpha(), (32, 32))
}

# Create lists to store food objects and their sprites
all_food: list[Food] = []
food_sprites = []

utils.world_food_respawn(all_food, food_sprites)

# Set up the game loop
running = True
while running:
    # Fill the screen with white
    screen.fill(WHITE)

    if crab_pot.bait:
        bait_text = f"Bait: {crab_pot.bait.__name__}"
    else:
        bait_text = "Bait: None"

    bait_surface = font.render(bait_text, True, (0, 0, 0))  # Black text
    screen.blit(bait_surface, (700, 10))  # Top-left corner

    food_to_remove = []

    m, f = Crab.count_sexes(crabs)
    font = pygame.font.SysFont(None, 30)
    text_surface = font.render(f"Males: {m}  Females: {f}", True, (0, 0, 0))
    screen.blit(text_surface, (10, 10))  # Top-left corner

    for crab, crab_sprite in zip(crabs, crab_sprites):
        screen.blit(crab_sprite, (crab.x, crab.y))

        crab.make_decision(all_crabs=crabs, crab_sprites=crab_sprites,                            
                              potential_food=all_food, crab_pot=crab_pot,)

        # Mark food for removal if eaten
        if hasattr(crab, "food_to_remove") and crab.food_to_remove:
            food_to_remove.append(crab.food_to_remove)
            crab.food_to_remove = None  # Reset after marking for removal
        
        crab.energy -= 0.01
        if crab.energy <= 0:
            print("Crab died due to lack of energy.")
            crabs.remove(crab)
            crab_sprites.remove(crab_sprite)  # Remove corresponding sprite


    # Remove eaten food after iteration
    for food in food_to_remove:
        if food in all_food:
            index = all_food.index(food)
            all_food.pop(index)
            food_sprites.pop(index)  # Remove corresponding sprite
    
    food_counts = defaultdict(int)
    for food in all_food:
        food_counts[type(food)] += 1
    timer += 1
    if timer % 2000 == 0:
        utils.world_food_respawn(all_food, food_sprites)
        timer = 0
    # Draw all food items dynamically
    for food, food_sprite in zip(all_food, food_sprites):
        new_food = food.update(food_counts)  # let food handle respawning
        if new_food:
            all_food.append(new_food)
            food_sprites.append(pygame.transform.scale(pygame.image.load(new_food.sprite()).convert_alpha(), (25, 25)))
        screen.blit(food_sprite, (food.x, food.y))

    if crab_pot.lowered and crab_pot.bait:
        bait_sprite = bait_images.get(crab_pot.bait.__name__)
        pygame.draw.rect(screen, (100, 50, 0), (crab_pot.x, crab_pot.y, crab_pot.width, crab_pot.height), 2)
        if bait_sprite:
            screen.blit(bait_sprite, (crab_pot.x + 25, crab_pot.y + 25))  # Hover above pot
            screen.blit(bait_sprite, (crab_pot.x + 50, crab_pot.y + 25))  # Hover above pot
            screen.blit(bait_sprite, (crab_pot.x + 35, crab_pot.y + 50))  # Hover above pot
        crab_pot.check_for_crabs(crabs)
    else:
        pygame.draw.rect(screen, (100, 100, 100), (crab_pot.x, crab_pot.y, crab_pot.width, crab_pot.height), 1)
    
    averages = utils.calculate_average_preferences(crabs)

    y_offset = 100
    for food_type, avg in averages.items():
        text = f"{food_type.__name__}: {avg:.2f}"
        text_surface = font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (10, y_offset))
        y_offset += 20
    clock.tick(30)

    # Update the display
    pygame.display.flip()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if crab_pot.lowered:
                    crab_pot.raise_pot()
                else:
                    crab_pot.lower()
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: crab_pot.x -= 2
    if keys[pygame.K_RIGHT]: crab_pot.x += 2
    if keys[pygame.K_UP]: crab_pot.y -= 2
    if keys[pygame.K_DOWN]: crab_pot.y += 2

    if keys[pygame.K_1]: crab_pot.bait = Seaweed
    if keys[pygame.K_2]: crab_pot.bait = Shrimp
        
        
    


# Quit the game
pygame.quit()
