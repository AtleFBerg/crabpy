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
import time
from services.game_timer_service import game_timer


# World variables
camera_x = 0
camera_y = 0
boat = None 
inventory = {"crab_count": 0, "money": 0, "reverse_periscope": 0}
running = True

# Global simulation state
all_crabs = []  
all_food = []
world_food_respawn_timer = 0

# Global status effects
is_drunk = False
drunk_end_time = None
good_time_active = False
good_time_end_time = None
good_time_duration = 5 * 60  # 5 minutes in seconds


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
    global camera_x, camera_y, inventory, all_crabs, all_food, world_food_respawn_timer, is_drunk, drunk_end_time, good_time_active, good_time_end_time
    
    camera_x = 0
    camera_y = 0
    is_drunk = False
    drunk_end_time = None
    good_time_active = False
    good_time_end_time = None
    
    inventory.clear()
    inventory.update({
        "money": 0,
        "crab_count": 0,
        "beer_count": 0,
        "reverse_periscope": 0
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
    
    # Update status effects
    update_status_effects()


def update_status_effects():
    """Update drunk and good_time status effects."""
    global is_drunk, drunk_end_time, good_time_active, good_time_end_time
    from services.score_service import score_service
    
    current_time = time.time()
    
    # Check if drunk status has expired
    if is_drunk and drunk_end_time is not None:
        if current_time >= drunk_end_time:
            is_drunk = False
            drunk_end_time = None
    
    # Always sync boat drunk status with global
    if boat is not None:
        boat.is_drunk = is_drunk
    
    # Check if good time has expired
    if good_time_active and good_time_end_time is not None:
        if current_time >= good_time_end_time:
            good_time_active = False
            good_time_end_time = None
            score_service.set_burlesque_bonus(False)


def activate_drunk(duration=30):
    """Activate drunk status for specified duration (in seconds).
    If already drunk, extends the time."""
    global is_drunk, drunk_end_time
    current_time = time.time()
    
    if is_drunk and drunk_end_time is not None:
        # Extend existing drunk time
        drunk_end_time += duration
    else:
        # Start new drunk timer
        is_drunk = True
        drunk_end_time = current_time + duration
    
    if boat is not None:
        boat.is_drunk = True


def activate_good_time():
    """Activate good time status."""
    global good_time_active, good_time_end_time
    from services.score_service import score_service
    good_time_active = True
    good_time_end_time = time.time() + good_time_duration
    score_service.set_burlesque_bonus(True)


def get_drunk_remaining():
    """Get remaining drunk time in seconds."""
    global is_drunk, drunk_end_time
    if not is_drunk or drunk_end_time is None:
        return 0
    current_time = time.time()
    remaining = max(0, drunk_end_time - current_time)
    return int(remaining)


def get_good_time_remaining():
    """Get remaining good time in seconds."""
    global good_time_active, good_time_end_time
    if not good_time_active or good_time_end_time is None:
        return 0
    current_time = time.time()
    remaining = max(0, good_time_end_time - current_time)
    return int(remaining)


def draw_status_effects(screen, current_view_name):
    """Draw status effects overlay on screen (only in sea view)."""
    import pygame
    
    # Only draw in sea view
    if current_view_name != "sea" and current_view_name != "town":
        return
    
    box_width = 300
    box_height = 100
    box_x = 10
    box_y = config.SCREEN_HEIGHT - box_height - 10
    
    # Draw semi-transparent background box
    box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    pygame.draw.rect(box_surface, (0, 0, 0, 150), (0, 0, box_width, box_height))
    pygame.draw.rect(box_surface, (200, 200, 200), (0, 0, box_width, box_height), 2)
    screen.blit(box_surface, (box_x, box_y))
    
    # Draw status text
    font_small = pygame.font.SysFont(None, 24)
    font_label = pygame.font.SysFont(None, 20)
    
    y_offset = box_y + 10
    
    # Drunk status
    if is_drunk:
        drunk_text = font_small.render("3X DRUNKBONUS!", True, (255, 100, 100))
        drunk_time_remaining = get_drunk_remaining()
        drunk_time = font_label.render(f"{drunk_time_remaining}s", True, (255, 150, 150))
        screen.blit(drunk_text, (box_x + 10, y_offset))
        screen.blit(drunk_time, (box_x + 250, y_offset))
        y_offset += 35
    
    # Good time status
    if good_time_active:
        good_time_text = font_small.render("2X GOOD TIME BONUS!", True, (100, 255, 100))
        good_time_remaining_secs = get_good_time_remaining()
        time_remaining = _format_time(good_time_remaining_secs)
        good_time_clock = font_label.render(time_remaining, True, (150, 255, 150))
        screen.blit(good_time_text, (box_x + 10, y_offset))
        screen.blit(good_time_clock, (box_x + 250, y_offset))


def _format_time(seconds):
    """Format time as MM:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"
