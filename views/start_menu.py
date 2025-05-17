import pygame

class StartMenuView:
    def __init__(self, background_img):
        self.background_img = background_img
        self.buttons = [
            {"label": "New Game", "rect": pygame.Rect(340, 200, 200, 50)},
            {"label": "Load Game", "rect": pygame.Rect(340, 270, 200, 50)},
            {"label": "Settings", "rect": pygame.Rect(340, 340, 200, 50)},
            {"label": "Quit", "rect": pygame.Rect(340, 410, 200, 50)},
        ]
        self.font = pygame.font.SysFont(None, 40)

    def update(self, screen, *args, **kwargs):
        screen.blit(self.background_img, (0, 0))
        for button in self.buttons:
            pygame.draw.rect(screen, (30, 144, 255), button["rect"])
            label_surface = self.font.render(button["label"], True, (255, 255, 255))
            label_rect = label_surface.get_rect(center=button["rect"].center)
            screen.blit(label_surface, label_rect)
    
    def handle_events(self, events, boat, crab_inventory):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["label"] == "Quit":
                            pygame.quit()
                            exit()
                        elif button["label"] == "New Game":
                            return "sea"  # Return the key for the new view
        return None

    def handle_keys(self, keys, *args, **kwargs):
        pass  # No key handling for menu by default

        # Load background image for main menu
    def load_background():
        return pygame.image.load('assets/background.png')
