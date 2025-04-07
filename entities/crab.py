import random
import time
import pygame
from entities.food import *

class Crab:
   
    def __init__(self, x=None, y=None, energy=None, preferred_foods=None):
        self.x = random.randint(0, 1024 - 50)
        self.y = random.randint(0, 800 - 50)
        self.speed = 1
        self.energy = random.randint(10, 50) if energy is None else energy
        self.looking_for_mate = False
        self.sex = random.choice(['M', 'F'])
        self.rejected_mates = {}  # Track crabs that are not valid mates
        self.preferred_foods = self.get_random_preferred_food(3)
    
    def get_random_preferred_food(self, how_many: int):
        """Get a random preferred food from the list."""
        return random.choices(
            [Seaweeds, Plankton, Starfish, Shrimp, Clam, FishRemains], 
            k=how_many
        )
    
    def look_for_mate(self, all_crabs: list["Crab"], crab_sprites: list):

        # Remove old rejections after some time (e.g., 5 seconds)
        current_time = time.time()
        self.rejected_mates = {mate_id: timestamp for mate_id, timestamp in self.rejected_mates.items() if current_time - timestamp < 5}

        # Find closest mate, but ignore rejected ones
        valid_mates = [mate for mate in all_crabs if mate is not self and id(mate) not in self.rejected_mates]

        
        if not valid_mates:
            print("No valid mates left.")
            return  # No valid mates left

        closest_mate = self.find_closest_mate(valid_mates)

        if closest_mate and self.is_near(closest_mate, threshold=5):
            if self.energy >= 50 and closest_mate.energy >= 50 and closest_mate.sex != self.sex:
                self.energy -= 40
                closest_mate.energy -= 40

                # Inherit food preferences
                inherited_foods = random.choice([self.preferred_foods, closest_mate.preferred_foods])[:2]
                new_food = random.choice([Seaweeds, Plankton, Starfish, Shrimp, Clam, FishRemains])
                baby_preferred_foods = [new_food] + inherited_foods

                baby_crab = Crab(x=self.x, y=self.y, energy=20)
                baby_crab.preferred_foods = baby_preferred_foods
                all_crabs.append(baby_crab)
                crab_sprites.append(pygame.image.load(baby_crab.sprite()))

            else:
                # Use `id(closest_mate)` as the key instead of the object itself
                self.rejected_mates[id(closest_mate)] = current_time

            return  # Stop moving closer after attempting to mate

        self.move_closer(closest_mate)

        
    def move_closer(self, target):
        """Move towards the target without overshooting."""
        if not target:
            return
        
        speed = self.get_speed()

        # Calculate distance
        dx = target.x - self.x
        dy = target.y - self.y

        # If crab is close enough, snap to target position
        if abs(dx) <= speed:
            self.x = target.x
        else:
            self.x += speed if dx > 0 else -speed

        if abs(dy) <= speed:
            self.y = target.y
        else:
            self.y += speed if dy > 0 else -speed

    def find_closest_mate(self, potential_mates):
        closest_mate = None
        closest_distance = float('inf')

        for mate in potential_mates:
            if mate is self:
                continue

            if id(mate) in self.rejected_mates:
                continue

            distance = ((self.x - mate.x) ** 2 + (self.y - mate.y) ** 2) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_mate = mate
        return closest_mate  
    
    def look_for_food(self, potential_food: list[Food]):
        if not potential_food:  # Check if list is empty
            return
        
        # Try to find the highest-ranked preferred food
        preferred_food = self.find_preferred_food(potential_food)
        
        if preferred_food:
            target_food = preferred_food  # Prioritize preferred food
        else:
            target_food = self.find_closest_food(potential_food)  # Default to any food
        
        # Move towards the chosen food
        if target_food.x == self.x and target_food.y == self.y:
            target_food.eat(self)
            self.food_to_remove = target_food  # Mark for removal instead of deleting here
            return
        
        self.move_closer(target_food)

    def find_closest_food(self, potential_food: list[Food]):   
        closest_food = None
        closest_distance = float('inf')
        for food in potential_food:
            distance = ((self.x - food.x) ** 2 + (self.y - food.y) ** 2) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_food = food
        return closest_food
    
    def find_preferred_food(self, potential_food):
        for preferred in self.preferred_foods:  # Check foods in order of preference
            for food in potential_food:
                if isinstance(food, preferred):
                    return food  # Eat the highest-ranked available food
        return None  # No preferred food found
    
    def make_decision(self, all_crabs, crab_sprites, potential_food: list[Food]):
        if self.energy > 50:
            self.looking_for_mate = True
            self.look_for_mate(all_crabs, crab_sprites)
        else:
            self.looking_for_mate = False
            self.look_for_food(potential_food)  # Now prioritizes preferred foods
    
    def get_speed(self):
        """Smooth speed scaling with energy."""
        return max(1, int(self.energy ** 0.5 / 2))  # Speed grows slower but more natural

    def move_left(self):
        if self.x > 0:
            self.x -= self.get_speed()

    def move_right(self):
        if self.x < 1024 - 50:
            self.x += self.get_speed()

    def move_up(self):
        if self.y > 0:
            self.y -= self.get_speed()

    def move_down(self):
        if self.y < 800 - 50:
            self.y += self.get_speed()

    def sprite(self):
        return 'crabby.png'
    
    def is_near(self, other_crab, threshold=5):
        """Check if two crabs are within a given pixel threshold."""
        distance = ((self.x - other_crab.x) ** 2 + (self.y - other_crab.y) ** 2) ** 0.5
        return distance <= threshold
    