
import pygame

class WaterAnimation:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.water_tile = pygame.image.load("assets/sprites/water_tile.png").convert_alpha()
        self.water_tile = pygame.transform.scale(self.water_tile, (32, 32))
        self.water_tile_width, self.water_tile_height = self.water_tile.get_width(), self.water_tile.get_height()
        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_speed = 0.5  # Adjust this value to change the speed of the water animation

    def update(self):
        # Update the scroll position for the water animation
        self.scroll_x += self.scroll_speed
        self.scroll_y += self.scroll_speed
        if self.scroll_x >= self.water_tile_width:
            self.scroll_x = 0
        if self.scroll_y >= self.water_tile_height:
            self.scroll_y = 0

    def draw(self, surface):
        # Draw the water tiles on the surface
        for x in range(0, self.screen_width + self.water_tile_width , self.water_tile_width):
            for y in range(0, self.screen_height + self.water_tile_height , self.water_tile_height):
                surface.blit(self.water_tile, (x - int(self.scroll_x), y - int(self.scroll_y)))

