import pygame

class Settings():
    """A class to store all of the settings for alien invasion."""

    def __init__(self):
        """Initialise the games settings."""

        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_colour = (230, 230, 230)
        self.columns = 0
        self.rows = 0
        self.bg_image = pygame.image.load("images/dark_city.bmp")
        self.debug = False

        # Ship settings
        self.ship_speed_factor = 0
        self.ship_limit = 3

        # Bullet settings
        self.bullet_speed_factor = 0
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_colour = 60, 200, 120
        self.bullets_allowd = 3
        self.rapidfire = False
        self.powerbullets = False
        self.widebullets = False

        # Alien settings
        self.shim_y = 100
        self.shim_x = 20
        self.alien_points = 0
        self.alien_bullet_colour = 200, 60, 120
        self.alien_speed_factor = 0
        self.fleet_drop_speed = 10
        self.alien_fire_rate = 0
        self.alien_columns_removed = 2

        # Blockade settings
        self.blockade_colour = 25, 70, 90
        self.block_width = 6
        self.block_height = 6

        # fleet_direction of 1 represents right, -1 left.
        self.fleet_direction = 1

        # How quickly the game speeds up.
        self.speedup_scale = 1.2

        # How quickly the alien point values increase.
        self.score_scale = 1.5
        self.alien_fire_scale = 0.98

        self.initialise_dynamic_settings()

    def initialise_dynamic_settings(self):
        """Initialise the settings that change throughout the game."""
        self.ship_speed_factor = 4
        self.bullet_speed_factor = 10
        self.alien_speed_factor = 1
        self.alien_fire_rate = 3000
        self.alien_points = 50

    def increase_speed(self):
        """Increase speed settings and alien point values."""
        self.ship_speed_factor *= self.speedup_scale
        self.alien_speed_factor *= self.speedup_scale
        self.bullet_speed_factor *= 1.05
        self.alien_points *= self.score_scale
        self.alien_fire_scaling()

    def increase_alien_fire(self):
        if self.alien_fire_rate > 250:
            self.alien_fire_rate = int(self.alien_fire_rate * self.alien_fire_scale)

    def alien_fire_scaling(self):
        if self.alien_fire_rate > 2500:
            self.alien_fire_rate -= 2000
        elif self.alien_fire_rate > 1000:
            self.alien_fire_rate -= 500
        elif self.alien_fire_rate > 100:
            self.alien_fire_rate -= 20
        elif self.alien_fire_rate > 50:
            self.alien_fire_rate -= 5
        elif self.alien_fire_rate > 5 and self.alien_fire_rate > 1:
            self.alien_fire_rate -= 1

