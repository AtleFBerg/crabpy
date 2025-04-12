import time
import pygame

from .crab import Crab

class CrabPot:
    def __init__(self, x=500, y=400, bait=None, width=100, height=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bait = bait  # Could be a class like Seaweeds, or just the name
        self.lowered = False
        self.caught_crabs = []
        self.number_of_crabs_allowed = 25

    def area(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def lower(self):
        print("Pot lowered!")
        self.lowered = True

    def raise_pot(self):
        self.lowered = False
        print("Crab pot raised. Caught crabs:", self.caught_crabs.__len__())
        self.caught_crabs = []

    def check_for_crabs(self, crabs: list[Crab]):
        if not self.lowered:
            return

        for crab in crabs[:]:  # Work on a copy to allow safe removal
            if self.area().colliderect(pygame.Rect(crab.x, crab.y, crab.width, crab.height)):
                if self.number_of_crabs_allowed == self.caught_crabs.__len__():
                        print("Crab pot is full!")
                        break
                if (
                    crab.target_food 
                    and isinstance(crab.target_food, self.bait)
                    and crab.preferred_foods.get(self.bait, 0) > 0.2):
                    print(f"Caught a crab chasing {self.bait.__name__}: {crab}")
                    self.caught_crabs.append(crab)
                    crabs.remove(crab)
                    
