import pygame

from views.base_view import BaseView

class StartMenuView(BaseView):
    def __init__(self):
        self.background_img = StartMenuView.load_background()
        self.controls_img = StartMenuView.load_controls()
        self.controls_img = pygame.transform.scale(self.controls_img, (self.controls_img.get_width() // 4, self.controls_img.get_height() // 4))
        self.buttons = [
            {"label": "New Game", "rect": pygame.Rect(200, 500, 200, 50)},
            {"label": "Highscores", "rect": pygame.Rect(480, 500, 200, 50)},
        ]
        self.selected_button_index = 0
        self.font = pygame.font.SysFont(None, 40)

    def update(self, screen, *args, **kwargs):
        screen.blit(self.background_img, (0, 0))
        screen.blit(self.controls_img, (screen.get_width() - self.controls_img.get_width() - 10, 10))
        for i, button in enumerate(self.buttons):
            color = (255, 165, 0) if i == self.selected_button_index else (30, 144, 255)
            pygame.draw.rect(screen, color, button["rect"])
            border_width = 3 if i == self.selected_button_index else 0
            if border_width:
                pygame.draw.rect(screen, (255, 255, 255), button["rect"], border_width)
            label_surface = self.font.render(button["label"], True, (255, 255, 255))
            label_rect = label_surface.get_rect(center=button["rect"].center)
            screen.blit(label_surface, label_rect)
    
    def update_camera(self, *args, **kwargs):
        # No camera movement in the start menu
        return 0, 0
    
    def handle_events(self, events, crab_inventory):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_button_index = (self.selected_button_index - 1) % len(self.buttons)
                elif event.key == pygame.K_RIGHT:
                    self.selected_button_index = (self.selected_button_index + 1) % len(self.buttons)
                elif event.key == pygame.K_RETURN:
                    selected_button = self.buttons[self.selected_button_index]
                    if selected_button["label"] == "New Game":
                        return "sea"
                    elif selected_button["label"] == "Highscores":
                        return "highscores"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, button in enumerate(self.buttons):
                    if button["rect"].collidepoint(event.pos):
                        self.selected_button_index = i
                        if button["label"] == "New Game":
                            return "sea"
                        elif button["label"] == "Highscores":
                            return "highscores"
        return None

    def handle_keys(self, keys, *args, **kwargs):
        pass  # No key handling for menu by default

    @staticmethod
    def load_background():
        return pygame.image.load('assets/background.png').convert_alpha()
    
    @staticmethod
    def load_controls():

        return pygame.image.load('assets/controls.png').convert_alpha()
