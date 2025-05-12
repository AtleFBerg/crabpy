import asyncio
from collections import defaultdict
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
from views.sea import SeaView


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

# Initialize views
views = {
    "sea": SeaView(),
}
view = "sea"
current_view = views[view]

# Toggle button for view mode
toggle_button_rect = pygame.Rect(config.SCREEN_WIDTH / 2, 20, 150, 40)

# Set up the crabs
for i in range(config.INITIAL_CRAB_COUNT):
    all_crabs.append(Crab())

async def main():
    global camera_x, camera_y, selected_bait, timer, view, all_crabs, all_food, crab_inventory, running, current_view

    while running:
        clock.tick(30)

        # Update and draw the current view
        current_view.update(screen, camera_x, camera_y, all_crabs, all_food, timer, boat)

        # GUI
        gui_elements.draw_average_crab_food_preferences(screen, all_crabs, font)
        gui_elements.draw_toggle_button(screen, toggle_button_rect, font, view)
        gui_elements.draw_current_crab_count(screen, crab_inventory, font)
        gui_elements.draw_selected_bait(screen, selected_bait, font)
        gui_elements.draw_crab_count(all_crabs, screen)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not selected_bait:
                        continue
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
                    current_view.underwater = not current_view.underwater
                    # view = "sea" if view == "town" else "town"  # Example toggle logic
                    # current_view = views[view]

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
