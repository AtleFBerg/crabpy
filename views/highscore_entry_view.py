import pygame
import asyncio
from views.base_view import BaseView
from integrations.supabase_client import supabase_client
import config

class HighscoreEntryView(BaseView):
    def __init__(self, score_data=None):
        super().__init__()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        from services.score_service import score_service
        self.score_data = score_data or score_service.get_final_score()
        
        self.available_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
                                  'Æ', 'Ø', 'Å']
        self.initials = [0, 0, 0]  
        self.current_position = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        self.message = ""
        self.message_color = (255, 255, 255)
        self.submitting = False
        self.existing_score = None
        self.checking_existing = False
        self.existing_checked = False
        
        if self.score_data:
            self.check_initials()
    
    def get_initials_string(self):
        """Get initials as a string"""
        return ''.join([self.available_letters[i] for i in self.initials])
    
    def get_current_letters(self):
        """Get current letters as a list"""
        return [self.available_letters[i] for i in self.initials]
    
    async def check_existing_score(self):
        if self.checking_existing:
            return
        
        self.checking_existing = True
        try:
            initials_str = self.get_initials_string()
            self.existing_score = await supabase_client.get_existing_score(initials_str)
            self.existing_checked = True
            print(f"Existing score check for {initials_str}: {self.existing_score}")
        except Exception as e:
            print(f"Error checking existing score: {e}")
            self.existing_score = None
            self.existing_checked = True
        finally:
            self.checking_existing = False
    
    def check_initials(self):
        if not self.checking_existing:
            self.existing_checked = False
            asyncio.create_task(self.check_existing_score())
    
    def change_letter(self, direction):
        if self.submitting:
            return
        
        current_index = self.initials[self.current_position]
        
        if direction == 1:  # Up arrow
            new_index = current_index + 1
            if new_index >= len(self.available_letters):
                new_index = 0  # Wrap around to A
        else:  # Down arrow
            new_index = current_index - 1
            if new_index < 0:
                new_index = len(self.available_letters) - 1  # Wrap around to Å
        
        self.initials[self.current_position] = new_index
        self.message = "" 
        
        # Show current letter in console for debugging
        current_letter = self.available_letters[new_index]
        print(f"Changed to: {current_letter} (index {new_index})")
        
        self.check_initials()
    
    def move_cursor(self, direction):
        if self.submitting:
            return
            
        if direction == 1 and self.current_position < 2:  
            self.current_position += 1
        elif direction == -1 and self.current_position > 0: 
            self.current_position -= 1
    
    async def submit_score_async(self):
        if self.submitting:
            return
        
        self.submitting = True
        self.message = "Submitting score..."
        self.message_color = (255, 255, 0)
        
        try:
            initials_str = self.get_initials_string()
            print(f"Submitting score with initials: {initials_str}")
            success, message = await supabase_client.submit_or_update_score(
                initials_str,
                self.score_data['total_score'],
                self.score_data['crabs_caught'],
                self.score_data['drunk_bonus']
            )
            
            self.message = message
            self.message_color = (0, 255, 0) if success else (255, 100, 100)
            
            if success:
                await asyncio.sleep(2)
                self.should_transition = True
                
        except Exception as e:
            print(f"Error submitting score: {e}")
            self.message = "Failed to submit score"
            self.message_color = (255, 100, 100)
        finally:
            self.submitting = False
    
    def submit_score(self):
        if not self.submitting:
            asyncio.create_task(self.submit_score_async())
    
    def update(self, screen, camera_x, camera_y, inventory, font):
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Blink every 30 frames
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
        
        # Clear screen
        screen.fill((20, 20, 40))
        
        # Title
        title_text = self.font_large.render("ENTER YOUR INITIALS", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)
        
        # Score display
        if self.score_data:
            score_text = f"Score: {self.score_data['total_score']:,}"
            score_surface = self.font_medium.render(score_text, True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 150))
            screen.blit(score_surface, score_rect)
        
        center_x = config.SCREEN_WIDTH // 2
        letter_spacing = 80
        start_x = center_x - letter_spacing
        
        # Get current letters
        current_letters = self.get_current_letters()
        
        for i in range(3):
            # Letter box
            box_x = start_x + (i * letter_spacing)
            box_y = 220
            letter_box = pygame.Rect(box_x - 30, box_y, 60, 60)
            
            # Highlight current position
            if i == self.current_position and not self.submitting:
                box_color = (100, 100, 150) if self.cursor_visible else (70, 70, 100)
                border_color = (255, 255, 0)
                border_width = 3
            else:
                box_color = (50, 50, 50)
                border_color = (255, 255, 255)
                border_width = 2
            
            pygame.draw.rect(screen, box_color, letter_box)
            pygame.draw.rect(screen, border_color, letter_box, border_width)
            
            try:
                letter_surface = self.font_large.render(current_letters[i], True, (255, 255, 255))
                letter_rect = letter_surface.get_rect(center=letter_box.center)
                screen.blit(letter_surface, letter_rect)
            except Exception as e:
                print(f"Error rendering letter {current_letters[i]}: {e}")
                fallback_surface = self.font_large.render("?", True, (255, 100, 100))
                fallback_rect = fallback_surface.get_rect(center=letter_box.center)
                screen.blit(fallback_surface, fallback_rect)
        
        # Instructions
        if not self.submitting:
            instructions = [
                "Use UP/DOWN arrows to change letters",
                "Use LEFT/RIGHT arrows to move cursor", 
                "Letters: A-Z, Æ, Ø, Å",
                "Press ENTER to submit"
            ]
            
            for i, instruction in enumerate(instructions):
                instruction_surface = self.font_small.render(instruction, True, (200, 200, 200))
                instruction_rect = instruction_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 320 + i * 25))
                screen.blit(instruction_surface, instruction_rect)
        
        # Current initials display (for debugging)
        current_initials_text = f"Current: {self.get_initials_string()}"
        debug_surface = self.font_small.render(current_initials_text, True, (100, 255, 100))
        screen.blit(debug_surface, (10, 10))
        
        # Existing score warning
        if self.existing_score and self.existing_checked and not self.submitting:
            if self.score_data['total_score'] > self.existing_score["score"]:
                warning_text = f"Will replace your score of {self.existing_score['score']:,}"
                color = (255, 215, 0)
            else:
                warning_text = f"Current best: {self.existing_score['score']:,} (higher than {self.score_data['total_score']:,})"
                color = (255, 100, 100)
            
            warning_surface = self.font_small.render(warning_text, True, color)
            warning_rect = warning_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 450))
            screen.blit(warning_surface, warning_rect)
        elif self.checking_existing:
            checking_text = "Checking existing score..."
            checking_surface = self.font_small.render(checking_text, True, (255, 255, 0))
            checking_rect = checking_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 450))
            screen.blit(checking_surface, checking_rect)
        
        # Message display
        if self.message:
            message_surface = self.font_medium.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 490))
            screen.blit(message_surface, message_rect)
        
        # Back button
        back_button = pygame.Rect(50, config.SCREEN_HEIGHT - 80, 100, 50)
        pygame.draw.rect(screen, (100, 0, 0), back_button)
        back_text = self.font_small.render("BACK", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_rect)
    
    def handle_events(self, events, inventory):
        if hasattr(self, 'should_transition') and self.should_transition:
            return "highscores"
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "game_over"
                elif event.key == pygame.K_UP:
                    self.change_letter(1)  # Next letter in sequence
                elif event.key == pygame.K_DOWN:
                    self.change_letter(-1)  # Previous letter in sequence
                elif event.key == pygame.K_LEFT:
                    self.move_cursor(-1)  # Move cursor left
                elif event.key == pygame.K_RIGHT:
                    self.move_cursor(1)  # Move cursor right
                elif event.key == pygame.K_RETURN:
                    if not self.submitting:
                        if self.existing_score and self.score_data['total_score'] <= self.existing_score["score"]:
                            self.message = f"Score too low! Your best: {self.existing_score['score']:,}"
                            self.message_color = (255, 100, 100)
                        else:
                            self.submit_score()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Back button
                back_button = pygame.Rect(50, config.SCREEN_HEIGHT - 80, 100, 50)
                if back_button.collidepoint(event.pos):
                    return "game_over"
                
                center_x = config.SCREEN_WIDTH // 2
                letter_spacing = 80
                start_x = center_x - letter_spacing
                
                for i in range(3):
                    box_x = start_x + (i * letter_spacing)
                    letter_box = pygame.Rect(box_x - 30, 220, 60, 60)
                    if letter_box.collidepoint(event.pos) and not self.submitting:
                        self.current_position = i
                        break
        
        return None
    
    def handle_keys(self, keys, *args, **kwargs):
        pass