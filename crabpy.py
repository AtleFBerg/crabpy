from collections import defaultdict
import pygame
from animations.underwater_animation import UnderwaterAnimation
from animations.water_animation import WaterAnimation
from entities.boat import Boat
from entities.crab import Crab
from entities.food import *
import utils
import config

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 24)

# Set up the screen

screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption('Crabpy')
clock = pygame.time.Clock()


# World variables
camera_x = 0
camera_y = 0
selected_bait = None
timer = 0
boat = Boat(100, 100)
all_food: list[Food] = []
utils.world_food_respawn(all_food)

# Animations
water_animation = WaterAnimation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
underwater_animation = UnderwaterAnimation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

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

# Set up the game loop
running = True
while running:
    # Fill the screen with white
    screen.fill((255, 255, 255))
    
    # Draw the water tiles
    if view_mode == "above":
        water_animation.update()
        water_animation.draw(screen)
    else:
        underwater_animation.draw(screen)

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
                screen.blit(crab_pot.buoy_sprite, (screen_x, screen_y))
                

            elif view_mode == "underwater":
                # Draw underwater crab pot
                screen.blit(crab_pot.underwater_pot_sprite, (screen_x, screen_y))

            crab_pot.check_for_crabs(crabs, all_food)
    
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
                MARGIN = 100
                pot_under_boat = None
                for pot in boat.pots:
                    if (
                        abs(pot.x - boat.x) < MARGIN // 2 and
                        abs(pot.y - boat.base_y) < MARGIN // 2
                    ):
                        pot_under_boat = pot
                        break

                if pot_under_boat:
                    boat.raise_pot(pot_under_boat, all_food)
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
    
    camera_x, camera_y = utils.update_camera(boat)
   
# Quit the game
pygame.quit()
