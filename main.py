import asyncio
import pygame
from entities.boat import Boat
from entities.food import *
import config
from services.score_service import score_service
from views.game_over_view import GameOverView
from views.highscore_entry_view import HighscoreEntryView
from views.highscores_view import HighscoresView
from views.sea import SeaView
from views.town import TownView
from views.shipyard import ShipyardView
from views.crab_vendor import CrabVendorView
from views.pub import PubView
from views.burlesque import BurlesqueView
from views.start_menu import StartMenuView
from services.game_timer_service import game_timer

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
boat = Boat(100, 100)  
inventory = {"crab_count": 0, "money": 0, "reverse_periscope": False}
running = True

# Initialize views
views = {
    "start_menu": StartMenuView(),
    "sea": SeaView(boat),
    "town": TownView(),
    "crab_vendor": CrabVendorView(),
    "shipyard": ShipyardView(boat),
    "pub": PubView(boat),
    "burlesque": BurlesqueView(),
    "highscores": HighscoresView(),
}
current_view = views["start_menu"]

def reset_global_game_state():
    global camera_x, camera_y, inventory
    
    camera_x = 0
    camera_y = 0
    
    beer_count = inventory.get("beer_count", 0)  
    inventory.clear()
    inventory.update({
        "money": 0,
        "crab_count": 0,
        "beer_count": beer_count,  
        "reverse_periscope": False
    })

score_service.register_reset_callback(reset_global_game_state)
score_service.register_reset_callback(boat.reset_for_new_game)

async def main():
    global camera_x, camera_y, inventory, running, current_view

    while running:
        clock.tick(30)

        current_view.update(screen, camera_x, camera_y, inventory, font)

        events = pygame.event.get()
        new_view_key = current_view.handle_events(events, inventory)
        if new_view_key:
            if new_view_key == "highscore_entry":
                current_view = HighscoreEntryView(score_service.get_final_score())
            elif new_view_key == "game_over":
                current_view = GameOverView()
            elif new_view_key in views:
                current_view = views[new_view_key]
            else:
                print(f"Warning: Unknown view key '{new_view_key}'")
                continue  
                
            if new_view_key == "sea":
                i = 0
                if not game_timer.is_running and not game_timer.is_finished:
                    game_timer.start()
            elif new_view_key == "crab_vendor":
                current_view.show_greeting()
            elif new_view_key == "pub":
                current_view.show_greeting()
            elif new_view_key == "highscores":
                current_view.refresh_scores()

        if hasattr(current_view, 'handle_keys'):
            keys = pygame.key.get_pressed()
            current_view.handle_keys(keys)
        
        camera_x, camera_y = current_view.update_camera()
        
        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())