import pygame

class Settings():
    """A class to store all of the settings for alien invasion."""

    def __init__(self):
        """Initials the games settings."""

        # Screen settings
        self.screen_width = 1200
        self.screen_hight = 800
        self.bg_colour = (230, 230, 230)
        self.ship_speed_factor = 5
        self.ship_limit = 3
        self.columns = 0
        self.rows = 0

        # Display spacers, shims
        self.shim_h = 20
        self.shim_top = 100

        # Bullet settings
        self.bullet_speed_factor = 2
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_colour = 60, 200, 120
        self.bullets_allowd = 3
        self.rapidfire = False
        self.powerbullets = False
        self.widebullets = False

        # Alien settings
        self.alien_bullet_colour = 200, 60, 120
        self.alien_speed_factor = 1
        self.fleet_drop_speed = 10
        self.alien_fire_rate = 2

        # fleet_direction of 1 represents right, -1 left.
        self.fleet_direction = 1

        # How quickly the game speeds up.
        self.speedup_scale = 1.1

        # How quickly the alien point values increase.
        self.score_scale = 1.5

        self.initialise_dynamic_settings()

    def initialise_dynamic_settings(self):
        """Initialise the settings that change throughout the game."""
        self.ship_speed_factor = 1.5
        self.bullet_speed_factor = 3
        self.alien_speed_factor = 1
        self.alien_points = 50

    def increase_speed(self):
        """Increase speed settings and alien point values."""
        self.ship_speed_factor *= self.speedup_scale
        self.bullet_speed_factor *= self.speedup_scale
        self.alien_speed_factor *= self.speedup_scale
        self.alien_fire_rate = int(self.alien_fire_rate * self.speedup_scale)
        self.alien_points = int(self.alien_points * self.score_scale)

