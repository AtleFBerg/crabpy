import pygame
import random

from animations import gui_elements
from .base_view import BaseView
import config

class CrabVendorView(BaseView):
    def __init__(self):
        self.background_img = pygame.image.load('assets/crab_vendor.png').convert_alpha()
        self.background_img = pygame.transform.scale(self.background_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.font = pygame.font.SysFont(None, 48)
        self.buttons = [
            {"label": "Sell Crabs", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 350, 200, 50)},
            {"label": "Back to Town", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 420, 200, 50)}
        ]
        self.speech_bubble = pygame.image.load('assets/speech_bubble.png').convert_alpha()
        self.speech_bubble = pygame.transform.scale(self.speech_bubble, (500, 300))
        self.speech_bubble = pygame.transform.flip(self.speech_bubble, True, False)

        self.greetings = [
            "Oh great, it’s you again.\nLet me guess — \nmore crabs. Wonderful.",
            "You smell like the docks.\nMust mean you’ve got crabs to sell.",
            "Back already?\nYou trying to bury me \nalive in crabs or what?",
            "If I see one more crab today,\n I’m moving inland.\nNow, let’s see what you’ve got.",
            "Ah, my favorite customer!\nSaid no one ever. \nShow me the crabs.",
            "You bring crabs,\n I bring disappointment.\nLet’s make this quick.",
            "Oh, fantastic.\nJust when I thought today\ncouldn’t get smellier.",
            "You again?\nIf you keep this up, I’ll start\n charging you rent for the counter.",
            "Crabs, huh?\nYou sure you don’t have\n anything nice,\n like gold? Or silence?",
            "Welcome back, crab dealer.\nYou’re single-handedly \nkeeping my misery alive."
        ]
        self.show_greeting()
    
    def show_greeting(self):
        self.is_speaking = True
        self.speech_text = random.choice(self.greetings)

    def update(self, screen, camera_x, camera_y, inventory, font, *args, **kwargs):
        screen.blit(self.background_img, (0, 0))
        if self.is_speaking:
            screen.blit(self.speech_bubble, (-50, 100))
            # Draw the speech text inside the bubble
            if hasattr(self, 'speech_text') and self.speech_text:
                speech_font = pygame.font.SysFont(None, 32)
                lines = self.speech_text.split('\n')
                for i, line in enumerate(lines):
                    text_surface = speech_font.render(line, True, (0, 0, 0))
                    text_rect = text_surface.get_rect(center=(200, + i * 20 + 200))
                    screen.blit(text_surface, text_rect)
        for button in self.buttons:
            pygame.draw.rect(screen, (30, 144, 255), button["rect"])
            label_surface = self.font.render(button["label"], True, (255, 255, 255))
            label_rect = label_surface.get_rect(center=button["rect"].center)
            screen.blit(label_surface, label_rect)
        gui_elements.draw_inventory(screen, inventory, font)

    def handle_events(self, events, inventory):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["label"] == "Back to Town":
                            return "town"
                        elif button["label"] == "Sell Crabs":
                            self.sell_crabs(inventory)
                            pass
        return None

    def handle_keys(self, keys):
        if keys[pygame.K_ESCAPE]:
            return "town_view"
        return None
    
    def sell_crabs(self, inventory):
        self.is_speaking = True
        crab_count = inventory.get("crab_count", 0)
        money_earned = crab_count * 10
        inventory["money"] += money_earned
        if crab_count == 0:
            self.speech_text = "You have no crabs to sell."
        else:
            self.speech_text = f"I will buy your {crab_count} crabs\nfor {money_earned} schmeckles."
        inventory["crab_count"] = 0
