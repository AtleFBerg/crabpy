import asyncio
from collections import defaultdict
import sys
import pygame
from animations.underwater_animation import UnderwaterAnimation
from animations.water_animation import WaterAnimation
from entities.boat import Boat
from entities.crab import Crab
from entities.food import *
import services.food_service as food_service
import animations.gui_elements as gui_elements
import utils
import config


pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 30)

# Set up the screen
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption('Crabpy')
clock = pygame.time.Clock()
load_food_images()

# World variables
camera_x = 0
camera_y = 0
selected_bait = None
timer = 0
boat = Boat(100, 100)
all_food: list[Food] = []
utils.world_food_respawn(all_food)
all_crabs: list[Crab] = []
crab_inventory = {"count": 0}
running = True

# Animations
water_animation = WaterAnimation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
underwater_animation = UnderwaterAnimation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

# # Toggle button for view mode
view_mode = "above"
toggle_button_rect = pygame.Rect(config.SCREEN_WIDTH / 2, 20, 150, 40)

# Set up the crabs
for i in range(config.INITIAL_CRAB_COUNT):
    all_crabs.append(Crab())

async def main():
    global camera_x, camera_y, selected_bait, timer, view_mode, all_crabs, all_food, crab_inventory, running

    while running:
        clock.tick(30)
        screen.fill((0, 255, 0))  # Clear the screen
        # Background animation
        if view_mode == "above":
            water_animation.update()
            water_animation.draw(screen)
        else:
            underwater_animation.draw(screen, camera_x, camera_y)

        # Crab logic
        food_to_remove = []
        for crab in all_crabs:
            crab.update()
            if crab.energy <= 0.0:
                all_crabs.remove(crab)
                continue
            if view_mode == "underwater":
                screen.blit(crab.sprite, (crab.x - camera_x, crab.y - camera_y))
            crab.make_decision(all_crabs=all_crabs, potential_food=all_food)
            if crab.food_to_remove:
                food_to_remove.append(crab.food_to_remove)
                crab.food_to_remove = None

        # Food logic
        if food_to_remove:
            food_service.remove_food(food_to_remove, all_food)

        food_counts = defaultdict(int)
        for food in all_food:
            food_counts[type(food)] += 1
        timer += 1
        if timer % 2000 == 0:
            utils.world_food_respawn(all_food)
            timer = 0

        for food in all_food:
            new_food = food.update(food_counts)
            if new_food:
                all_food.append(new_food)
            if view_mode == "underwater":
                screen.blit(food.sprite, (food.x - camera_x, food.y - camera_y))

        # Crab pots
        if boat.pots:
            for crab_pot in boat.pots:
                crab_pot.draw(screen, camera_x, camera_y, view_mode)
                crab_pot.check_for_crabs(all_crabs, all_food)

        # GUI
        gui_elements.draw_average_crab_food_preferences(screen, all_crabs, font)
        gui_elements.draw_toggle_button(screen, toggle_button_rect, font, view_mode)
        gui_elements.draw_current_crab_count(screen, crab_inventory, font)
        gui_elements.draw_selected_bait(screen, selected_bait, font)
        gui_elements.draw_crab_count(all_crabs, screen)

        # Boat logic
        if view_mode == "above":
            boat.update()
            boat.draw(screen, camera_x, camera_y)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    MARGIN = 100
                    pot_under_boat = None
                    for pot in boat.pots:
                        if abs(pot.x - boat.x) < MARGIN // 2 and abs(pot.y - boat.base_y) < MARGIN // 2:
                            pot_under_boat = pot
                            break
                    if pot_under_boat:
                        boat.raise_pot(pot_under_boat, all_food, crab_inventory)
                    else:
                        boat.drop_pot(selected_bait, all_food)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if toggle_button_rect.collidepoint(event.pos):
                    view_mode = "underwater" if view_mode == "above" else "above"

        # Movement and input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            boat.x -= 2
            if not boat.facing_left:
                boat.facing_left = True
                boat.sprite = pygame.transform.flip(boat.sprite, True, False)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            boat.x += 2
            if boat.facing_left:
                boat.facing_left = False
                boat.sprite = pygame.transform.flip(boat.sprite, True, False)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            boat.base_y -= 2
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            boat.base_y += 2
        if keys[pygame.K_1]: selected_bait = Seaweed(is_bait=True)
        if keys[pygame.K_2]: selected_bait = Shrimp(is_bait=True)
        if keys[pygame.K_3]: selected_bait = Clam(is_bait=True)
        if keys[pygame.K_4]: selected_bait = FishRemains(is_bait=True)
        if keys[pygame.K_5]: selected_bait = Plankton(is_bait=True)
        if keys[pygame.K_6]: selected_bait = Starfish(is_bait=True)

        camera_x, camera_y = utils.update_camera(boat)
        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())
