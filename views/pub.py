import pygame
import random

from animations import gui_elements
from .base_view import BaseView
import config

class PubView(BaseView):
    def __init__(self):
        self.background_img = pygame.image.load('assets/pub.png').convert_alpha()
        self.background_img = pygame.transform.scale(self.background_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.font = pygame.font.SysFont(None, 48)
        self.buttons = [
            {"label": "Buy Beer (5)", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 350, 250, 50)},
            {"label": "Back to Town", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 420, 250, 50)}
        ]
        self.speech_bubble = pygame.image.load('assets/speech_bubble.png').convert_alpha()
        self.speech_bubble = pygame.transform.scale(self.speech_bubble, (500, 300))
        self.speech_bubble = pygame.transform.flip(self.speech_bubble, True, False)

        self.greetings = [
            "Welcome to the pub!\nCare for a cold one?",
            "Ahoy there, sailor!\nWhat'll it be?",
            "Good to see you!\nThirsty after all that\ncrab catching?",
            "Pull up a stool!\nBeer's fresh today.",
            "Welcome, friend!\nA beer will fix\nwhatever ails you.",
            "Hey there!\nLooking to wet your whistle?",
            "Come in, come in!\nThe beer's cold and\nthe stories are tall.",
            "Ahoy!\nNothing like a good brew\nafter a day at sea."
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
            pygame.draw.rect(screen, (139, 69, 19), button["rect"])  # Brown color for pub
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
                        elif button["label"] == "Buy Beer (5)":
                            self.buy_beer(inventory)
        return None

    def handle_keys(self, keys):
        if keys[pygame.K_ESCAPE]:
            return "town"
        return None
    
    def buy_beer(self, inventory):
        self.is_speaking = True
        beer_price = 5
        if inventory.get("money", 0) >= beer_price:
            inventory["money"] -= beer_price
            inventory["beer_count"] = inventory.get("beer_count", 0) + 1
            self.speech_text = "Here's your beer!\nEnjoy, sailor!"
        else:
            self.speech_text = "Sorry, friend.\nYou don't have enough\nschmeckles for that."
