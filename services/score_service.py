import pygame
from typing import Dict
from .game_timer_service import game_timer

class ScoreService:
    def __init__(self):
        self.reset_game()
        self.reset_callbacks = []  # List of functions to call when resetting
        self.burlesque_bonus_active = False  # Double points from burlesque
        self.cheats_used = False  # Track if cheats were used this game
    
    def reset_game(self):
        self.crabs_caught = 0
        self.drunk_catches = 0
        self.total_score = 0
        self.game_active = True
        self.game_ended = False
        self.burlesque_bonus_active = False
        self.cheats_used = False  # Reset cheat status
    
    def register_reset_callback(self, callback):
        self.reset_callbacks.append(callback)
    
    def start_new_game(self):
        print("Starting new game - resetting everything...")
        
        # Reset score and timer
        self.reset_game()
        game_timer.reset()
        game_timer.start()
        
        # Call all registered reset callbacks
        for callback in self.reset_callbacks:
            try:
                callback()
                print(f"Reset callback executed: {callback.__name__}")
            except Exception as e:
                print(f"Error in reset callback {callback.__name__}: {e}")

        print("New game started!")

    def update(self):
        game_timer.update()
        
        if game_timer.is_finished and not self.game_ended:
            self.end_game()
    
    def add_crab_catch(self, is_drunk: bool = False):
        if not self.game_active or game_timer.is_finished:
            return 0
            
        base_points = 10
        drunk_multiplier = 3 if is_drunk else 1
        burlesque_multiplier = 2 if self.burlesque_bonus_active else 1
        
        points = base_points * drunk_multiplier * burlesque_multiplier
        
        self.crabs_caught += 1
        if is_drunk:
            self.drunk_catches += 1
        
        self.total_score += points
        
        return points
    
    def set_burlesque_bonus(self, active: bool):
        """Enable or disable the burlesque double points bonus"""
        self.burlesque_bonus_active = active
        if active:
            print("Burlesque bonus activated! Double points for caught crabs!")
        else:
            print("Burlesque bonus expired.")
    
    def mark_cheats_used(self):
        """Mark that cheats were used in this game"""
        self.cheats_used = True
        print("Cheats detected! Highscore entry will be disabled.")
    
    def get_final_score(self) -> Dict:
        return {
            "total_score": self.total_score,
            "crabs_caught": self.crabs_caught,
            "drunk_catches": self.drunk_catches,
            "drunk_bonus": self.drunk_catches * 20,
            "game_time": game_timer.get_elapsed_time(),
            "cheats_used": self.cheats_used
        }
    
    def end_game(self):
        if not self.game_ended:
            self.game_active = False
            self.game_ended = True
            game_timer.stop()
            print(f"Game ended! Final score: {self.total_score}")
            return True
        return False
    
    def is_game_over(self) -> bool:
        return game_timer.is_finished or self.game_ended

# Global score service
score_service = ScoreService()