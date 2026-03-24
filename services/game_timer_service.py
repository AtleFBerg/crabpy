import pygame
import time

class GameTimerService:
    def __init__(self, duration_minutes: int = 5):
        self._initial_duration = duration_minutes * 60
        self.duration_seconds = self._initial_duration
        self.start_time = None
        self.end_time = None
        self.is_running = False
        self.is_finished = False
        self.times_bought = 0
        self._font = None 
        
    @property
    def font(self):
        if self._font is None:
            if pygame.get_init():
                self._font = pygame.font.SysFont(None, 48)
            else:
                return None
        return self._font
        
    def start(self):
        self.start_time = time.time()
        self.is_running = True
        self.is_finished = False
        print(f"Game started! {self.duration_seconds // 60} minute timer begins...")
        
    def stop(self):
        if self.is_running:
            self.end_time = time.time()
            self.is_running = False
            
    def add_time(self, seconds: int):
        """Add extra seconds to the timer."""
        if self.is_running and not self.is_finished:
            self.duration_seconds += seconds
            print(f"Added {seconds} seconds! Total duration now: {self.duration_seconds}s")

    def reset(self):
        self.duration_seconds = self._initial_duration
        self.start_time = None
        self.end_time = None
        self.is_running = False
        self.is_finished = False
        self.times_bought = 0
        
    def update(self):
        if not self.is_running or self.is_finished:
            return
            
        elapsed = time.time() - self.start_time
        
        if elapsed >= self.duration_seconds:
            self.is_finished = True
            self.is_running = False
            self.end_time = time.time()
            print("TIME'S UP! Game Over!")
            
    def get_remaining_time(self) -> int:
        if not self.is_running or self.is_finished:
            return 0
            
        elapsed = time.time() - self.start_time
        remaining = max(0, self.duration_seconds - elapsed)
        return int(remaining)
        
    def get_elapsed_time(self) -> int:
        if not self.start_time:
            return 0
            
        end_time = self.end_time or time.time()
        return int(end_time - self.start_time)
        
    def format_time(self, seconds: int) -> str:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
        
    def draw_timer(self, screen, x: int = 10, y: int = 10):
        if not self.font:  
            return
            
        remaining = self.get_remaining_time()
        time_text = self.format_time(remaining)
        
        # Change color based on remaining time
        if remaining > 60:
            color = (255, 255, 255)  # White
        elif remaining > 30:
            color = (255, 255, 0)    # Yellow
        else:
            color = (255, 0, 0)      # Red
            
        if remaining <= 10 and remaining > 0:
            blink = int(time.time() * 4) % 2  
            if blink:
                color = (255, 100, 100)
                
        timer_surface = self.font.render(f"Time: {time_text}", True, color)
        screen.blit(timer_surface, (x, y))
        
        if self.is_finished:
            game_over_surface = self.font.render("GAME OVER!", True, (255, 0, 0))
            screen.blit(game_over_surface, (x, y + 50))

# Global timer instance
game_timer = GameTimerService(duration_minutes=10)