import random
import time
import pygame
import config

FOOD_IMAGES = {}

def load_food_images():
    food_types = [Seaweed, Clam, FishRemains, Plankton, Starfish, Shrimp]
    for cls in food_types:
        name = cls.__name__.lower()
        image = pygame.image.load(f"assets/sprites/{name}.png").convert_alpha()
        FOOD_IMAGES[name] = pygame.transform.scale(image, (25, 25))
        
class Food():
    def __init__(self, energy, width=25, height=25, time_to_multiply=None, is_bait=False):
        self.energy = energy
        self.width = width
        self.height = height
        self.is_bait = is_bait 
        self.x = random.randint(0, config.WORLD_WIDTH - self.width)
        self.y = random.randint(0, config.WORLD_HEIGHT - self.height)
        self.time_to_multiply = time_to_multiply
        self.sprite = FOOD_IMAGES[self.__class__.__name__.lower()]

    def eat(self, crab):
        crab.energy += self.energy
        crab.adjust_food_preferences(type(self))
        self.consumed = True
        self.last_eaten_time = time.time()

    def update(self, food_counts):
        if self.time_to_multiply is not None:
            self.time_to_multiply -= 1
            if self.time_to_multiply <= 0:
                self.time_to_multiply = random.randint(300, 1200)
                if food_counts.get(type(self), 0) > 50:
                    return 
                return self.multiply()
            
    def multiply(self):
        new_food = self.__class__()
        new_food.x = random.randint(0, config.WORLD_WIDTH - new_food.width)
        new_food.y = random.randint(0, config.SCREEN_HEIGHT - new_food.height)
        return new_food
   
class Seaweed(Food):
    def __init__(self, is_bait=False):
        super().__init__(energy=5, time_to_multiply=300, is_bait=is_bait)

class Clam(Food):
    def __init__(self, is_bait=False):
        super().__init__(energy=15, time_to_multiply=800, is_bait=is_bait)

class FishRemains(Food):
    def __init__(self, is_bait=False):
        super().__init__(energy=25, time_to_multiply=800, is_bait=is_bait)

class Plankton(Food):
    def __init__(self, is_bait=False):
        super().__init__(energy=3, time_to_multiply=300, is_bait=is_bait)

class Starfish(Food):
    def __init__(self, is_bait=False):
        super().__init__(energy=15, time_to_multiply=500, is_bait=is_bait)

class Shrimp(Food):
    def __init__(self, is_bait=False):
        super().__init__(energy=11, time_to_multiply=600, is_bait=is_bait)
