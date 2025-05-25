from collections import defaultdict
import pygame
from animations import gui_elements
from animations.underwater_animation import UnderwaterAnimation
from animations.water_animation import WaterAnimation
import config
from entities.boat import Boat
import utils
from entities.food import *
from entities.crab import Crab
from views.base_view import BaseView


class SeaView(BaseView):
    
    def __init__(self, boat: Boat):
        super().__init__()
        self.underwater = False
        self.boat = boat
        self.water_animation = WaterAnimation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.underwater_animation = UnderwaterAnimation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.all_food: list[Food] = []
        self.selected_bait = None
        utils.world_food_respawn(self.all_food)
        self.all_crabs: list[Crab] = [Crab() for _ in range(config.INITIAL_CRAB_COUNT)]
        self.toggle_button_rect = pygame.Rect(config.SCREEN_WIDTH / 2, 20, 150, 40)
        self.world_food_respawn_timer = 0
        # Create the PiP surface once and reuse it
        self.pip_width, self.pip_height = 300, 200
        self.pip_surface = pygame.Surface((self.pip_width, self.pip_height), pygame.SRCALPHA).convert_alpha()

    def update(self, screen, camera_x, camera_y, inventory, font):
        if self.underwater:
            self.underwater_animation.draw(screen, camera_x, camera_y)
        else:
            self.water_animation.update()
            self.water_animation.draw(screen, camera_x, camera_y)
            if inventory["reverse_periscope"]:
                self.draw_pip(screen)
        self.update_crabs(screen, camera_x, camera_y)
        self.draw_boat(screen, camera_x, camera_y)
        self.draw_pots(screen, camera_x, camera_y)
        self.draw_food(screen, camera_x, camera_y)
        gui_elements.draw_average_crab_food_preferences(screen, self.all_crabs, font)
        gui_elements.draw_toggle_button(screen, self.toggle_button_rect, font, "Above" if not self.underwater else "Underwater")
        gui_elements.draw_current_crab_count(screen, inventory, font)
        gui_elements.draw_selected_bait(screen, self.selected_bait, font)
        gui_elements.draw_crab_count(self.all_crabs, screen)
        gui_elements.draw_to_town_arrow(screen, camera_x, camera_y)

    
    def update_camera(self):
        return utils.update_camera(self.boat)

    def draw(self, screen, camera_x, camera_y):
        # Additional drawing logic if needed
        pass

    def update_crabs(self, screen, camera_x, camera_y):
        food_to_remove = []
        for crab in self.all_crabs:
            crab.update()
            if crab.energy <= 0.0:
                self.all_crabs.remove(crab)
                continue
            if self.underwater:
                screen.blit(crab.sprite, (crab.x - camera_x, crab.y - camera_y))
            crab.make_decision(all_crabs=self.all_crabs, potential_food=self.all_food)
            if crab.food_to_remove:
                food_to_remove.append(crab.food_to_remove)
                crab.food_to_remove = None
        if food_to_remove:
            Food.remove_food(food_to_remove, self.all_food)

    def draw_food(self, screen, camera_x, camera_y):
        food_counts = defaultdict(int)
        for food in self.all_food:
            food_counts[type(food)] += 1
        self.world_food_respawn_timer += 1
        if self.world_food_respawn_timer % 2000 == 0:
            utils.world_food_respawn(self.all_food)
            self.world_food_respawn_timer = 0
        
        for food in self.all_food:
            new_food = food.update(food_counts)
            if new_food:
                self.all_food.append(new_food)
            if self.underwater:
                screen.blit(food.sprite, (food.x - camera_x, food.y - camera_y))
    
    def draw_boat(self, screen, camera_x, camera_y):
        self.boat.update()
        if not self.underwater:
            self.boat.draw(screen, camera_x, camera_y)
    
    def draw_pots(self, screen, camera_x, camera_y):
        pot_under_boat = None
        MARGIN = 100
        # Find pot under boat
        if self.boat.pots:
            for pot in self.boat.pots:
                if abs(pot.x - self.boat.x) < MARGIN // 2 and abs(pot.y - self.boat.base_y) < MARGIN // 2:
                    pot_under_boat = pot
                    break
        # Draw pots, highlighting the one under the boat
        if self.boat.pots:
            for crab_pot in self.boat.pots:
                highlight = (crab_pot is pot_under_boat)
                crab_pot.draw(screen, camera_x, camera_y, self.underwater, highlight=highlight)
                crab_pot.check_for_crabs(self.all_crabs, self.all_food)

    def handle_events(self, events, crab_inventory):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.selected_bait:
                        continue
                    MARGIN = 100
                    pot_under_boat = None
                    for pot in self.boat.pots:
                        if abs(pot.x - self.boat.x) < MARGIN // 2 and abs(pot.y - self.boat.base_y) < MARGIN // 2:
                            pot_under_boat = pot
                            break
                    if pot_under_boat:
                        self.boat.raise_pot(pot_under_boat, self.all_food, crab_inventory)
                    else:
                        self.boat.drop_pot(self.selected_bait, self.all_food)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.toggle_button_rect.collidepoint(event.pos):
                    self.underwater = not self.underwater
        # Check if boat is at the left edge
        if self.boat.x <= 0:
            self.boat.x = 10
            return "town"
        return None

    def handle_keys(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.boat.x -= 2
            if not self.boat.facing_left:
                self.boat.facing_left = True
                self.boat.sprite = pygame.transform.flip(self.boat.sprite, True, False)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.boat.x += 2
            if self.boat.facing_left:
                self.boat.facing_left = False
                self.boat.sprite = pygame.transform.flip(self.boat.sprite, True, False)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.boat.base_y -= 2
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.boat.base_y += 2
        if keys[pygame.K_1]: self.selected_bait = Seaweed(is_bait=True)
        if keys[pygame.K_2]: self.selected_bait = Shrimp(is_bait=True)
        if keys[pygame.K_3]: self.selected_bait = Clam(is_bait=True)
        if keys[pygame.K_4]: self.selected_bait = FishRemains(is_bait=True)
        if keys[pygame.K_5]: self.selected_bait = Plankton(is_bait=True)
        if keys[pygame.K_6]: self.selected_bait = Starfish(is_bait=True)

    def draw_pip(self, screen):
        # Clear the PiP surface each frame
        self.pip_surface.fill((0, 0, 0, 0))
        pip_camera_x = self.boat.x - self.pip_width // 2
        pip_camera_y = self.boat.base_y - self.pip_height // 2
        self.underwater_animation.draw(self.pip_surface, pip_camera_x, pip_camera_y)
        for food in self.all_food:
            pip_x = food.x - pip_camera_x
            pip_y = food.y - pip_camera_y
            self.pip_surface.blit(food.sprite, (pip_x, pip_y))
        for crab in self.all_crabs:
            pip_x = crab.x - pip_camera_x
            pip_y = crab.y - pip_camera_y
            self.pip_surface.blit(crab.sprite, (pip_x, pip_y))
        if self.boat.pots:
            for crab_pot in self.boat.pots:
                pip_x = crab_pot.x - pip_camera_x
                pip_y = crab_pot.y - pip_camera_y
                self.pip_surface.blit(crab_pot.underwater_pot_sprite, (pip_x, pip_y))
        screen.blit(self.pip_surface, (screen.get_width() - self.pip_width - 20, screen.get_height() - self.pip_height - 20))
