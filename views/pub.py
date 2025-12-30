import pygame
import random
import simulation

from animations import gui_elements
from .base_view import BaseView
import config

class PubView(BaseView):
    def __init__(self, boat=None):
        self.boat = boat
        self.background_img = pygame.image.load('assets/pub.png').convert_alpha()
        self.background_img = pygame.transform.scale(self.background_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.font = pygame.font.SysFont(None, 48)
        self.buttons = [
            {"label": "Buy Beer (5)", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 350, 250, 50)},
            {"label": "Back to Town", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 420, 250, 50)}
        ]
        self.selected_button_index = 0
        self.speech_bubble = pygame.image.load('assets/speech_bubble.png').convert_alpha()
        self.speech_bubble = pygame.transform.scale(self.speech_bubble, (500, 300))
        self.speech_bubble = pygame.transform.flip(self.speech_bubble, True, False)

        self.greetings = [
            "Welcome back!\nNothing says 'healthy coping'\nlike day-drinking with\na stranger, right?",
            "Ahoy there!\nAnother successful day of\navoiding your problems at sea?",
            "Good to see a familiar face!\nWell, familiar in the sense that\nI see you here every day.",
            "Pull up a stool!\nThe beer's cold,\nmy marriage is colder.",
            "Welcome, friend!\nBeer won't solve your problems,\nbut neither will\nsobriety, so...",
            "Hey there!\nYou know what they say:\n'It's 5 o'clock somewhere,\nand it's always somewhere here.'",
            "Come in, come in!\nThe beer's cold,\nthe atmosphere is depressing,\nand I wouldn't have it\nany other way.",
            "Ahoy!\nNothing like a good brew\nto remind you that tomorrow\nis another day to survive.",
            "Back again?\nI admire your dedication\nto slowly pickling your liver.",
            "Welcome!\nThey say money can't buy\nhappiness, but it can buy beer,\nwhich is pretty much\nthe same thing.",
            "Welcome!\nThey say life is just\na detour, to death.\nMight aswell have a beer."
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
        for i, button in enumerate(self.buttons):
            color = (255, 165, 0) if i == self.selected_button_index else (139, 69, 19)
            pygame.draw.rect(screen, color, button["rect"])  # Brown color for pub
            border_width = 3 if i == self.selected_button_index else 0
            if border_width:
                pygame.draw.rect(screen, (255, 255, 255), button["rect"], border_width)
            label_surface = self.font.render(button["label"], True, (255, 255, 255))
            label_rect = label_surface.get_rect(center=button["rect"].center)
            screen.blit(label_surface, label_rect)
        gui_elements.draw_inventory(screen, inventory, font)

    def handle_events(self, events, inventory):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_button_index = (self.selected_button_index - 1) % len(self.buttons)
                elif event.key == pygame.K_DOWN:
                    self.selected_button_index = (self.selected_button_index + 1) % len(self.buttons)
                elif event.key == pygame.K_RETURN:
                    selected_button = self.buttons[self.selected_button_index]
                    if selected_button["label"] == "Back to Town":
                        return "town"
                    elif selected_button["label"] == "Buy Beer (5)":
                        self.buy_beer(inventory)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, button in enumerate(self.buttons):
                    if button["rect"].collidepoint(event.pos):
                        self.selected_button_index = i
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
            # Activate global drunk effect (30 seconds)
            simulation.activate_drunk(duration=30)
            self.speech_text = "Here's your beer!\nDrink responsibly...\nJust kidding, I don't care."
        else:
            self.speech_text = "Sorry, friend.\nYou don't have enough schmeckles.\nProbably for the best, honestly."
