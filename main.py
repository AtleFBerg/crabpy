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
timer = 0
boat = Boat(100, 100)

crab_inventory = {"count": 0}
running = True

# Initialize views
views = {
    "sea": SeaView(),
}

current_view = views["sea"]

# Toggle button for view mode

async def main():
    global camera_x, camera_y, timer, crab_inventory, running, current_view

    while running:
        clock.tick(30)

        # Update and draw the current view
        current_view.update(screen, camera_x, camera_y, timer, boat, crab_inventory, font)

        # Handle events
        events = pygame.event.get()
        current_view.handle_events(events, boat, crab_inventory)

        # Movement and input
        keys = pygame.key.get_pressed()
        current_view.handle_keys(keys, boat)
        
        camera_x, camera_y = utils.update_camera(boat)
        
        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())
