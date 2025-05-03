import pygame
import config
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

def draw_current_crab_count(screen, crab_inventory, font):
    crab_count_text = f"Caught crabs: {crab_inventory['count']}"
    crab_count_surface = font.render(crab_count_text, True, (0, 0, 0)) 
    screen.blit(crab_count_surface, (config.SCREEN_WIDTH -200, 50)) 