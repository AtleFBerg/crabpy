from collections import defaultdict
import pygame
from entities.boat import Boat
from entities.crab import Crab
from entities.crab_pot import CrabPot
from entities.food import *
import utils
import config

# Initialize the game
pygame.init()

# Set up the screen

screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption('Crabpy')
clock = pygame.time.Clock()

camera_x = 0
camera_y = 0

pygame.font.init()
font = pygame.font.SysFont('Arial', 24)

# Boat
boat = Boat(100, 100)
boat.sprite = pygame.image.load("sprites/boat.png").convert_alpha()
boat.sprite = pygame.transform.scale(boat.sprite, (144, 96))

#Water animation
water_tile = pygame.image.load("sprites/water_tile.png").convert_alpha()
water_tile = pygame.transform.scale(water_tile, (32, 32))
water_tile_width, water_tile_height = water_tile.get_width(), water_tile.get_height()
scroll_x = 0
scroll_y = 0
scroll_speed = 0.5  

# Sea bed animation
sea_bed_tile = pygame.image.load("sprites/sea_bed_tile.png").convert_alpha()
sea_bed_tile = pygame.transform.scale(sea_bed_tile, (32, 32))
sea_bed_tile_width, sea_bed_tile_height = sea_bed_tile.get_width(), sea_bed_tile.get_height()

# Bait
selected_bait = None

# Set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

timer = 0

# Toggle button for view mode
view_mode = "above"
toggle_button_rect = pygame.Rect(config.SCREEN_WIDTH / 2, 20, 150, 40)  # x, y, width, height 


# Set up the crabs
crabs: list[Crab] = []
crab_sprites = []
for i in range(5):
    crab = Crab()
    crabs.append(crab)
    crab_sprite = pygame.image.load(crab.sprite())
    crab_sprites.append(crab_sprite)

# Set up the crab pot
# crab_pot = CrabPot(x=500, y=400, bait=None, width=100, height=100)
# crab_pot_sprite = pygame.image.load("sprites/crab_pot.png").convert_alpha()

bait_images = {
    'Seaweed': pygame.transform.scale(pygame.image.load('sprites/seaweed.png').convert_alpha(), (32, 32)),
    'Shrimp': pygame.transform.scale(pygame.image.load('sprites/shrimp.png').convert_alpha(), (32, 32)),
    'Clam': pygame.transform.scale(pygame.image.load('sprites/clam.png').convert_alpha(), (32, 32)),
    'FishRemains': pygame.transform.scale(pygame.image.load('sprites/fishremains.png').convert_alpha(), (32, 32)),
    'Plankton': pygame.transform.scale(pygame.image.load('sprites/plankton.png').convert_alpha(), (32, 32)),
    'Starfish': pygame.transform.scale(pygame.image.load('sprites/starfish.png').convert_alpha(), (32, 32)),
}

# Create lists to store food objects and their sprites
all_food: list[Food] = []

utils.world_food_respawn(all_food)

# Set up the game loop
running = True
while running:
    # Fill the screen with white
    screen.fill(WHITE)

    # Camera movement
    scroll_x = (scroll_x + scroll_speed) % water_tile_width
    scroll_y = (scroll_y + scroll_speed) % water_tile_height
    
    # Draw the water tiles
    if view_mode == "above":
        for y in range(-water_tile_height, config.SCREEN_HEIGHT + water_tile_height, water_tile_height):
            for x in range(-water_tile_width, config.SCREEN_WIDTH + water_tile_width, water_tile_width):
                screen.blit(water_tile, (x - scroll_x, y - scroll_y))
    else:
        for y in range(-sea_bed_tile_height, config.WORLD_HEIGHT + sea_bed_tile_height, sea_bed_tile_height):
            for x in range(-sea_bed_tile_width, config.WORLD_WIDTH + sea_bed_tile_width, sea_bed_tile_width):
                screen.blit(sea_bed_tile, (x - camera_x, y - camera_y))

    if selected_bait:
        bait_text = f"Bait: {selected_bait.__class__.__name__}"
    else:
        bait_text = "Bait: None"

    bait_surface = font.render(bait_text, True, (0, 0, 0))  # Black text
    screen.blit(bait_surface, (700, 10))  # Top-left corner

    food_to_remove = []

    # Male/Female count
    m, f = Crab.count_sexes(crabs)
    font = pygame.font.SysFont(None, 30)
    text_surface = font.render(f"Males: {m}  Females: {f}", True, (0, 0, 0))
    screen.blit(text_surface, (10, 10))  # Top-left corner
    
    
    # Draw all crabs dynamically
    for crab, crab_sprite in zip(crabs, crab_sprites):
        if view_mode == "underwater":
            screen.blit(crab_sprite, (crab.x - camera_x, crab.y - camera_y))

        crab.make_decision(all_crabs=crabs, crab_sprites=crab_sprites,                            
                              potential_food=all_food)

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
            if not food.is_bait:
                all_food.pop(index)
    
    food_counts = defaultdict(int)
    for food in all_food:
        food_counts[type(food)] += 1
    timer += 1
    if timer % 2000 == 0:
        utils.world_food_respawn(all_food)
        timer = 0

    # Draw all food items dynamically
    for food in all_food:
        new_food = food.update(food_counts)  # let food handle respawning
        if new_food:
            all_food.append(new_food)
        if view_mode == "underwater":
            screen.blit(food.sprite, (food.x - camera_x, food.y - camera_y))

    # Draw the crab pot
    if boat.pots:
        for crab_pot in boat.pots:
            screen_x = crab_pot.x - camera_x
            screen_y = crab_pot.y - camera_y

            if view_mode == "above":
                # Draw buoy sprite if pot is lowered
                if crab_pot.lowered:
                    screen.blit(crab_pot.buoy_sprite, (screen_x, screen_y))
                else:
                    # Optional: draw pot on deck, or just skip
                    pygame.draw.rect(screen, (100, 100, 100), (screen_x, screen_y, crab_pot.width, crab_pot.height), 1)

            elif view_mode == "underwater":
                # Draw underwater crab pot
                screen.blit(crab_pot.underwater_pot_sprite, (screen_x, screen_y))

                # Draw bait inside pot if it has bait
                if crab_pot.lowered and crab_pot.bait:
                    crab_pot.bait_sprite = bait_images.get(type(crab_pot.bait).__name__)
                    if crab_pot.bait_sprite:
                        bait_rect = crab_pot.bait_sprite.get_rect()
                        bait_x = screen_x + (crab_pot.width - bait_rect.width) // 2
                        bait_y = screen_y + (crab_pot.height - bait_rect.height) // 2 - 4  # Adjust up by 4px
                        screen.blit(crab_pot.bait_sprite, (bait_x, bait_y))

            crab_pot.check_for_crabs(crabs)
    
    averages = utils.calculate_average_preferences(crabs)

    y_offset = 100
    for food_type, avg in averages.items():
        text = f"{food_type.__name__}: {avg:.2f}"
        text_surface = font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (10, y_offset))
        y_offset += 20
    clock.tick(30)

    # Draw the toggle button
    button_color = (0, 100, 200) if view_mode == "above" else (0, 0, 100)
    pygame.draw.rect(screen, button_color, toggle_button_rect)
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"View: {view_mode}", True, (255, 255, 255))
    screen.blit(text, (toggle_button_rect.x + 10, toggle_button_rect.y + 10))

    if view_mode == "above":
        boat.update()
        boat.draw(screen, camera_x, camera_y)
    # Update the display
    pygame.display.flip()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Check if boat is over a crab pot
                pot_under_boat = None
                MARGIN = 256  # Margin for collision detection
                for pot in boat.pots:
                    if (
                        abs(pot.x - boat.x) < MARGIN // 2 and
                        abs(pot.y - boat.base_y) < MARGIN // 2
                    ):
                        pot_under_boat = pot
                        break

                if pot_under_boat:
                    # Raise the pot if it's already lowered
                    if pot_under_boat.lowered:
                        pot_under_boat.raise_pot()
                    else:
                        pot_under_boat.lower()
                else:
                    # No pot under boat, drop a new one
                    boat.drop_pot(selected_bait, all_food)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if toggle_button_rect.collidepoint(event.pos):
                view_mode = "underwater" if view_mode == "above" else "above"
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        boat.x -= 2
        if not boat.facing_left:
            boat.facing_left = True
            boat.sprite = pygame.transform.flip(boat.sprite, True, False)

    if keys[pygame.K_RIGHT]:
        boat.x += 2
        if boat.facing_left:
            boat.facing_left = False
            boat.sprite = pygame.transform.flip(boat.sprite, True, False)
    if keys[pygame.K_UP]: boat.base_y -= 2
    if keys[pygame.K_DOWN]: boat.base_y += 2

    if keys[pygame.K_1]: selected_bait = Seaweed(is_bait=True)
    if keys[pygame.K_2]: selected_bait = Shrimp(is_bait=True)
    if keys[pygame.K_3]: selected_bait = Clam(is_bait=True)
    if keys[pygame.K_4]: selected_bait = FishRemains(is_bait=True)
    if keys[pygame.K_5]: selected_bait = Plankton(is_bait=True)
    if keys[pygame.K_6]: selected_bait = Starfish(is_bait=True)
    
    # if keys[pygame.K_1]: crab_pot.set_bait(Seaweed())
    # if keys[pygame.K_2]: crab_pot.set_bait(Shrimp())
    # if keys[pygame.K_3]: crab_pot.set_bait(Clam())
    # if keys[pygame.K_4]: crab_pot.set_bait(FishRemains())
    # if keys[pygame.K_5]: crab_pot.set_bait(Plankton())
    # if keys[pygame.K_6]: crab_pot.set_bait(Starfish())
    
    camera_x, camera_y = utils.update_camera(boat)

    
    

        
# Quit the game
pygame.quit()
