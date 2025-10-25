import pygame
import asyncio
from views.base_view import BaseView
from services.score_service import score_service
from integrations.supabase_client import supabase_client
import config

class GameOverView(BaseView):
    def __init__(self):
        super().__init__()
        self.font_large = pygame.font.SysFont(None, 72)
        self.font_medium = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 36)
        
        self.score_data = None
        self.is_high_score = False
        self.is_checking_score = False
        self.buttons_created = False
        self.high_score_checked = False
    
    async def check_high_score(self):
        if not self.score_data or self.is_checking_score:
            return
        
        self.is_checking_score = True
        try:
            self.is_high_score = await supabase_client.is_high_score(self.score_data['total_score'])
            print(f"High score check result: {self.is_high_score}")
            self.buttons_created = False
        except Exception as e:
            print(f"Error checking high score: {e}")
            self.is_high_score = True
            self.buttons_created = False
        finally:
            self.is_checking_score = False
        
    def create_buttons(self):
        """Create buttons - only call this after high score check is complete"""
        if self.buttons_created or self.is_checking_score:
            return
            
        if not self.high_score_checked:
            return
        
        # Buttons
        button_width = 200
        button_height = 50
        center_x = config.SCREEN_WIDTH // 2
        
        self.buttons = []
        y_offset = 400
        
        if self.is_high_score:
            self.buttons.append({
                "label": "ENTER INITIALS",
                "rect": pygame.Rect(center_x - button_width // 2, y_offset, button_width, button_height),
                "action": "highscore_entry"
            })
            y_offset += 60
        
        self.buttons.extend([
            {
                "label": "NEW GAME",
                "rect": pygame.Rect(center_x - button_width // 2, y_offset, button_width, button_height),
                "action": "sea"  
            },
            {
                "label": "VIEW HIGHSCORES",
                "rect": pygame.Rect(center_x - button_width // 2, y_offset + 60, button_width, button_height),
                "action": "highscores"
            }
        ])
        
        self.buttons_created = True
        print(f"Buttons created. High score: {self.is_high_score}")
        
    def update(self, screen, camera_x, camera_y, inventory, font):
        if not self.score_data:
            self.score_data = score_service.get_final_score()
            print(f"Score data: {self.score_data}")
        
        if not self.high_score_checked and not self.is_checking_score:
            self.high_score_checked = True
            asyncio.create_task(self.check_high_score())
        
        if not self.buttons_created and not self.is_checking_score:
            self.create_buttons()
        
        screen.fill((20, 20, 40))
        
        # Game Over title
        title_text = self.font_large.render("GAME OVER", True, (255, 100, 100))
        title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Show checking status
        if self.is_checking_score:
            checking_text = self.font_medium.render("Checking high score...", True, (255, 255, 0))
            checking_rect = checking_text.get_rect(center=(config.SCREEN_WIDTH // 2, 140))
            screen.blit(checking_text, checking_rect)
        elif self.is_high_score:
            # High score notification
            high_score_text = self.font_medium.render("NEW HIGH SCORE!", True, (255, 215, 0))
            high_score_rect = high_score_text.get_rect(center=(config.SCREEN_WIDTH // 2, 140))
            screen.blit(high_score_text, high_score_rect)
        
        # Score display
        if self.score_data:
            score_y = 200
            score_texts = [
                f"Final Score: {self.score_data['total_score']:,}",
                f"Crabs Caught: {self.score_data['crabs_caught']}",
                f"Drunk Catches: {self.score_data['drunk_catches']}",
                f"Drunk Bonus: +{self.score_data['drunk_bonus']}",
                f"Game Time: {self.format_time(self.score_data['game_time'])}"
            ]
            
            for i, text in enumerate(score_texts):
                color = (255, 215, 0) if i == 0 else (255, 255, 255)
                score_surface = self.font_medium.render(text, True, color)
                score_rect = score_surface.get_rect(center=(config.SCREEN_WIDTH // 2, score_y + i * 30))
                screen.blit(score_surface, score_rect)
        
        # Draw buttons
        if hasattr(self, 'buttons') and self.buttons:
            for button in self.buttons:
                color = (100, 100, 100) if button["action"] != "sea" else (0, 100, 0)
                pygame.draw.rect(screen, color, button["rect"])
                pygame.draw.rect(screen, (255, 255, 255), button["rect"], 2)
                
                button_text = self.font_small.render(button["label"], True, (255, 255, 255))
                button_text_rect = button_text.get_rect(center=button["rect"].center)
                screen.blit(button_text, button_text_rect)
    
    def format_time(self, seconds: int) -> str:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def handle_events(self, events, inventory):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "town"
                elif event.key == pygame.K_RETURN:
                    if self.is_high_score and not self.is_checking_score:
                        return "highscore_entry"
                    elif not self.is_checking_score:
                        score_service.start_new_game()
                        return "sea"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self, 'buttons') and self.buttons and not self.is_checking_score:
                    for button in self.buttons:
                        if button["rect"].collidepoint(event.pos):
                            if button["action"] == "sea":
                                score_service.start_new_game()
                            return button["action"]
        
        return None
    
    def handle_keys(self, keys, *args, **kwargs):
        pass