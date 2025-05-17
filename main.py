import asyncio
import pygame
from entities.boat import Boat
from entities.food import *
import utils
import config
from views.sea import SeaView
from views.start_menu import StartMenuView

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

crab_inventory = {"count": 0}
running = True

# Initialize views
views = {
    "start_menu": StartMenuView(),
    "sea": SeaView(),
}
current_view = views["start_menu"]

# Toggle button for view mode

async def main():
    global camera_x, camera_y, timer, crab_inventory, running, current_view

    while running:
        clock.tick(30)

        # Update and draw the current view
        current_view.update(screen, camera_x, camera_y, timer, crab_inventory, font)

        # Handle events
        events = pygame.event.get()
        new_view_key = current_view.handle_events(events, crab_inventory)
        if new_view_key and new_view_key in views:
            current_view = views[new_view_key]

        # Movement and input (only if not in menu)
        if hasattr(current_view, 'handle_keys'):
            keys = pygame.key.get_pressed()
            current_view.handle_keys(keys)
        
        camera_x, camera_y = current_view.update_camera()
        
        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())
