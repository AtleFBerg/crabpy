from collections import defaultdict
from animations.underwater_animation import UnderwaterAnimation
from animations.water_animation import WaterAnimation
import config
from services import food_service
import utils
from views.base_view import BaseView


class SeaView(BaseView):
    def __init__(self):
        super().__init__()
        self.underwater = False
        self.water_animation = WaterAnimation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        self.underwater_animation = UnderwaterAnimation(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    
    def update(self, screen, camera_x, camera_y, all_crabs, all_food, timer, boat):
        if self.underwater:
            self.underwater_animation.draw(screen, camera_x, camera_y)
            self.draw_crabs(screen, all_crabs, all_food, camera_x, camera_y)
            self.draw_food(screen, all_food, camera_x, camera_y, timer)
            self.draw_pots(boat, screen, camera_x, camera_y, self.underwater, all_crabs, all_food)
        else:
            self.water_animation.update()
            self.water_animation.draw(screen, camera_x, camera_y)
            self.draw_boat(boat, screen, camera_x, camera_y)
            self.draw_pots(boat, screen, camera_x, camera_y, self.underwater, all_crabs, all_food)
            

    def draw(self, screen, camera_x, camera_y):
        # Additional drawing logic if needed
        pass

    def draw_crabs(self, screen, all_crabs, all_food, camera_x, camera_y):
        food_to_remove = []
        for crab in all_crabs:
            crab.update()
            if crab.energy <= 0.0:
                all_crabs.remove(crab)
                continue
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
            screen.blit(food.sprite, (food.x - camera_x, food.y - camera_y))
    
    def draw_boat(self, boat, screen, camera_x, camera_y):
        boat.update()
        boat.draw(screen, camera_x, camera_y)
    
    def draw_pots(self, boat, screen, camera_x, camera_y, underwater, all_crabs, all_food):
        if boat.pots:
            for crab_pot in boat.pots:
                crab_pot.draw(screen, camera_x, camera_y, underwater)
                crab_pot.check_for_crabs(all_crabs, all_food)
