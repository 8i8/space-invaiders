import pygame
from pygame.sprite import Sprite

class Block(Sprite):
    """Block, part of the defence barricade."""
    def __init__(self, settings, screen, x, y):
        super(Block, self).__init__()
        self.screen = screen
        self.settings = settings

        # Create a block rect at (0, 0).
        self.rect = pygame.Rect(0, 0, settings.block_width,
                                    settings.block_height)
        self.rect.x = x
        self.rect.y = y
        self.colour = settings.blockade_colour

    def draw_block(self):
        """Draw block on screen."""
        pygame.draw.rect(self.screen, self.colour, self.rect)
