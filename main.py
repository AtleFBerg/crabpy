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
        events = pygame.event.get()
        current_view.handle_events(events, selected_bait, boat, all_food, crab_inventory, toggle_button_rect)

        # Movement and input
        keys = pygame.key.get_pressed()
        selected_bait = current_view.handle_keys(keys, boat, selected_bait)
        
        camera_x, camera_y = utils.update_camera(boat)
        
        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())
