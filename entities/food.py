import random


class Food():
    def __init__(self, energy, width=50, height=50):
        self.energy = energy
        self.width = width
        self.height = height
        self.x = random.randint(0, 1024 - width)
        self.y = random.randint(0, 800 - height)
    
    def eat(self, crab):
        crab.energy += self.energy
        
    def sprite(self):
        raise NotImplementedError("Each food type must define its own sprite")

class Seaweeds(Food):
    def __init__(self):
        super().__init__(energy=10)
    
    def sprite(self):
        return 'seaweed.png'

class Clam(Food):
    def __init__(self):
        super().__init__(energy=25)
    
    def sprite(self):
        return 'clam.png'

class FishRemains(Food):
    def __init__(self):
        super().__init__(energy=40)
    
    def sprite(self):
        return 'fish_remains.png'

class Plankton(Food):
    def __init__(self):
        super().__init__(energy=5, width=30, height=30)
    
    def sprite(self):
        return 'plankton.png'

class Starfish(Food):
    def __init__(self):
        super().__init__(energy=30)
    
    def sprite(self):
        return 'starfish.png'

class Shrimp(Food):
    def __init__(self):
        super().__init__(energy=20)
    
    def sprite(self):
        return 'shrimp.png'