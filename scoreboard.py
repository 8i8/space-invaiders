import pygame.font
from pygame.sprite import Group

from ship import Ship


class Scoreboard():
    """A class to report scoring information."""

    def __init__(self, settings, screen, stats):
        """Initialise scorekeeping attributes."""
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.settings = settings
        self.stats = stats

        # Font settings for scoring information.
        self.text_colour = (230, 230, 230)
        self.font = pygame.font.SysFont(None, 48)

        # Prepare the initial score alnd level images.
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()
        if settings.debug:
            self.prep_fire_rate(0)

    def prep_score(self):
        """Turn the score into a rendered image."""
        rounded_score = int(round(self.stats.score, -1))
        score_str = "{:,}".format(rounded_score)
        self.score_image = self.font.render(score_str, True, self.text_colour)

        # Display the score at the top right of the screen.
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def prep_high_score(self):
        """Turn the high score into a rendered image."""
        high_score = int(round(self.stats.high_score, -1))
        high_score_str = "{:,}".format(high_score)
        self.high_score_image = self.font.render(high_score_str, True,
                self.text_colour)

        # Center the high score at the top of the screen.
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = self.score_rect.top

    def prep_level(self):
        """Turn the level into a rendered image."""
        self.level_image = self.font.render(str(self.stats.level), True,
                self.text_colour)

        # Position the level below the score.
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10

    def prep_ships(self):
        """Show how many ships are left."""
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.settings, self.screen)
            ship.rect.x = 10 + ship_number * ship.rect.width
            ship.rect.y = 10
            self.ships.add(ship)

    def prep_fire_rate(self, rate):
        """debug fire rate"""
        self.fire_rate = rate
        self.fire_rate_str = "{:,}".format(rate)
        self.fire_rate_image = self.font.render(self.fire_rate_str, True,
                self.text_colour)

        self.fire_rate_rect = self.level_image.get_rect()
        self.fire_rate_rect.left = self.screen_rect.left + 10
        self.fire_rate_rect.bottom = self.screen_rect.bottom - 10

    def show_score(self):
        """Draw scores and level count to the screen."""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        if self.settings.debug:
            self.screen.blit(self.fire_rate_image, self.fire_rate_rect)
        self.ships.draw(self.screen)

