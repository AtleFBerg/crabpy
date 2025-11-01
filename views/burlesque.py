import pygame
import time
import random
from .base_view import BaseView
from services.score_service import score_service
import config


class BurlesqueView(BaseView):
    """
    Burlesque joint where players can have a 'Good time' for 300 money.
    Provides double points for caught crabs for the next 5 minutes.
    """

    def __init__(self):
        super().__init__()
        
        # Background and visual elements
        self.background_img = pygame.image.load('assets/burlesque_vendor.png').convert_alpha()
        self.background_img = pygame.transform.scale(self.background_img, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        
        # Speech bubble
        self.speech_bubble = pygame.image.load('assets/speech_bubble.png').convert_alpha()
        self.speech_bubble = pygame.transform.scale(self.speech_bubble, (500, 300))
        self.speech_bubble = pygame.transform.flip(self.speech_bubble, True, False)
        
        # Good time mechanics
        self.good_time_cost = 300
        self.good_time_duration = 5 * 60  # 5 minutes in seconds
        self.good_time_active = False
        self.good_time_start_time = None
        self.good_time_end_time = None
        
        # UI fonts
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        
        # Buttons
        self.good_time_button = pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 350, 200, 50)
        self.exit_button = pygame.Rect(config.SCREEN_WIDTH // 2 - 100, 420, 200, 50)
        
        # Dialog system
        self.is_speaking = False  # Start with no dialog showing
        self.should_greet = True   # Flag to show greeting when view becomes active
        self.greetings = [
            "Welcome to\nThe Saucy Sailor!\nWhere the perfume's strong,\nthe rum's stronger,\nand the crabs are...\nwell-seasoned.",
            "Oooh, look what\ndrifted in!\nSmells like low tide\nand bad decisions.\nPerfect — you'll\nfit right in.",
            "Ahoy, sugar!\nIf your catch today\ndidn't pinch ya,\nour dancers\njust might.",
            "Welcome, darling!\nShake off the sea stink,\nkeep the wallet open,\nand try not to scratch\nyour… curiosity.",
            "Hey sailor!\nIf you're tired\nof catchin' crabs,\ncongrats — you're in\nthe wrong place.",
            "Step right up, stinky!\nWe've got glitz, glamour,\nand glitter that\nsticks longer than\ndock-bugs in beard hair.",
            "Welcome aboard, captain!\nOur gals are hotter\nthan a boiler room\nand twice as dangerous\nto your hygiene.",
            "Lookin' for adventure?\nWe've got thrills, spills,\nand a lingering scent\nyou won't forget.",
            "Come on in!\nIf your ship smells\nlike fish, you'll feel\nright at home here.",
            "Welcome to paradise!\nWhere the rum flows,\nthe feathers fly,\nand nobody asks why you’re itching."
        ]
        
        self.show_greeting()
        
        # Register reset callback
        score_service.register_reset_callback(self.reset_burlesque_state)
        
    def show_greeting(self):
        """Show a random greeting when entering the burlesque"""
        self.is_speaking = True
        self.speech_text = random.choice(self.greetings)
        
    def reset_burlesque_state(self):
        """Reset burlesque state when game resets"""
        self.good_time_active = False
        self.good_time_start_time = None
        self.good_time_end_time = None
        self.is_speaking = False
        self.should_greet = True  
        score_service.set_burlesque_bonus(False)
        
    def can_afford_good_time(self, inventory):
        """Check if player can afford good time"""
        return inventory.get("money", 0) >= self.good_time_cost
        
    def purchase_good_time(self, inventory):
        """Purchase good time if affordable"""
        if self.can_afford_good_time(inventory) and not self.good_time_active:
            inventory["money"] -= self.good_time_cost
            self.good_time_active = True
            self.good_time_start_time = time.time()
            self.good_time_end_time = self.good_time_start_time + self.good_time_duration
            
            # Activate the scoring bonus
            score_service.set_burlesque_bonus(True)
            return True
        return False
        
    def is_good_time_active(self):
        """Check if good time bonus is currently active"""
        if not self.good_time_active:
            return False
            
        current_time = time.time()
        if current_time >= self.good_time_end_time:
            self.good_time_active = False
            # Deactivate the scoring bonus
            score_service.set_burlesque_bonus(False)
            return False
            
        return True
        
    def get_good_time_remaining(self):
        """Get remaining good time in seconds"""
        if not self.is_good_time_active():
            return 0
            
        current_time = time.time()
        remaining = max(0, self.good_time_end_time - current_time)
        return int(remaining)
        
    def format_time(self, seconds):
        """Format time as MM:SS"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def update(self, screen, camera_x, camera_y, inventory, font, *args, **kwargs):
        # Draw background image
        screen.blit(self.background_img, (0, 0))
        
        # Show greeting when entering the view
        if self.should_greet:
            self.show_greeting()
            self.should_greet = False
        
        # Update good time status (this will deactivate bonus if expired)
        self.is_good_time_active()
        
        if self.is_speaking:
            screen.blit(self.speech_bubble, (-50, 100))
            if hasattr(self, 'speech_text') and self.speech_text:
                speech_font = pygame.font.SysFont(None, 32)
                lines = self.speech_text.split('\n')
                for i, line in enumerate(lines):
                    text_surface = speech_font.render(line, True, (0, 0, 0))
                    text_rect = text_surface.get_rect(center=(200, + i * 20 + 200))
                    screen.blit(text_surface, text_rect)
        
        # Draw buttons
        # Good time button - always shows the same text
        button_color = (100, 50, 75) if not self.good_time_active else (50, 25, 40)
        pygame.draw.rect(screen, button_color, self.good_time_button)
        pygame.draw.rect(screen, (255, 255, 255), self.good_time_button, 3)
        
        # Static button text
        button_text = "Good time 500$"
        text_color = (255, 255, 255) if not self.good_time_active else (150, 150, 150)
            
        button_surface = self.font.render(button_text, True, text_color)
        button_rect = button_surface.get_rect(center=self.good_time_button.center)
        screen.blit(button_surface, button_rect)
        
        # Exit button
        pygame.draw.rect(screen, (100, 0, 0), self.exit_button)
        pygame.draw.rect(screen, (255, 255, 255), self.exit_button, 2)
        exit_text = self.font.render("Back to Town", True, (255, 255, 255))
        exit_rect = exit_text.get_rect(center=self.exit_button.center)
        screen.blit(exit_text, exit_rect)
        
        # Good time status overlay
        if self.is_good_time_active():
            remaining = self.get_good_time_remaining()
            status_text = self.font.render(f"Good Time: {self.format_time(remaining)}", True, (0, 255, 0))
            screen.blit(status_text, (10, 10))
            
            bonus_text = self.small_font.render("Double points for caught crabs!", True, (255, 255, 0))
            screen.blit(bonus_text, (10, 40))

    def handle_events(self, events, inventory, *args, **kwargs):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.exit_button.collidepoint(event.pos):
                        self.should_greet = True  # Reset for next entry
                        return "town"
                    elif self.good_time_button.collidepoint(event.pos):
                        if self.purchase_good_time(inventory):
                            # Show success dialog
                            self.is_speaking = True
                            self.speech_text = "Excellent choice, darling!\nYou're in for a treat."
                        elif not self.can_afford_good_time(inventory):
                            # Show not enough money dialog
                            self.is_speaking = True
                            self.speech_text = f"Sorry sugar, you need\n300$ for our special\nentertainment. Come back\nwhen you're ready!"
                        elif self.good_time_active:
                            # Already active dialog
                            self.is_speaking = True
                            self.speech_text = "You're already having\nthe time of your life!"
        return None

    def handle_keys(self, keys, *args, **kwargs):
        if keys[pygame.K_ESCAPE]:
            self.should_greet = True  # Reset for next entry
            return "town"
        return None