import random
import time
import pygame
from entities.food import *
import config

class Crab:
   
    def __init__(self, x=None, y=None, energy=None, preferred_foods=None):
        self.x = random.randint(0, config.WORLD_WIDTH - 50)
        self.y = random.randint(0, config.SCREEN_HEIGHT - 50)
        self.speed = 1
        self.width = 50
        self.height = 50
        self.sprite = pygame.image.load("sprites/crabby.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
        self.energy = random.randint(10, 50) if energy is None else energy
        self.looking_for_mate = False
        self.sex = random.choice(['M', 'F'])
        self.rejected_mates = {}
        self.preferred_foods = self.generate_food_preferences()
        self.target_food = None
        self.food_to_remove = None 
    
    def update(self):
        self.energy -= 0.01

    def generate_food_preferences(self):
        """Assign a random float between 0.1 and 1.0 for each available food."""
        all_foods = [Seaweed, Plankton, Starfish, Shrimp, Clam, FishRemains]
        return {food: round(random.uniform(0.1, 1.0), 2) for food in all_foods}
    
    def look_for_mate(self, all_crabs: list["Crab"]):

        # Remove old rejections after some time (e.g., 5 seconds)
        current_time = time.time()
        self.rejected_mates = {mate_id: timestamp for mate_id, timestamp in self.rejected_mates.items() if current_time - timestamp < 5}

        # Find closest mate, but ignore rejected ones
        valid_mates = [mate for mate in all_crabs if mate is not self and id(mate) not in self.rejected_mates]

        if not valid_mates:
            return  # No valid mates left

        closest_mate = self.find_closest_mate(valid_mates)

        if closest_mate and self.is_near(closest_mate, threshold=5):
            if self.energy >= 50 and closest_mate.energy >= 50 and closest_mate.sex != self.sex:
                self.energy -= 40
                closest_mate.energy -= 40

                baby_crab = Crab(x=self.x, y=self.y, energy=20)
                baby_crab.preferred_foods = self.inherit_preferences(self.preferred_foods, closest_mate.preferred_foods)
                all_crabs.append(baby_crab)

            else:
                # Use `id(closest_mate)` as the key instead of the object itself
                self.rejected_mates[id(closest_mate)] = current_time

            return  # Stop moving closer after attempting to mate

        self.move_closer(closest_mate)

    def inherit_preferences(self, parent1_prefs, parent2_prefs):
        baby_prefs = {}
        all_foods = [Seaweed, Plankton, Starfish, Shrimp, Clam, FishRemains]
        mutation_chance = 0.01

        for food in all_foods:
            if random.random() < mutation_chance:
                # Random mutation
                baby_val = round(random.uniform(0.1, 1.0), 2)
                print(f"Mutation occurred for {food.__name__}: {baby_val}")
            else:
                parent1_val = parent1_prefs.get(food, 0.5)
                parent2_val = parent2_prefs.get(food, 0.5)
                avg = (parent1_val + parent2_val) / 2

                # Non-linear variation
                variation = (random.uniform(-1, 1) ** 3) * 0.5
                baby_val = round(max(0.1, min(1.0, avg + variation)), 2)

            baby_prefs[food] = baby_val

        return baby_prefs

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
        if not potential_food:
            return

        # Try to find the highest-ranked preferred food
        preferred_food = self.find_preferred_food(potential_food)

        # If no strongly preferred food is found, find any food
        if preferred_food and self.preferred_foods.get(type(preferred_food), 0) >= 0.2:
            target_food = preferred_food
        else:
            # Only choose fallback food if it's not disliked
            fallback = self.find_closest_food(potential_food)
            if fallback and self.preferred_foods.get(type(fallback), 0) >= 0.2:
                target_food = fallback
            else:
                return  # No food worth eating

        self.target_food = target_food

        if target_food.x == self.x and target_food.y == self.y:
            target_food.eat(self)
            self.food_to_remove = target_food
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
        best_food = None
        best_score = -1  # Higher is better
        preference_weight = 3

        for food in potential_food:
            if self.preferred_foods.get(type(food), 0) <= 0.2:
                continue
            food_type = type(food)
            preference = self.preferred_foods.get(food_type, 0.1)  # Default to 0.1 if missing

            distance = ((self.x - food.x) ** 2 + (self.y - food.y) ** 2) ** 0.5
            if distance == 0:  # Avoid division by zero
                distance = 0.1

            score = (preference * preference_weight) / distance

            if score > best_score:
                best_score = score
                best_food = food

        return best_food
    
    def make_decision(self, all_crabs, potential_food: list[Food]):
        if self.energy > 50:
            self.looking_for_mate = True
            self.look_for_mate(all_crabs)
        else:
            self.looking_for_mate = False
            all_food = potential_food[:]
            self.look_for_food(all_food)

    def get_speed(self):
        """Smooth speed scaling with energy."""
        return max(1, int(self.energy ** 0.5 / 4))  # Speed grows slower but more natural

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
    
    def is_near(self, other_crab, threshold=5):
        """Check if two crabs are within a given pixel threshold."""
        distance = ((self.x - other_crab.x) ** 2 + (self.y - other_crab.y) ** 2) ** 0.5
        return distance <= threshold
    
    def count_sexes(crabs):
        males = sum(1 for crab in crabs if crab.sex == 'M')
        females = sum(1 for crab in crabs if crab.sex == 'F')
        return males, females
    
    def adjust_food_preferences(self, eaten_food_type):
        for food_name in self.preferred_foods:
            if food_name == eaten_food_type.__name__:
                self.preferred_foods[food_name] += 0.05  # Reward the one just eaten
            else:
                self.preferred_foods[food_name] = max(0, self.preferred_foods[food_name] - 0.0025)  # Light decay

    