import pygame
from pygame.sprite import Sprite

class Ship(Sprite):

    def __init__(self, settings, screen):
        """Initialise the ship and set its starting position."""
        super(Ship, self).__init__()
        self.settings = settings
        self.screen = screen
        self.screen_rect = screen.get_rect()

        # Load the ship image and get its rect.
        self.image = pygame.image.load('images/ship.png')
        self.rect = self.image.get_rect()

        # Start each new ship at the bottom center of the screen.
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom

        # Store decimal value for the ships center
        self.center = float(self.rect.centerx)

        # Movement flags
        self.moving_left = False
        self.moving_right = False

    def update(self):
        """Update the ships position based on the movement flag."""
        if self.moving_left and self.rect.left > self.screen_rect.left:
            self.center -= self.settings.ship_speed_factor
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.center += self.settings.ship_speed_factor

        # Update rect object from self.center`
        self.rect.centerx = self.center

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        """Return ship to center for game restart."""
        self.center = self.screen_rect.centerx
