"""
Global simulation state and logic for the game world.
Manages crabs, food, and world state updates.
"""
from collections import defaultdict
from entities.boat import Boat
from entities.food import Food, load_food_images
from entities.crab import Crab
import config
import utils
from services.game_timer_service import game_timer


# World variables
camera_x = 0
camera_y = 0
boat = None 
inventory = {"crab_count": 0, "money": 0, "reverse_periscope": False}
running = True

# Global simulation state
all_crabs = []  
all_food = []
world_food_respawn_timer = 0


def initialize_simulation():
    """Initialize simulation after pygame display is set up.
    Must be called after pygame.display.set_mode()."""
    global boat, all_crabs
    
    load_food_images()
    
    if boat is None:
        boat = Boat(100, 100)
    
    if not all_crabs:
        all_crabs.extend([Crab() for _ in range(config.INITIAL_CRAB_COUNT)])
    
    utils.world_food_respawn(all_food)


def reset_global_game_state():
    """Reset all global simulation variables to initial state."""
    global camera_x, camera_y, inventory, all_crabs, all_food, world_food_respawn_timer
    
    camera_x = 0
    camera_y = 0
    
    beer_count = inventory.get("beer_count", 0)
    inventory.clear()
    inventory.update({
        "money": 0,
        "crab_count": 0,
        "beer_count": beer_count,
        "reverse_periscope": False
    })

    # Reset global simulation
    all_crabs.clear()
    all_crabs.extend([Crab() for _ in range(config.INITIAL_CRAB_COUNT)])
    all_food.clear()
    utils.world_food_respawn(all_food)
    world_food_respawn_timer = 0


def update_global_simulation():
    global all_crabs, all_food, world_food_respawn_timer
    
    # Only run simulation when game is active
    if not game_timer.is_running or game_timer.is_finished:
        return
    
    # Update food respawn timer
    world_food_respawn_timer += 1
    if world_food_respawn_timer % 2000 == 0:
        utils.world_food_respawn(all_food)
        world_food_respawn_timer = 0
    
    # Update food
    food_counts = defaultdict(int)
    for food in all_food:
        food_counts[type(food)] += 1
    
    for food in all_food:
        new_food = food.update(food_counts)
        if new_food:
            all_food.append(new_food)
    
    # Update crabs
    food_to_remove = []
    crabs_to_remove = []
    
    for crab in all_crabs:
        crab.update()
        if crab.energy <= 0.0:
            crabs_to_remove.append(crab)
            continue
        
        crab.make_decision(all_crabs=all_crabs, potential_food=all_food)
        if crab.food_to_remove:
            food_to_remove.append(crab.food_to_remove)
            crab.food_to_remove = None
    
    # Remove dead crabs
    for crab in crabs_to_remove:
        all_crabs.remove(crab)
    
    # Remove consumed food
    if food_to_remove:
        Food.remove_food(food_to_remove, all_food)
    
    # Check for crabs in boat pots
    if boat is not None and boat.pots:
        for crab_pot in boat.pots:
            crab_pot.check_for_crabs(all_crabs, all_food)
