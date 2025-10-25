import pygame
import asyncio
from views.base_view import BaseView
from integrations.supabase_client import supabase_client
import config

class HighscoresView(BaseView):
    def __init__(self):
        super().__init__()
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 42)
        self.font_small = pygame.font.Font(None, 32)
        self.scores = []
        self.loading = False
        self.loading_started = False
        self.load_task = None  # Track the async task
        
        self.back_button = pygame.Rect(50, config.SCREEN_HEIGHT - 80, 150, 50)
    
    async def load_scores_async(self):
        try:
            print("Loading scores from database...")
            self.scores = await supabase_client.get_top_scores(10)
            print(f"Loaded {len(self.scores)} scores: {self.scores}")
            self.loading = False
        except Exception as e:
            print(f"Error loading scores: {e}")
            self.scores = []
            self.loading = False
        finally:
            self.load_task = None  
        
    def refresh_scores(self):
        if not self.loading and not self.load_task:
            self.loading = True
            self.loading_started = True
            
            try:
                self.load_task = asyncio.create_task(self.load_scores_async())
                print("Created async task for loading scores")
            except Exception as e:
                print(f"Error creating async task: {e}")
                self.loading = False
                self.scores = [
                    {"initials": "AAA", "score": 1000, "crabs_caught": 50, "drunk_bonus": 20},
                    {"initials": "BBB", "score": 800, "crabs_caught": 40, "drunk_bonus": 15},
                    {"initials": "CCC", "score": 600, "crabs_caught": 30, "drunk_bonus": 10},
                ]
                print("Using fallback scores")
    
    def update(self, screen, camera_x, camera_y, inventory, font):
        if not self.loading_started:
            self.refresh_scores()
        
        if self.load_task and self.load_task.done():
            try:
                self.load_task.result()
                print("Async loading completed successfully")
            except Exception as e:
                print(f"Async loading failed: {e}")
                self.loading = False
                self.scores = []
            finally:
                self.load_task = None
        
        screen.fill((0, 20, 40))
        
        # Title
        title_text = self.font_large.render("HIGH SCORES", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, 60))
        screen.blit(title_text, title_rect)
        
        if self.loading:
            loading_text = self.font_medium.render("Loading...", True, (255, 255, 255))
            loading_rect = loading_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
            screen.blit(loading_text, loading_rect)
        else:
            # Draw scores
            start_y = 120
            for i, score in enumerate(self.scores):
                rank = i + 1
                initials = score.get('initials', 'AAA')
                points = score.get('score', 0)
                crabs = score.get('crabs_caught', 0)
                drunk_bonus = score.get('drunk_bonus', 0)
                
                # Rank and initials
                rank_text = f"{rank:2d}. {initials}"
                rank_surface = self.font_medium.render(rank_text, True, (255, 255, 255))
                screen.blit(rank_surface, (100, start_y + i * 35))
                
                # Score
                score_text = f"{points:,}"
                score_surface = self.font_medium.render(score_text, True, (255, 215, 0))
                screen.blit(score_surface, (300, start_y + i * 35))
                
                # Details
                details_text = f"{crabs} crabs"
                if drunk_bonus > 0:
                    details_text += f" (+{drunk_bonus} drunk bonus)"
                details_surface = self.font_small.render(details_text, True, (150, 150, 150))
                screen.blit(details_surface, (500, start_y + i * 35 + 5))
            
            if not self.scores:
                no_scores_text = self.font_medium.render("No scores yet! Be the first!", True, (255, 255, 255))
                no_scores_rect = no_scores_text.get_rect(center=(config.SCREEN_WIDTH // 2, 200))
                screen.blit(no_scores_text, no_scores_rect)
        
        # Refresh button
        refresh_button = pygame.Rect(config.SCREEN_WIDTH - 200, config.SCREEN_HEIGHT - 80, 150, 50)
        refresh_color = (0, 100, 0) if not self.loading else (100, 100, 100)
        pygame.draw.rect(screen, refresh_color, refresh_button)
        refresh_text = self.font_small.render("REFRESH", True, (255, 255, 255))
        refresh_rect = refresh_text.get_rect(center=refresh_button.center)
        screen.blit(refresh_text, refresh_rect)
        
        # Back button
        pygame.draw.rect(screen, (100, 0, 0), self.back_button)
        back_text = self.font_small.render("BACK", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_button.center)
        screen.blit(back_text, back_rect)
    
    def handle_events(self, events, inventory):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "game_over"
                elif event.key == pygame.K_r and not self.loading:  # Only refresh if not already loading
                    self.refresh_scores()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Back button
                if self.back_button.collidepoint(event.pos):
                    return "game_over"
                
                refresh_button = pygame.Rect(config.SCREEN_WIDTH - 200, config.SCREEN_HEIGHT - 80, 150, 50)
                if refresh_button.collidepoint(event.pos) and not self.loading:
                    self.loading_started = False  # Reset so it can start fresh
                    self.refresh_scores()

        return None
    
    def handle_keys(self, keys, *args, **kwargs):
        pass