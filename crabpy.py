from time import sleep
import pygame
import random
from entities.crab import Crab
from entities.food import *

# Initialize the game
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((1024, 800))
pygame.display.set_caption('Crabpy')
clock = pygame.time.Clock()

# Set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Set up the crabs
crabs: list[Crab] = []
crab_sprites = []
for i in range(4):
    crab = Crab()
    crabs.append(crab)
    crab_sprite = pygame.image.load(crab.sprite())
    crab_sprites.append(crab_sprite)


# Define food types and their probabilities (weights)
food_weights = {
    Seaweed: 0.3,       # 30% chance
    Clam: 0.15,          # 15% chance
    FishRemains: 0.1,    # 10% chance
    Plankton: 0.3,       # 30% chance
    Starfish: 0.1,       # 10% chance
    Shrimp: 0.05         # 5% chance
}

# Create lists to store food objects and their sprites
all_food: list[Food] = []
food_sprites = []

# Generate exactly 20 food items based on the given probabilities
food_classes = list(food_weights.keys())
food_probabilities = list(food_weights.values())

for i in range(20):
    food_class = random.choices(food_classes, weights=food_probabilities, k=1)[0]  # Pick a food type based on weight
    food = food_class()  # Create the food object
    all_food.append(food)  # Store it

    # Load and scale the sprite
    sprite = pygame.image.load(food.sprite()).convert_alpha()
    sprite = pygame.transform.scale(sprite, (25, 25))
    food_sprites.append(sprite)

# Set up the game loop
running = True
while running:
    # Fill the screen with white
    screen.fill(WHITE)

    food_to_remove = []

    for crab, crab_sprite in zip(crabs, crab_sprites):
        screen.blit(crab_sprite, (crab.x, crab.y))

        crab.make_decision(all_crabs=crabs, crab_sprites=crab_sprites,                            
                              potential_food=all_food)

        # Mark food for removal if eaten
        if hasattr(crab, "food_to_remove") and crab.food_to_remove:
            food_to_remove.append(crab.food_to_remove)
            crab.food_to_remove = None  # Reset after marking for removal
        
        crab.energy -= 0.05
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
  
    # Draw all food items dynamically
    for food, food_sprite in zip(all_food, food_sprites):
        new_food = food.update()  # let food handle respawning
        if new_food:
            all_food.append(new_food)
            food_sprites.append(pygame.transform.scale(pygame.image.load(new_food.sprite()).convert_alpha(), (25, 25)))
        screen.blit(food_sprite, (food.x, food.y))
    
    clock.tick(30)

    # Update the display
    pygame.display.flip()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Handle player input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and crab.x > 0:
        crab.move_left()
    if keys[pygame.K_RIGHT] and crab.x < 1024 - crab.width:
        crab.move_right()
    if keys[pygame.K_UP] and crab.y > 0:
        crab.move_up()
    if keys[pygame.K_DOWN] and crab.y < 800 - crab.height:
        crab.move_down()

# Quit the game
pygame.quit()
