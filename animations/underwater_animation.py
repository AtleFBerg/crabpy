import pygame


class UnderwaterAnimation:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sea_bed_tile = pygame.image.load("sprites/sea_bed_tile.png").convert_alpha()
        self.sea_bed_tile = pygame.transform.scale(self.sea_bed_tile, (32, 32))
        self.sea_bed_tile_width, self.sea_bed_tile_height = self.sea_bed_tile.get_width(), self.sea_bed_tile.get_height()
        
    def draw(self, screen):
        for x in range(0, self.screen_width + self.sea_bed_tile_width, self.sea_bed_tile_width):
            for y in range(0, self.screen_height + self.sea_bed_tile_height, self.sea_bed_tile_height):
                screen.blit(self.sea_bed_tile, (x, y))