from collections import defaultdict
import pygame
import random
from animations import gui_elements
from animations.underwater_animation import UnderwaterAnimation
from animations.water_animation import WaterAnimation
import config
import simulation
from entities.boat import Boat
from services.score_service import score_service
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
        self.selected_bait = None
        self.cheat_code = ""
        self.cheat_active = False
        self.toggle_button_rect = pygame.Rect(config.SCREEN_WIDTH / 2, 20, 150, 40)
        self.periscope_level = 0
        self.pip_base_width, self.pip_base_height = 125, 75
        self.pip_width, self.pip_height = self.pip_base_width, self.pip_base_height
        self.pip_surface = pygame.Surface((self.pip_width, self.pip_height), pygame.SRCALPHA).convert_alpha()
        self.periscope_img_orig = pygame.image.load("assets/sprites/periscope.png").convert_alpha()
        self.periscope_img = pygame.transform.scale(self.periscope_img_orig, (self.pip_width + 40, self.pip_height + 40))
        self.drunk_remap_timer = 0
        self.drunk_remap_duration = 90  
        self.current_control_map = {'left': 'left', 'right': 'right', 'up': 'up', 'down': 'down'}
        score_service.register_reset_callback(self.reset_game_world)

    def update(self, screen, camera_x, camera_y, inventory, font):
        score_service.update()
    
        if self.boat.is_drunk:
            self.drunk_remap_timer += 1
            if self.drunk_remap_timer >= self.drunk_remap_duration:
                self.randomize_drunk_controls()
                self.drunk_remap_timer = 0
        else:
            self.current_control_map = {'left': 'left', 'right': 'right', 'up': 'up', 'down': 'down'}
            self.drunk_remap_timer = 0
        
        if self.underwater:
            self.underwater_animation.draw(screen, camera_x, camera_y)
        else:
            self.water_animation.update()
            self.water_animation.draw_ocean(screen, camera_x, camera_y)
        if inventory["reverse_periscope"]:
            self._update_periscope_size(inventory["reverse_periscope"])
            self.draw_pip(screen)
        self.render_crabs(screen, camera_x, camera_y, simulation.all_crabs)
        self.draw_boat(screen, camera_x, camera_y)
        self.draw_pots(screen, camera_x, camera_y)
        self.render_food(screen, camera_x, camera_y, simulation.all_food)
    
        gui_elements.draw_average_crab_food_preferences(screen, simulation.all_crabs, font)
        if self.cheat_active:
            gui_elements.draw_toggle_button(screen, self.toggle_button_rect, font, "Above" if not self.underwater else "Underwater")
        gui_elements.draw_inventory(screen, inventory, font)
        gui_elements.draw_selected_bait(screen, self.selected_bait, font)
        gui_elements.draw_crab_count(simulation.all_crabs, screen)
        gui_elements.draw_to_town_arrow(screen, camera_x, camera_y)
        
        # Draw the timer on screen
        from services.game_timer_service import game_timer
        game_timer.draw_timer(screen, config.SCREEN_WIDTH/ 2 - 100, 10)  # Position below other UI elements
        
        # Draw current score
        score_text = font.render(f"Score: {score_service.total_score}", True, (255, 255, 255))
        screen.blit(score_text, (config.SCREEN_WIDTH/ 2 - 100, 60))
    
    def render_crabs(self, screen, camera_x, camera_y, all_crabs):
        for crab in all_crabs:
            if self.underwater:
                screen.blit(crab.sprite, (crab.x - camera_x, crab.y - camera_y))

    def render_food(self, screen, camera_x, camera_y, all_food):
        for food in all_food:
            if self.underwater:
                screen.blit(food.sprite, (food.x - camera_x, food.y - camera_y))

    def update_camera(self):
        return utils.update_camera(self.boat)
    
    def randomize_drunk_controls(self):
        directions = ['left', 'right', 'up', 'down']
        shuffled = directions.copy()
        random.shuffle(shuffled)
        self.current_control_map = {
            'left': shuffled[0],
            'right': shuffled[1],
            'up': shuffled[2],
            'down': shuffled[3]
        }

    def draw(self, screen, camera_x, camera_y):
        pass


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
        if self.boat.pots:
            for pot in self.boat.pots:
                if abs(pot.x - self.boat.x) < MARGIN // 2 and abs(pot.y - self.boat.base_y) < MARGIN // 2:
                    pot_under_boat = pot
                    break
        if self.boat.pots:
            for crab_pot in self.boat.pots:
                highlight = (crab_pot is pot_under_boat)
                crab_pot.draw(screen, camera_x, camera_y, self.underwater, highlight=highlight)
                crab_pot.check_for_crabs(simulation.all_crabs, simulation.all_food)
    
    def handle_events(self, events, crab_inventory):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                # Cheat code detection
                if event.unicode.lower() in 'crab':
                    self.cheat_code += event.unicode.lower()
                    if len(self.cheat_code) > 4:
                        self.cheat_code = self.cheat_code[-4:] 
                    if self.cheat_code == "crab":
                        self.cheat_active = not self.cheat_active  
                        if self.cheat_active:
                            score_service.mark_cheats_used()  # Mark cheats as used
                        self.cheat_code = "" 
                else:
                    self.cheat_code = ""  
                
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
                        self.boat.raise_pot(pot_under_boat, simulation.all_food, crab_inventory)  # Use global food
                    else:
                        self.boat.drop_pot(self.selected_bait, simulation.all_food)  # Use global food
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.cheat_active and self.toggle_button_rect.collidepoint(event.pos):
                    self.underwater = not self.underwater
        if self.boat.x <= 0:
            self.boat.x = 10
            return "town"
        if score_service.is_game_over():
            return "game_over" 
        return None

    def handle_keys(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            action = self.current_control_map['left']
            if action == 'left':
                self.boat.x -= self.boat.speed
            elif action == 'right':
                self.boat.x += self.boat.speed
            elif action == 'up':
                self.boat.base_y -= self.boat.speed
            elif action == 'down':
                self.boat.base_y += self.boat.speed
            
            if not self.boat.facing_left:
                self.boat.facing_left = True
                self.boat.sprite = pygame.transform.flip(self.boat.sprite, True, False)
        
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            action = self.current_control_map['right']
            if action == 'left':
                self.boat.x -= self.boat.speed
            elif action == 'right':
                self.boat.x += self.boat.speed
            elif action == 'up':
                self.boat.base_y -= self.boat.speed
            elif action == 'down':
                self.boat.base_y += self.boat.speed
            
            if self.boat.facing_left:
                self.boat.facing_left = False
                self.boat.sprite = pygame.transform.flip(self.boat.sprite, True, False)
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            action = self.current_control_map['up']
            if action == 'left':
                self.boat.x -= self.boat.speed
            elif action == 'right':
                self.boat.x += self.boat.speed
            elif action == 'up':
                self.boat.base_y -= self.boat.speed
            elif action == 'down':
                self.boat.base_y += self.boat.speed
        
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            action = self.current_control_map['down']
            if action == 'left':
                self.boat.x -= self.boat.speed
            elif action == 'right':
                self.boat.x += self.boat.speed
            elif action == 'up':
                self.boat.base_y -= self.boat.speed
            elif action == 'down':
                self.boat.base_y += self.boat.speed
        
        if keys[pygame.K_1]: self.selected_bait = Seaweed(is_bait=True)
        if keys[pygame.K_2]: self.selected_bait = Shrimp(is_bait=True)
        if keys[pygame.K_3]: self.selected_bait = Clam(is_bait=True)
        if keys[pygame.K_4]: self.selected_bait = FishRemains(is_bait=True)
        if keys[pygame.K_5]: self.selected_bait = Plankton(is_bait=True)
        if keys[pygame.K_6]: self.selected_bait = Starfish(is_bait=True)

    def _update_periscope_size(self, level):
        """Resize PIP and frame based on periscope upgrade level (1-3)."""
        if level == self.periscope_level:
            return
        self.periscope_level = level
        scale = 1.0 + (level - 1) * 0.5  # level 1: 1.0x, level 2: 1.5x, level 3: 2.0x
        self.pip_width = int(self.pip_base_width * scale)
        self.pip_height = int(self.pip_base_height * scale)
        self.pip_surface = pygame.Surface((self.pip_width, self.pip_height), pygame.SRCALPHA).convert_alpha()
        v_padding = 40 + (level - 1) * 15  # extra vertical stretch per upgrade
        self.frame_top_extra = (level - 1) * 10  # extra top extension per upgrade
        frame_h = self.pip_height + v_padding + self.frame_top_extra
        self.periscope_img = pygame.transform.scale(self.periscope_img_orig, (self.pip_width + 40, frame_h))

    def draw_pip(self, screen):
        self.pip_surface.fill((0, 0, 0, 0))
        boat_center_x = self.boat.x + self.boat.sprite.get_width() // 2
        boat_center_y = self.boat.base_y + self.boat.sprite.get_height() // 2
        pip_camera_x = boat_center_x - self.pip_width // 2
        pip_camera_y = boat_center_y - self.pip_height // 2
        self.underwater_animation.draw(self.pip_surface, pip_camera_x, pip_camera_y)
        for food in simulation.all_food:
            pip_x = food.x - pip_camera_x
            pip_y = food.y - pip_camera_y
            self.pip_surface.blit(food.sprite, (pip_x, pip_y))
        for crab in simulation.all_crabs:
            pip_x = crab.x - pip_camera_x
            pip_y = crab.y - pip_camera_y
            self.pip_surface.blit(crab.sprite, (pip_x, pip_y))
        if self.boat.pots:
            for crab_pot in self.boat.pots:
                pip_x = crab_pot.x - pip_camera_x
                pip_y = crab_pot.y - pip_camera_y
                self.pip_surface.blit(crab_pot.underwater_pot_sprite, (pip_x, pip_y))
        mask = pygame.Surface((self.pip_width, self.pip_height), pygame.SRCALPHA)
        pygame.draw.ellipse(mask, (255, 255, 255, 255), (0, 0, self.pip_width, self.pip_height))
        round_pip = self.pip_surface.copy()
        round_pip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pip_x = screen.get_width() - self.pip_width - 20
        pip_y = screen.get_height() - self.pip_height - 20
        screen.blit(round_pip, (screen.get_width() - self.pip_width - 20, screen.get_height() - self.pip_height - 20))
        top_extra = getattr(self, 'frame_top_extra', 0)
        screen.blit(self.periscope_img, (pip_x - 20 , pip_y - 20 - top_extra))

    def reset_game_world(self):
        print("🌊 Resetting sea world...")
        
        # Reset boat
        self.boat.x = config.SCREEN_WIDTH // 2
        self.boat.y = config.SCREEN_HEIGHT // 2
        self.boat.base_y = self.boat.y
        self.boat.is_drunk = False
        self.boat.drunk_timer = 0
        self.boat.pots = []  # Clear all pots
        
        global camera_x, camera_y
        camera_x = 0
        camera_y = 0
        
        
        # Reset food
        self.all_food.clear()
        utils.world_food_respawn(self.all_food)
        
        # Reset other sea view specific stuff
        self.selected_bait = None
        self.cheat_active = False
        self.underwater = False
        self.periscope_level = 0
        self.pip_width, self.pip_height = self.pip_base_width, self.pip_base_height
        self.pip_surface = pygame.Surface((self.pip_width, self.pip_height), pygame.SRCALPHA).convert_alpha()
        self.periscope_img = pygame.transform.scale(self.periscope_img_orig, (self.pip_width + 40, self.pip_height + 40))
        
        # Reset drunk controls
        self.current_control_map = {'left': 'left', 'right': 'right', 'up': 'up', 'down': 'down'}
        self.drunk_remap_timer = 0
        
        print("✅ Sea world reset complete!")