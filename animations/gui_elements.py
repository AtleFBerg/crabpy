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