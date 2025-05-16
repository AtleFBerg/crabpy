from collections import defaultdict

import pygame
from animations import gui_elements
from animations.underwater_animation import UnderwaterAnimation
from animations.water_animation import WaterAnimation
import config
from services import food_service
import utils
from entities.food import *
from entities.crab import Crab
from views.base_view import BaseView


class SeaView(BaseView):
    
    def __init__(self):
        super().__init__()
        self.underwater = False
        self.water_animation = WaterAnimation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.underwater_animation = UnderwaterAnimation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.all_food: list[Food] = []
        self.selected_bait = None
        utils.world_food_respawn(self.all_food)
        self.all_crabs: list[Crab] = [Crab() for _ in range(config.INITIAL_CRAB_COUNT)]
        self.toggle_button_rect = pygame.Rect(config.SCREEN_WIDTH / 2, 20, 150, 40)

    def update(self, screen, camera_x, camera_y, timer, boat, crab_inventory, font):
        if self.underwater:
            self.underwater_animation.draw(screen, camera_x, camera_y)
        else:
            self.water_animation.update()
            self.water_animation.draw(screen, camera_x, camera_y)
        self.update_crabs(screen, self.all_crabs, self.all_food, camera_x, camera_y)
        self.draw_boat(boat, screen, camera_x, camera_y)
        self.draw_pots(boat, screen, camera_x, camera_y, self.underwater, self.all_crabs, self.all_food)
        self.draw_food(screen, self.all_food, camera_x, camera_y, timer)
        gui_elements.draw_average_crab_food_preferences(screen, self.all_crabs, font)
        gui_elements.draw_toggle_button(screen, self.toggle_button_rect, font, "Above" if not self.underwater else "Underwater")
        gui_elements.draw_current_crab_count(screen, crab_inventory, font)
        gui_elements.draw_selected_bait(screen, self.selected_bait, font)
        gui_elements.draw_crab_count(self.all_crabs, screen)    

    def draw(self, screen, camera_x, camera_y):
        # Additional drawing logic if needed
        pass

    def update_crabs(self, screen, all_crabs, all_food, camera_x, camera_y):
        food_to_remove = []
        for crab in all_crabs:
            crab.update()
            if crab.energy <= 0.0:
                all_crabs.remove(crab)
                continue
            if self.underwater:
                screen.blit(crab.sprite, (crab.x - camera_x, crab.y - camera_y))
            crab.make_decision(all_crabs=all_crabs, potential_food=all_food)
            if crab.food_to_remove:
                food_to_remove.append(crab.food_to_remove)
                crab.food_to_remove = None
        if food_to_remove:
            food_service.remove_food(food_to_remove, all_food)

    def draw_food(self, screen, all_food, camera_x, camera_y, timer):
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
            if self.underwater:
                screen.blit(food.sprite, (food.x - camera_x, food.y - camera_y))
    
    def draw_boat(self, boat, screen, camera_x, camera_y):
        boat.update()
        if not self.underwater:
            boat.draw(screen, camera_x, camera_y)
    
    def draw_pots(self, boat, screen, camera_x, camera_y, underwater, all_crabs, all_food):
        if boat.pots:
            for crab_pot in boat.pots:
                crab_pot.draw(screen, camera_x, camera_y, underwater)
                crab_pot.check_for_crabs(all_crabs, all_food)

    def handle_events(self, events, boat, crab_inventory):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.selected_bait:
                        continue
                    MARGIN = 100
                    pot_under_boat = None
                    for pot in boat.pots:
                        if abs(pot.x - boat.x) < MARGIN // 2 and abs(pot.y - boat.base_y) < MARGIN // 2:
                            pot_under_boat = pot
                            break
                    if pot_under_boat:
                        boat.raise_pot(pot_under_boat, self.all_food, crab_inventory)
                    else:
                        boat.drop_pot(self.selected_bait, self.all_food)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.toggle_button_rect.collidepoint(event.pos):
                    self.underwater = not self.underwater

    def handle_keys(self, keys, boat):
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
        if keys[pygame.K_1]: self.selected_bait = Seaweed(is_bait=True)
        if keys[pygame.K_2]: self.selected_bait = Shrimp(is_bait=True)
        if keys[pygame.K_3]: self.selected_bait = Clam(is_bait=True)
        if keys[pygame.K_4]: self.selected_bait = FishRemains(is_bait=True)
        if keys[pygame.K_5]: self.selected_bait = Plankton(is_bait=True)
        if keys[pygame.K_6]: self.selected_bait = Starfish(is_bait=True)
