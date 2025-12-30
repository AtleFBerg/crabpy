import pygame
import config
from entities.crab import Crab
import utils

def draw_average_crab_food_preferences(screen, all_crabs, font):
    if all_crabs:
        averages = utils.calculate_average_preferences(all_crabs)
        for i, (food_type, avg_preference) in enumerate(averages.items()):
            food_surface = font.render(f"{food_type.__name__}: {avg_preference:.2f}", True, (0, 0, 0))  # Black text
            screen.blit(food_surface, (10, 50 + i * 20))

def draw_toggle_button(screen, toggle_button_rect, font, view_mode):
    button_color = (0, 100, 200) if view_mode == "above" else (0, 0, 100)
    pygame.draw.rect(screen, button_color, toggle_button_rect)
    text = font.render(f"View: {view_mode}", True, (255, 255, 255))
    screen.blit(text, (toggle_button_rect.x + 10, toggle_button_rect.y + 10))

def draw_inventory(screen, inventory, font):
    y = 50
    for key, value in inventory.items():
        text = f"{key.replace('_', ' ').capitalize()}: {value}"
        text_surface = font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (config.SCREEN_WIDTH - 250, y))
        y += 30

def draw_selected_bait(screen, selected_bait, font):
    if selected_bait:
        bait_text = f"Bait: {selected_bait.__class__.__name__}"
        bait_surface = font.render(bait_text, True, (0, 0, 0))
        x = config.SCREEN_WIDTH - 250
        y = 10
        screen.blit(bait_surface, (x, y))
        if hasattr(selected_bait, "sprite"):
            sprite = selected_bait.sprite
            sprite_y = y + (bait_surface.get_height() - sprite.get_height()) // 2
            screen.blit(sprite, (x + bait_surface.get_width() + 10, sprite_y))
    else:
        bait_text = "Bait: None"
        bait_surface = font.render(bait_text, True, (0, 0, 0))
        screen.blit(bait_surface, (config.SCREEN_WIDTH - 250, 10))

def draw_crab_count(all_crabs, screen):
    m, f = Crab.count_sexes(all_crabs)
    font = pygame.font.SysFont(None, 30)
    text_surface = font.render(f"Males: {m}  Females: {f}", True, (0, 0, 0))
    screen.blit(text_surface, (10, 10))  # Top-left corner

def draw_to_town_arrow(screen, camera_x, camera_y):
    if not hasattr(draw_to_town_arrow, "arrow_image"):
        arrow_image = pygame.image.load('assets/arrow.png').convert_alpha()
        arrow_image = pygame.transform.scale(arrow_image, (50, 50))
        draw_to_town_arrow.arrow_image = arrow_image
    else:
        arrow_image = draw_to_town_arrow.arrow_image
    x = 50 - camera_x
    y = (config.SCREEN_HEIGHT // 2 - 25) - camera_y
    screen.blit(arrow_image, (x, y))
    font = pygame.font.SysFont(None, 32)
    text_surface = font.render('Town', True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + 25, y - 20))
    screen.blit(text_surface, text_rect)

def draw_status_effects(screen, is_drunk, drunk_remaining, good_time_active, good_time_remaining):
    """Draw status effects box in bottom left corner."""
    import simulation
    
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
        drunk_time = font_label.render(f"{drunk_remaining}s", True, (255, 150, 150))
        screen.blit(drunk_text, (box_x + 10, y_offset))
        screen.blit(drunk_time, (box_x + 250, y_offset))
        y_offset += 35
    
    # Good time status
    if good_time_active:
        good_time_text = font_small.render("2X GOOD TIME BONUS!", True, (100, 255, 100))
        time_remaining = format_time(good_time_remaining)
        good_time_clock = font_label.render(time_remaining, True, (150, 255, 150))
        screen.blit(good_time_text, (box_x + 10, y_offset))
        screen.blit(good_time_clock, (box_x + 250, y_offset))

def format_time(seconds):
    """Format time as MM:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"