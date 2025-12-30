import asyncio
import pygame
import config
import simulation
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

simulation.initialize_simulation()

# Initialize views
views = {
    "start_menu": StartMenuView(),
    "sea": SeaView(simulation.boat),
    "town": TownView(),
    "crab_vendor": CrabVendorView(),
    "shipyard": ShipyardView(simulation.boat),
    "pub": PubView(simulation.boat),
    "burlesque": BurlesqueView(),
    "highscores": HighscoresView(),
}
current_view = views["start_menu"]
current_view_key = "start_menu"

score_service.register_reset_callback(simulation.reset_global_game_state)
score_service.register_reset_callback(simulation.boat.reset_for_new_game)

async def main():
    global current_view, current_view_key, running

    while simulation.running:
        clock.tick(30)
        simulation.update_global_simulation()
        current_view.update(screen, simulation.camera_x, simulation.camera_y, simulation.inventory, font)

        events = pygame.event.get()
        new_view_key = current_view.handle_events(events, simulation.inventory)
        if new_view_key:
            if new_view_key == "highscore_entry":
                current_view = HighscoreEntryView(score_service.get_final_score())
                current_view_key = "highscore_entry"
            elif new_view_key == "game_over":
                current_view = GameOverView()
                current_view_key = "game_over"
            elif new_view_key in views:
                current_view = views[new_view_key]
                current_view_key = new_view_key
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
        
        simulation.camera_x, simulation.camera_y = current_view.update_camera()
        
        simulation.draw_status_effects(screen, current_view_key)
        
        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())