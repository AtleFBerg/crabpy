import pygame

class UnderwaterAnimation:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sea_bed_tile = pygame.image.load("sprites/sea_bed_tile.png").convert_alpha()
        self.sea_bed_tile = pygame.transform.scale(self.sea_bed_tile, (32, 32))
        self.sea_bed_tile_width, self.sea_bed_tile_height = self.sea_bed_tile.get_width(), self.sea_bed_tile.get_height()
        
    def draw(self, screen, camera_x, camera_y):
        start_x = -int(camera_x) % self.sea_bed_tile_width - self.sea_bed_tile_width
        start_y = -int(camera_y) % self.sea_bed_tile_height - self.sea_bed_tile_height

        for x in range(start_x, self.screen_width + self.sea_bed_tile_width, self.sea_bed_tile_width):
            for y in range(start_y, self.screen_height + self.sea_bed_tile_height, self.sea_bed_tile_height):
                screen.blit(self.sea_bed_tile, (x, y))