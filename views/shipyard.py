import pygame
from animations import gui_elements
from .base_view import BaseView
import config
from entities.boat import Boat

class ShipyardView(BaseView):
    # Purchase limits: None means unlimited
    PURCHASE_LIMITS = {
        "Upgrade Engine": None,
        "Buy Crab Pot": None,
        "Reverse Periscope": 3,
    }

    def __init__(self, boat: Boat):
        self.boat = boat
        self.background_img = pygame.image.load('assets/shipyard.png').convert_alpha()
        self.background_img = pygame.transform.scale(self.background_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.font = pygame.font.SysFont(None, 30)
        self.buttons = [
            {"label": "Upgrade Ship", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 350, 200, 50)},
            {"label": "Back to Town", "rect": pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 420, 200, 50)}
        ]
        self.selected_button_index = 0
        self.show_grid = False
        grid_y = 200
        grid_spacing_x = 200
        grid_spacing_y = 100
        grid_center = config.SCREEN_WIDTH // 2
        self.grid_items = [
            {"label": "Upgrade Engine", "price": 10, "rect": pygame.Rect(grid_center - grid_spacing_x, grid_y, 180, 80)},
            {"label": "Buy Crab Pot", "price": 10, "rect": pygame.Rect(grid_center + 20, grid_y, 180, 80)},
            {"label": "Reverse Periscope", "price": 15, "rect": pygame.Rect(grid_center - 90, grid_y + grid_spacing_y, 180, 80)},
            {"label": "Back", "price": None, "rect": pygame.Rect(grid_center - 90, grid_y + 2 * grid_spacing_y, 180, 80)}
        ]
        self.purchase_counts = {"Upgrade Engine": 0, "Buy Crab Pot": 0, "Reverse Periscope": 0}
        self.selected_grid_index = 0
        self.info_text = "Shipyard"
        self.speech_text = None

        # Register reset callback
        from services.score_service import score_service
        score_service.register_reset_callback(self.reset_shipyard_state)

    def reset_shipyard_state(self):
        """Reset shipyard state when game resets"""
        self.purchase_counts = {"Upgrade Engine": 0, "Buy Crab Pot": 0, "Reverse Periscope": 0}
        self.show_grid = False
        self.selected_grid_index = 0
        self.speech_text = None

    def update(self, screen, camera_x, camera_y, inventory, font, *args, **kwargs):
        screen.blit(self.background_img, (0, 0))
        text_surface = self.font.render(self.info_text, True, (30, 60, 90))
        text_rect = text_surface.get_rect(center=(screen.get_width() // 2, 120))
        screen.blit(text_surface, text_rect)
        if self.speech_text:
            speech_font = pygame.font.SysFont(None, 32)
            lines = self.speech_text.split('\n')
            for i, line in enumerate(lines):
                text_surface = speech_font.render(line, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(screen.get_width() // 2, 180 + i * 30))
                screen.blit(text_surface, text_rect)
        if self.show_grid:
            for i, item in enumerate(self.grid_items):
                label = item["label"]
                limit = self.PURCHASE_LIMITS.get(label)
                is_maxed = limit is not None and self.purchase_counts.get(label, 0) >= limit

                if is_maxed:
                    color = (80, 80, 80)  # Grey when maxed out
                elif i == self.selected_grid_index:
                    color = (255, 165, 0)
                else:
                    color = (60, 180, 60)
                pygame.draw.rect(screen, color, item["rect"])
                border_width = 3 if i == self.selected_grid_index else 0
                if border_width:
                    pygame.draw.rect(screen, (255, 255, 255), item["rect"], border_width)
                text_color = (150, 150, 150) if is_maxed else (255, 255, 255)
                label_surface = self.font.render(item["label"], True, text_color)
                label_rect = label_surface.get_rect(center=(item["rect"].centerx, item["rect"].centery - 15))
                screen.blit(label_surface, label_rect)
                if item["price"] is not None:
                    if is_maxed:
                        price_surface = self.font.render("MAXED", True, (255, 100, 100))
                    else:
                        price_surface = self.font.render(f"${item['price']}", True, (255, 255, 0))
                    price_rect = price_surface.get_rect(center=(item["rect"].centerx, item["rect"].centery + 20))
                    screen.blit(price_surface, price_rect)
        else:
            for i, button in enumerate(self.buttons):
                color = (255, 165, 0) if i == self.selected_button_index else (30, 144, 255)
                pygame.draw.rect(screen, color, button["rect"])
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
                if self.show_grid:
                    if event.key == pygame.K_ESCAPE:
                        self.show_grid = False
                        self.selected_grid_index = 0
                    elif event.key == pygame.K_LEFT:
                        self.selected_grid_index = (self.selected_grid_index - 1) % len(self.grid_items)
                    elif event.key == pygame.K_RIGHT:
                        self.selected_grid_index = (self.selected_grid_index + 1) % len(self.grid_items)
                    elif event.key == pygame.K_UP:
                        # Move up in grid
                        if self.selected_grid_index == 2:
                            # From middle row, go back to top row
                            self.selected_grid_index = 0
                        elif self.selected_grid_index == 3:
                            # From bottom row, go to middle row
                            self.selected_grid_index = 2
                        else:
                            # From top row, wrap to bottom
                            self.selected_grid_index = 3
                    elif event.key == pygame.K_DOWN:
                        # Move down in grid
                        if self.selected_grid_index in [0, 1]:
                            # From top row, go to middle row
                            self.selected_grid_index = 2
                        elif self.selected_grid_index == 2:
                            # From middle row, go to bottom row
                            self.selected_grid_index = 3
                        elif self.selected_grid_index == 3:
                            # From bottom row, wrap to top
                            self.selected_grid_index = 0
                    elif event.key == pygame.K_RETURN:
                        selected_item = self.grid_items[self.selected_grid_index]
                        if selected_item["label"] == "Back":
                            self.show_grid = False
                            self.selected_grid_index = 0
                        else:
                            self.buy_item(selected_item["label"], inventory)
                else:
                    if event.key == pygame.K_UP:
                        self.selected_button_index = (self.selected_button_index - 1) % len(self.buttons)
                    elif event.key == pygame.K_DOWN:
                        self.selected_button_index = (self.selected_button_index + 1) % len(self.buttons)
                    elif event.key == pygame.K_RETURN:
                        selected_button = self.buttons[self.selected_button_index]
                        if selected_button["label"] == "Back to Town":
                            return "town"
                        elif selected_button["label"] == "Upgrade Ship":
                            self.show_grid = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.show_grid:
                    for i, item in enumerate(self.grid_items):
                        if item["rect"].collidepoint(event.pos):
                            self.selected_grid_index = i
                            if item["label"] == "Back":
                                self.show_grid = False
                                self.selected_grid_index = 0
                                return None
                            self.buy_item(item["label"], inventory)
                else:
                    for i, button in enumerate(self.buttons):
                        if button["rect"].collidepoint(event.pos):
                            self.selected_button_index = i
                            if button["label"] == "Back to Town":
                                return "town"
                            elif button["label"] == "Upgrade Ship":
                                self.show_grid = True
        return None

    def handle_keys(self, keys):
        if keys[pygame.K_ESCAPE]:
            if self.show_grid:
                self.show_grid = False
            else:
                return "town_view"
        return None
    
    def is_maxed(self, item_name):
        """Check if an item has reached its purchase limit."""
        limit = self.PURCHASE_LIMITS.get(item_name)
        if limit is None:
            return False
        return self.purchase_counts.get(item_name, 0) >= limit

    def buy_item(self, item_name, inventory):
        # Check purchase limit first
        if self.is_maxed(item_name):
            self.speech_text = f"{item_name} is already maxed out!"
            return

        if item_name == "Upgrade Engine":
            if inventory["money"] >= 10:
                inventory["money"] -= 10
                self.boat.speed += 0.5 
                self.purchase_counts[item_name] += 1
                self.speech_text = "Engine upgraded!"
            else:
                self.speech_text = "Not enough money for engine upgrade."
        elif item_name == "Buy Crab Pot":
            if inventory["money"] >= 10:
                inventory["money"] -= 10
                self.boat.max_pots += 1
                self.purchase_counts[item_name] += 1
                self.speech_text = "Crab pot purchased!"
            else:
                self.speech_text = "Not enough money for crab pot."
        elif item_name == "Reverse Periscope":
            if inventory["money"] >= 15:
                inventory["money"] -= 15
                self.purchase_counts[item_name] += 1
                level = self.purchase_counts[item_name]
                inventory["reverse_periscope"] = level
                level_names = {1: "installed", 2: "upgraded", 3: "fully upgraded"}
                self.speech_text = f"Periscope {level_names.get(level, 'upgraded')}!"
            else:
                self.speech_text = "Not enough money for periscope."
