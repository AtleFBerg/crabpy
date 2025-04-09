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

    def area(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def lower(self):
        self.lowered = True

    def raise_pot(self):
        self.lowered = False
        self.caught_crabs = []
        print("Crab pot raised. Caught crabs:", self.caught_crabs)

    def check_for_crabs(self, crabs: list[Crab]):
        if not self.lowered:
            return

        for crab in crabs[:]:  # Work on a copy to allow safe removal
            if self.area().colliderect(pygame.Rect(crab.x, crab.y, crab.width, crab.height)):
                if crab.preferred_foods.get(self.bait, 0) >= 1:  # Crabs that like the bait
                    print(f"Caught a crab: {crab}")
                    self.caught_crabs.append(crab)
                    crabs.remove(crab)
