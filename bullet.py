import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    """A class to manage bullets fired from the ship."""

    def __init__(self, ai_settings, screen, vehicule):
        """Create a bullet object at the ships current position."""
        super(Bullet, self).__init__()
        self.screen = screen

        if ai_settings.widebullets == True:
            bullet_width = 100 * ai_settings.bullet_width
        else:
            bullet_width = ai_settings.bullet_width

        # Create a bullet rect at (0, 0).
        self.rect = pygame.Rect(0, 0, bullet_width, ai_settings.bullet_height)

        self.colour = ai_settings.bullet_colour
        self.speed_factor = ai_settings.bullet_speed_factor

    def update(self):
        """Move the bullet."""
        # Update the decimal position of the bullet.
        self.y += self.speed_factor * self.direction
        # Update the rect position.
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the bullet to the screen."""
        pygame.draw.rect(self.screen, self.colour, self.rect)


class FriendlyBullet(Bullet):
    """Bullet from the players ship."""
    def __init__(self, ai_settings, screen, ship):
        super(FriendlyBullet, self).__init__(ai_settings, screen, ship)
        # Set the bullets starting position.
        self.rect.centerx = ship.rect.centerx
        self.rect.top = ship.rect.top

        # Store the bullets position as a decimal value.
        self.y = float(self.rect.y)

        self.direction = -1


class AlienBullet(Bullet):
    """Bullet from an alien."""
    def __init__(self, ai_settings, screen, alien):
        super(AlienBullet, self).__init__(ai_settings, screen, alien)
        # Set the bullets starting position.
        self.rect.centerx = alien.rect.centerx
        self.rect.top = alien.rect.bottom

        # Store the bullets position as a decimal value.
        self.y = float(self.rect.y)

        self.direction = 1
        self.colour = ai_settings.alien_bullet_colour

