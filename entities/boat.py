from typing import List
import pygame
import math
import time
import random
from .crab_pot import CrabPot
import config


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
        self.is_drunk = False
        self.drunk_timer = 0  

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
        from services.score_service import score_service
        from services.game_timer_service import game_timer
        num_crabs = len(pot.caught_crabs)
        if pot.caught_crabs:
            for crab in pot.caught_crabs:
                points = score_service.add_crab_catch(is_drunk=self.is_drunk)
                print(f"Caught crab! +{points} points" + (" (DRUNK BONUS!)" if self.is_drunk else ""))

        crab_inventory["crab_count"] += num_crabs
        if num_crabs > 0:
            game_timer.add_time(num_crabs)
            print(f"Time bonus: +{num_crabs} seconds!")
        pot.raise_pot(all_food)
        self.pots.remove(pot)

    def update(self):
        # Wobble up/down using sine wave
        self.wobble_timer += 0.05
        self.wobble_offset = math.sin(pygame.time.get_ticks() * 0.005) * 2
        
    def drink_beer(self):
        self.drunk_timer += 900
        self.is_drunk = True

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.sprite, (self.x - camera_x, self.base_y - camera_y + self.wobble_offset, ))

    def reset_for_new_game(self):
        """Reset boat state for new game"""
        print("⛵ Resetting boat...")
        
        # Reset position
        self.x = 100
        self.y = 100
        self.base_y = self.y
        
        # Reset drunk state
        self.is_drunk = False
        self.drunk_timer = 0
        
        # Reset upgrades to initial values
        self.speed = 2.0  # Reset to initial speed
        self.max_pots = 3  # Reset to initial max pots
        
        # Clear all pots
        self.pots.clear()
        
        print("✅ Boat reset complete!")

   