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

    def sprite(self):
        raise NotImplementedError("Each food type must define its own sprite")
    
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
   
class Seaweeds(Food):
    def __init__(self):
        super().__init__(energy=10, time_to_multiply=200)

    def sprite(self):
        return 'seaweed.png'

class Clam(Food):
    def __init__(self):
        super().__init__(energy=25, time_to_multiply=600)
    
    def sprite(self):
        return 'clam.png'

class FishRemains(Food):
    def __init__(self):
        super().__init__(energy=40, time_to_multiply=800)
    
    def sprite(self):
        return 'fish_remains.png'

class Plankton(Food):
    def __init__(self):
        super().__init__(energy=5, time_to_multiply=200)
    
    def sprite(self):
        return 'plankton.png'

class Starfish(Food):
    def __init__(self):
        super().__init__(energy=30, time_to_multiply=600)
    
    def sprite(self):
        return 'starfish.png'

class Shrimp(Food):
    def __init__(self):
        super().__init__(energy=20, time_to_multiply=400)
    
    def sprite(self):
        return 'shrimp.png'