import pygame
from pygame.sprite import Sprite

class Block(Sprite):
    """Block, part of the defence barricade."""
    def __init__(self, settings, screen, x, y):
        self.screen = screen
        self.settings = settings

        # Create a block rect at (0, 0).
        self.rect = pygame.Rect(x, y, settings.block_width, settings.block_height)

        self.colour = settings.blockade_colour

    def draw_block(self):
        """Draw block on screen."""
        pygame.draw.rect(self.screen, self.colour, self.rect)
