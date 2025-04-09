import random
import time


class Food():
    def __init__(self, energy, width=25, height=25, time_to_multiply=None):
        self.energy = energy
        self.width = width
        self.height = height
        self.x = random.randint(0, 1024 - width)
        self.y = random.randint(0, 800 - height)
        self.time_to_multiply = time_to_multiply

    def eat(self, crab):
        crab.energy += self.energy
        crab.adjust_food_preferences(type(self))
        self.consumed = True
        self.last_eaten_time = time.time()

    def sprite(self):
        return f"sprites/{self.__class__.__name__}.png"
    
    def update(self):
        if self.time_to_multiply is not None:
            self.time_to_multiply -= 1
            if self.time_to_multiply <= 0:
                self.time_to_multiply = random.randint(300, 1200)
                return self.multiply()
            
    def multiply(self):
        new_food = self.__class__()
        new_food.x = random.randint(0, 1024 - new_food.width)
        new_food.y = random.randint(0, 800 - new_food.height)
        return new_food
   
class Seaweed(Food):
    def __init__(self):
        super().__init__(energy=10, time_to_multiply=150)

class Clam(Food):
    def __init__(self):
        super().__init__(energy=25, time_to_multiply=400)

class FishRemains(Food):
    def __init__(self):
        super().__init__(energy=40, time_to_multiply=400)

class Plankton(Food):
    def __init__(self):
        super().__init__(energy=5, time_to_multiply=150)

class Starfish(Food):
    def __init__(self):
        super().__init__(energy=30, time_to_multiply=400)

class Shrimp(Food):
    def __init__(self):
        super().__init__(energy=20, time_to_multiply=300)
