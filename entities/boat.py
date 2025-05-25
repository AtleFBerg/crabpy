from typing import List
import pygame
import math
import time
from .crab_pot import CrabPot  # Adjust import as needed

class Boat:
    def __init__(self, x, y, max_pots=3):
        self.x = x
        self.y = y
        self.base_y = y  # for wobble
        self.width = 48
        self.height = 32
        self.speed = 2.0
        self.sprite = pygame.image.load("assets/sprites/boat.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (144, 96))
        self.facing_left = True
        self.pots: List[CrabPot] = []
        self.max_pots = max_pots
        self.wobble_timer = 0
        self.wobble_offset = 0

    def move(self, keys):
        if keys[pygame.K_a or pygame.K_RIGHT]: self.x -= self.speed
        if keys[pygame.K_d or pygame.K_LEFT]: self.x += self.speed
        if keys[pygame.K_w or pygame.K_UP]: self.base_y -= self.speed
        if keys[pygame.K_s or pygame.K_DOWN]: self.base_y += self.speed

    def drop_pot(self, selected_bait, all_food):
        if len(self.pots) < self.max_pots:
            new_bait = selected_bait.__class__(is_bait=True)
            new_bait.x = self.x + self.width // 2
            new_bait.y = self.base_y + self.height
            new_pot = CrabPot(self.x + self.width // 2, self.base_y + self.height, bait=new_bait)
            new_pot.lower()
            self.pots.append(new_pot)
            all_food.append(new_bait)

    def raise_pot(self, pot: CrabPot, all_food, crab_inventory):
        crab_inventory["crab_count"] += len(pot.caught_crabs)
        pot.raise_pot(all_food)
        self.pots.remove(pot)

    def update(self):
        # Wobble up/down using sine wave
        self.wobble_timer += 0.05
        self.wobble_offset = math.sin(pygame.time.get_ticks() * 0.005) * 2

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.sprite, (self.x - camera_x, self.base_y - camera_y + self.wobble_offset, ))

