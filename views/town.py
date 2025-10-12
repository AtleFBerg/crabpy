import pygame

from animations.water_animation import WaterAnimation
from .base_view import BaseView
import config
import os

class TownView(BaseView):
    TILE_SIZE = 32
    COLORS = {
        '#': (100, 80, 60),   # Wall/building
        '.': (220, 210, 180), # Walkable
        'G': (150, 200, 150), # Grass
        'T': (0, 100, 0),     # Tree
        'W': (0, 0, 255),     # Water
        'R': (255, 0, 0),     # Roof
        'P': (30, 144, 255),  # Pub
        'S': (60, 180, 60),   # Shipyard
        'C': (200, 80, 80),   # Crab vendor
        'E': (255, 255, 0),   # Entrance (to sea)
        '@': (0, 0, 0),       # Player
    }
    ENTRANCES = {'P': 'pub', 'S': 'shipyard', 'C': 'crab_vendor', 'E': 'sea'}

    def __init__(self):
        self.font = pygame.font.SysFont(None, 32)
        self.town_map = self.load_map()
        self.player_pos = self.find_spawn()
        self.info_text = "Walk around town!"
        self.transition = None
        self.move_cooldown = 0
        self.animating = False
        self.anim_start = None
        self.anim_from = None
        self.anim_to = None
        self.anim_duration = 4  # frames for smooth transition
        self.anim_progress = 0
        self.player_sprite = pygame.image.load("assets/sprites/player_sprite.png").convert_alpha()
        self.player_sprite = pygame.transform.scale(self.player_sprite, (self.TILE_SIZE, self.TILE_SIZE))
        self.grass_tile =  pygame.image.load("assets/sprites/grass_tile.png").convert_alpha()
        self.grass_tile = pygame.transform.scale(self.grass_tile, (self.TILE_SIZE, self.TILE_SIZE))
        self.water_tile = pygame.image.load("assets/sprites/water_tile.png").convert_alpha()
        self.water_tile = pygame.transform.scale(self.water_tile, (self.TILE_SIZE, self.TILE_SIZE))
        self.water_anim_rows = 7  # Number of rows for water animation at the bottom
        self.water_animation = WaterAnimation(
            screen_width=config.SCREEN_WIDTH,
            screen_height=self.water_anim_rows * self.TILE_SIZE
        )
        self.cobblestone_tile = pygame.image.load("assets/sprites/cobblestone_tile.jpg").convert()
        self.cobblestone_tile = pygame.transform.scale(self.cobblestone_tile, (self.TILE_SIZE, self.TILE_SIZE))
        # Initialize TILE_RECTS here so we can use self.tile_rect
        self.TILE_RECTS = {
            # Foundation
            'F': self.tile_rect(5, 12, 2, 1),
            # Ground Floor
            '1a': self.tile_rect(0, 12.5, 1.5, 1),
            '1b': self.tile_rect(1.5, 13, 3.5, 1),
            '1c': self.tile_rect(5, 12.5, 5.5, 1),
            # Upper Floor
            '2a': self.tile_rect(0, 9.5, 1.5, 1),
            '2b': self.tile_rect(1.5, 10, 3.5, 1),
            '2c': self.tile_rect(5, 9.5, 5.5, 1),
            #Attics
            '3a': self.tile_rect(1, 7.5, 1, 1),
            '3b': self.tile_rect(2.5, 7.5, 1, 1),
            '3c': self.tile_rect(4, 7.5, 1, 1),
            '3d': (*self.tile_rect(1, 6, 4, 0.5), 0, -16), 
            '3e': (*self.tile_rect(1, 6, 4, 0.5), 0, -16), 
            '3f': self.tile_rect(1.5, 6, 3.5, 0.5),

            # Roofs
            'E': self.tile_rect(11, 12.5, 2, 1),
            'C': self.tile_rect(13.5, 12.5, 2, 1),
            'S': self.tile_rect(13.5, 12.5, 2, 1),
            'P': self.tile_rect(13.5, 12.5, 2, 1),
            # Rooftop (just a few samples for demo)
            'R': (*self.tile_rect(0, 0, 4.5, 5), 16, -20),
            'r': (*self.tile_rect(1.5, 0, 2, 5), 16, -20),
        }

    @classmethod
    def tile_rect(cls, col, row, w=1, h=1):
        return (col * cls.TILE_SIZE, row * cls.TILE_SIZE, w * cls.TILE_SIZE, h * cls.TILE_SIZE)
    
    def should_draw_multi_tile(self, symbol, map_x, map_y):
        """Only draw if this tile is the top-left of a multi-tile group."""
        break_symbols = {'_'}
        left_same = (
            map_x > 0 and
            self.town_map[map_y][map_x - 1] == symbol and
            (map_x < 2 or self.town_map[map_y][map_x - 2] not in break_symbols)
        )
        top_same = (
            map_y > 0 and
            map_x < len(self.town_map[map_y - 1]) and
            self.town_map[map_y - 1][map_x] == symbol and
            (map_y < 2 or self.town_map[map_y - 2][map_x] not in break_symbols)
        )
        # If the tile to the left or above is a break symbol, treat this as a new group
        if map_x > 0 and self.town_map[map_y][map_x - 1] in break_symbols:
            left_same = False
        if map_y > 0 and map_x < len(self.town_map[map_y - 1]) and self.town_map[map_y - 1][map_x] in break_symbols:
            top_same = False
        return not (left_same or top_same)
    
    def draw_debug_grid(self, screen, width, height):
        for x in range(0, width, self.TILE_SIZE):
            pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, height))
        for y in range(0, height, self.TILE_SIZE):
            pygame.draw.line(screen, (50, 50, 50), (0, y), (width, y))

    def draw_tile(self, screen, symbol, x, y, map_x, map_y):
        if symbol in {'-', '_'}:
            return
    
        tileset = self.get_tileset()
        rect_info = self.TILE_RECTS.get(symbol)
        if symbol in ('R', 'r', 'E', 'C', 'P', 'S', '1a', '1b', '1c', '2a', '2b', '2c', '3d', '3e'):
            if self.should_draw_multi_tile(symbol, map_x, map_y) and rect_info:
                # Support (x, y, w, h) or (x, y, w, h, overlap)
                if len(rect_info) == 6:
                    rect = pygame.Rect(*rect_info[:4])
                    x_overlap = rect_info[4]
                    y_overlap = rect_info[5]
                else:
                    rect = pygame.Rect(*rect_info)
                    y_overlap = 0
                    x_overlap = 0
                y_offset = y - y_overlap if y_overlap else y
                x_offset = x - x_overlap if x_overlap else x
                screen.blit(tileset, (x_offset, y_offset), rect)
            else:
                return
        elif rect_info:
            if len(rect_info) == 6:
                rect = pygame.Rect(*rect_info[:4])
                y_overlap = rect_info[4]
                x_overlap = rect_info[5]
            else:
                rect = pygame.Rect(*rect_info)
                y_overlap = 0
                x_overlap = 0
            y_offset = y - y_overlap if y_overlap else y
            x_offset = x - x_overlap if x_overlap else x
            screen.blit(tileset, (x_offset, y_offset), rect)
        elif symbol == '.':
            screen.blit(self.cobblestone_tile, (x, y))
        else:
            color = self.COLORS.get(symbol, (180, 180, 180))
            pygame.draw.rect(screen, color, (x, y, self.TILE_SIZE, self.TILE_SIZE))
            
    def update(self, screen, camera_x, camera_y, *args, **kwargs):
        self.fill_with_grass(screen)
        self.water_animation.update()
        water_y = screen.get_height() - self.water_anim_rows * self.TILE_SIZE
        self.water_animation.draw_river(screen, 0, water_y)

        # Draw rows from bottom to top for correct overlap
        for y in reversed(range(len(self.town_map))):
            row = self.town_map[y]
            for x, cell in enumerate(row):
                self.draw_tile(screen, cell, x * self.TILE_SIZE, y * self.TILE_SIZE, x, y)
        if self.animating and self.anim_from and self.anim_to:
            t = self.anim_progress / self.anim_duration
            px = (1-t) * self.anim_from[0] + t * self.anim_to[0]
            py = (1-t) * self.anim_from[1] + t * self.anim_to[1]
            screen.blit(self.player_sprite, (px * self.TILE_SIZE, py * self.TILE_SIZE))
            self.anim_progress += 1
            if self.anim_progress >= self.anim_duration:
                self.animating = False
                self.player_pos = list(self.anim_to)
        else:
            px, py = self.player_pos
            screen.blit(self.player_sprite, (px * self.TILE_SIZE, py * self.TILE_SIZE))
        # Info
        text_surface = self.font.render(self.info_text, True, (60, 40, 20))
        screen.blit(text_surface, (10, 10))

    def handle_events(self, events, *args, **kwargs):
        # Check for entrance on every event (so view can change even if player is standing still)
        px, py = self.player_pos
        cell = self.town_map[py][px]
        if cell in self.ENTRANCES:
            # Move player back to previous tile (simulate stepping out of the shop)
            if hasattr(self, 'anim_from') and self.anim_from:
                self.player_pos = list(self.anim_from)
            else:
                # Fallback: try to move back in the opposite direction
                if cell == 'P':  # Pub
                    self.player_pos[1] += 1
                elif cell == 'S':  # Shipyard
                    self.player_pos[0] -= 1
                elif cell == 'C':  # Crab vendor
                    self.player_pos[0] -= 1
                elif cell == 'E':  # Sea
                    self.player_pos[1] += 1
            return self.ENTRANCES[cell]
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        return None

    def handle_keys(self, keys, *args, **kwargs):
        if self.animating:
            return None
        dx, dy = 0, 0
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return None
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
        if dx != 0 or dy != 0:
            nx, ny = self.player_pos[0] + dx, self.player_pos[1] + dy
            if self.is_walkable(nx, ny):
                self.animating = True
                self.anim_from = tuple(self.player_pos)
                self.anim_to = (nx, ny)
                self.anim_progress = 0
                self.move_cooldown = self.anim_duration
                cell = self.town_map[ny][nx]
                if cell in self.ENTRANCES:
                    # Return the name of the entrance view immediately
                    return self.ENTRANCES[cell]
        if not self.animating and self.transition:
            t = self.transition
            self.transition = None
            return t
        return None

    def is_walkable(self, x, y):
        if 0 <= y < len(self.town_map) and 0 <= x < len(self.town_map[0]):
            return self.town_map[y][x] in ('.', '-', 'E', 'P', 'S', 'C')
        return False

    def load_map(self):
        """Load the town map from assets/town_map.txt as a 2D list of tile codes."""
        map_path = os.path.join('assets', 'town_map.txt')
        with open(map_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Each line is split by spaces to support multi-character tile codes
        return [line.strip().split() for line in lines if line.strip()]

    def find_spawn(self):
        """Find the first walkable tile above an 'E' entrance to spawn the player."""
        for y, row in enumerate(self.town_map):
            for x, cell in enumerate(row):
                if cell == 'E' and y > 0:
                    # Check if the tile above is walkable
                    above = self.town_map[y - 1][x]
                    if above != '#' and above != 'R':
                        return [x, y - 1]
        # Fallback: first walkable tile
        for y, row in enumerate(self.town_map):
            for x, cell in enumerate(row):
                if cell == '.' or cell == '@':
                    return [x, y]
        return [1, 1]  # fallback

    def get_tileset(self):
        """Load and cache the tileset image. Compatible with browser/pygbag."""
        if not hasattr(self, '_tileset') or self._tileset is None:
            path = os.path.join('assets', 'tileset.png')
            try:
                img = pygame.image.load(path)
                # Use convert_alpha for browser compatibility
                self._tileset = img.convert_alpha()
            except Exception as e:
                # Fallback: create a dummy surface if tileset is missing
                self._tileset = pygame.Surface((self.TILE_SIZE*16, self.TILE_SIZE*16), pygame.SRCALPHA)
                self._tileset.fill((255, 0, 255, 128))
        return self._tileset
    
    def fill_with_grass(self, screen):
        tile_w, tile_h = self.grass_tile.get_width(), self.grass_tile.get_height()
        for y in range(0, screen.get_height(), tile_h):
            for x in range(0, screen.get_width(), tile_w):
                screen.blit(self.grass_tile, (x, y))
