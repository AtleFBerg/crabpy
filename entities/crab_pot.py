import time
import pygame

from entities.food import Food
from animations.bouy_glow_effect import bouy_glow_effect

from .crab import Crab

class CrabPot:
    def __init__(self, x=500, y=400, width=50, height=50, bait=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bait = bait  # Could be a class like Seaweeds, or just the name
        self.bait_sprite = self.bait.sprite if bait else None
        self.lowered = False
        self.caught_crabs = []
        self.is_full = False
        self.number_of_crabs_allowed = 25
        self.buoy_sprite = pygame.image.load("assets/sprites/buoy.png").convert_alpha()
        self.buoy_sprite = pygame.transform.scale(self.buoy_sprite, (self.width, self.height))
        self.underwater_pot_sprite = pygame.image.load("assets/sprites/crab_pot.png").convert_alpha()
        self.underwater_pot_sprite = pygame.transform.scale(self.underwater_pot_sprite, (self.width, self.height))
        self.time_to_live = 300 * 30
        self.blink_alpha = 255         # current alpha (brightness)
        self.blink_direction = -5      # decrease alpha (fade out)

    def set_bait(self, bait_instance):
        self.bait = bait_instance
        if self.bait:
            self.bait_sprite = pygame.image.load(self.bait.sprite()).convert_alpha()
            self.bait_sprite = pygame.transform.scale(self.bait_sprite, (25, 25))

    def area(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def lower(self):
        print("Pot lowered!")
        self.lowered = True

    def raise_pot(self, all_food: list[Food]):
        if self.bait in all_food:
            all_food.remove(self.bait)
        self.lowered = False
        print("Crab pot raised. Caught crabs:", self.caught_crabs.__len__())
        self.caught_crabs = []

    def check_for_crabs(self, crabs: list[Crab], all_food: list[Food]):
        if self.is_full:
            self.blink_alpha, self.blink_direction = bouy_glow_effect(self.buoy_sprite, self.x, self.y, self.width, self.height, self.blink_alpha, self.blink_direction)
            self.buoy_sprite.set_alpha(self.blink_alpha)
            return
        if self.time_to_live <= 0:
            self.blink_alpha, self.blink_direction = bouy_glow_effect(self.buoy_sprite, self.x, self.y, self.width, self.height, self.blink_alpha, self.blink_direction)
            self.buoy_sprite.set_alpha(self.blink_alpha)
            return
        self.time_to_live -= 1
        if self.time_to_live <= 0:
            print("Crab pot ran out of bait!")
            if self.bait in all_food:
                all_food.remove(self.bait)
            self.bait = None
            self.bait_sprite = None
            return
        for crab in crabs[:]:  # Work on a copy to allow safe removal
            if self.area().colliderect(pygame.Rect(crab.x, crab.y, crab.width, crab.height)):
                if self.number_of_crabs_allowed == self.caught_crabs.__len__():
                        print("Crab pot is full!")
                        self.is_full = True
                        if self.bait in all_food:
                            all_food.remove(self.bait)
                        self.bait = None
                        self.bait_sprite = None
                        break
                if (
                    crab.target_food 
                    and isinstance(crab.target_food, type(self.bait))
                    and crab.preferred_foods.get(type(self.bait), 0) > 0.2):
                    print(f"Caught a crab chasing {type(self.bait).__name__}: {crab}")
                    self.caught_crabs.append(crab)
                    crabs.remove(crab)

                
        
    def draw(self, screen, camera_x, camera_y, underwater: bool):
        if underwater:
            screen.blit(self.underwater_pot_sprite, (self.x - camera_x, self.y - camera_y))
        else:
            screen.blit(self.buoy_sprite, (self.x - camera_x, self.y - camera_y))
        
                    
