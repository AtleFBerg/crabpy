import pygame
from .base_view import BaseView
import config

class TownView(BaseView):
    def __init__(self):
        self.background_color = (220, 210, 180)  # Light tan for placeholder
        self.font = pygame.font.SysFont(None, 48)
        self.info_text = "Welcome to Town! (WIP)"
        self.buttons = [
            {"label": "Pub", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 300, 200, 50)},
            {"label": "Crab vendor", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 370, 200, 50)},
            {"label": "Shipyard", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 440, 200, 50)},
            {"label": "Back to Sea", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 510, 200, 50)}
        ]

    def update(self, screen, camera_x, camera_y, *args, **kwargs):
        screen.fill(self.background_color)
        text_surface = self.font.render(self.info_text, True, (60, 40, 20))
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, 200))
        screen.blit(text_surface, text_rect)
        for button in self.buttons:
            pygame.draw.rect(screen, (30, 144, 255), button["rect"])
            label_surface = self.font.render(button["label"], True, (255, 255, 255))
            label_rect = label_surface.get_rect(center=button["rect"].center)
            screen.blit(label_surface, label_rect)

    def handle_events(self, events, *args, **kwargs):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["label"] == "Back to Sea":
                            return "sea"
                        elif button["label"] == "Crab vendor":
                            return "crab_vendor"
                        elif button["label"] == "Shipyard":
                            return "shipyard"
        return None

    def handle_keys(self, keys, *args, **kwargs):
        # Example: ESC to go back to sea
        if keys[pygame.K_ESCAPE]:
            return "sea"
        return None
