import random
from collections import defaultdict
import pygame
from entities.food import Seaweed, Plankton, Starfish, Shrimp, Clam, FishRemains
def calculate_average_preferences(crabs):

    totals = defaultdict(float)
    counts = defaultdict(int)

    for crab in crabs:
        for food_type, score in crab.preferred_foods.items():
            totals[food_type] += score
            counts[food_type] += 1

    averages = {}
    for food_type in totals:
        averages[food_type] = totals[food_type] / counts[food_type]

    return averages

def world_food_respawn(all_food, food_sprites):
    # Define food types and their probabilities (weights)
    food_weights = {
        Seaweed: 0.3,       # 30% chance
        Clam: 0.1,          # 15% chance
        FishRemains: 0.1,    # 10% chance
        Plankton: 0.3,       # 30% chance
        Starfish: 0.1,       # 10% chance
        Shrimp: 0.1         # 5% chance
    }
    # Generate exactly 20 food items based on the given probabilities
    food_classes = list(food_weights.keys())
    food_probabilities = list(food_weights.values())
    
    for i in range(30):
        food_class = random.choices(food_classes, weights=food_probabilities, k=1)[0]  # Pick a food type based on weight
        food = food_class()  # Create the food object
        all_food.append(food)  # Store it

        # Load and scale the sprite
        sprite = pygame.image.load(food.sprite()).convert_alpha()
        sprite = pygame.transform.scale(sprite, (25, 25))
        food_sprites.append(sprite)