import random

from entities.food import Food


class Crab:
   
    def __init__(self, x=None, y=None, energy=None):
        self.x = random.randint(0, 1024 - 50)
        self.y = random.randint(0, 800 - 50)
        self.width = 50
        self.height = 50
        self.speed = 1
        self.energy = 40
        self.looking_for_mate = False
        self.sex = random.choice(['M', 'F'])
        self.rejected_mates = set()  # Track crabs that are not valid mates

    
    def look_for_mate(self, potential_mates: list["Crab"], all_crabs: list["Crab"]):
        if not potential_mates:
            return

        # Exclude rejected mates
        valid_mates = [mate for mate in potential_mates if mate not in self.rejected_mates]

        closest_mate = self.find_closest_mate(valid_mates)

        if closest_mate:
            if closest_mate.sex == self.sex:  
                self.rejected_mates.add(closest_mate)  # Ignore same-sex crabs permanently
                return

            if self.x == closest_mate.x and self.y == closest_mate.y:
                if self.energy >= 40 and closest_mate.energy >= 40:
                    self.energy -= 40
                    closest_mate.energy -= 40

                    # Create a baby crab at the same position
                    baby_crab = Crab(x=self.x, y=self.y, energy=20)
                    all_crabs.append(baby_crab)

                return  # Stop moving closer after mating

        self.move_closer(closest_mate)
        
    def move_closer(self, target):
        """Move towards the target without overshooting."""
        if not target:
            return
        
        speed = self.get_speed()

        # Calculate distance
        dx = target.x - self.x
        dy = target.y - self.y

        # If crab is close enough, snap to target position
        if abs(dx) <= speed:
            self.x = target.x
        else:
            self.x += speed if dx > 0 else -speed

        if abs(dy) <= speed:
            self.y = target.y
        else:
            self.y += speed if dy > 0 else -speed

    def find_closest_mate(self, potential_mates):
        closest_mate = None
        closest_distance = float('inf')
        for mate in potential_mates:
            if mate is self:
                continue
            distance = ((self.x - mate.x) ** 2 + (self.y - mate.y) ** 2) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_mate = mate
        return closest_mate   
    
    def look_for_food(self, potential_food: list[Food]):
        if not potential_food:  # Check if list is empty
            return
        
        closest_food = self.find_closest_food(potential_food)
        
        if closest_food.x == self.x and closest_food.y == self.y:
            closest_food.eat(self)
            self.food_to_remove = closest_food  # Mark for removal instead of deleting here
            return
        
        self.move_closer(closest_food)

    def find_closest_food(self, potential_food: list[Food]):   
        closest_food = None
        closest_distance = float('inf')
        for food in potential_food:
            distance = ((self.x - food.x) ** 2 + (self.y - food.y) ** 2) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_food = food
        return closest_food
    
    def make_decision(self, all_crabs, potential_mates, potential_food: list[Food]):
        if self.energy > 50:
            self.looking_for_mate = True
            self.look_for_mate(potential_mates, all_crabs)
        else:
            self.looking_for_mate = False
            self.look_for_food(potential_food)
    
    def get_speed(self):
        """Smooth speed scaling with energy."""
        return max(1, int(self.energy ** 0.5 / 2))  # Speed grows slower but more natural

    def move_left(self):
        if self.x > 0:
            self.x -= self.get_speed()

    def move_right(self):
        if self.x < 1024 - 50:
            self.x += self.get_speed()

    def move_up(self):
        if self.y > 0:
            self.y -= self.get_speed()

    def move_down(self):
        if self.y < 800 - 50:
            self.y += self.get_speed()

    def sprite(self):
        return 'crabby.png'
    