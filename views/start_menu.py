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
        self.font = pygame.font.SysFont(None, 40)

    def update(self, screen, *args, **kwargs):
        screen.blit(self.background_img, (0, 0))
        screen.blit(self.controls_img, (screen.get_width() - self.controls_img.get_width() - 10, 10))
        for button in self.buttons:
            pygame.draw.rect(screen, (30, 144, 255), button["rect"])
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button["rect"].collidepoint(event.pos):
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
