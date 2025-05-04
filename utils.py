import random
from collections import defaultdict
import pygame
from entities.crab import Crab
from entities.food import Seaweed, Plankton, Starfish, Shrimp, Clam, FishRemains
import config
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

def world_food_respawn(all_food):
    # Define food types and their probabilities (weights)
    food_weights = {
        Seaweed: 0.3,       # 30% chance
        Clam: 0.1,          # 15% chance
        FishRemains: 0.1,    # 10% chance
        Plankton: 0.3,       # 30% chance
        Starfish: 0.1,       # 10% chance
        Shrimp: 0.1         # 5% chance
    }
    food_classes = list(food_weights.keys())
    food_probabilities = list(food_weights.values())

    for i in range(30):
        food_class = random.choices(food_classes, weights=food_probabilities, k=1)[0]  # Pick a food type based on weight
        food = food_class()  # Create the food object
        all_food.append(food)  # Store it

def update_camera(boat):

    # Target center based on boat pot
    target_x = boat.x + boat.width // 2 - config.SCREEN_WIDTH // 2
    target_y = boat.base_y + boat.height // 2 - config.SCREEN_HEIGHT // 2

    # Clamp to world bounds
    camera_x = max(0, min(target_x, config.WORLD_WIDTH - config.SCREEN_WIDTH))
    camera_y = max(0, min(target_y, config.WORLD_HEIGHT - config.SCREEN_HEIGHT))

    return camera_x, camera_y

