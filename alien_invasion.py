import pygame
from pygame.sprite import Group

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from alien import Alien

import game_functions as gf # The principle functions that run the game.

def run_game():
    # Initialise pygame, settings and screen object.
    pygame.init()
    clock = pygame.time.Clock()
    # Initialise the games start state includes screen dimensions for the
    # pygame display.
    settings = Settings()
    screen = pygame.display.set_mode(
            (settings.screen_width, settings.screen_height))
    pygame.display.set_caption('Alien Invasion')

    # Make play button, stats and scoreboard.
    play_button = Button(settings, screen, 'Play')
    stats = GameStats(settings)
    sb = Scoreboard(settings, screen, stats)

    # Make a ship, a group of bullets and a swarm of aliens.
    ship = Ship(settings, screen)
    bullets = Group()
    blockade = Group()
    alien_groups = []

    # Create an alien fleet and defences.
    gf.initialise_fleet(settings, screen, ship, alien_groups)
    gf.create_fleet(settings, screen, ship, alien_groups)
    gf.create_defence(settings, screen, blockade)

    # Start the main game loop.
    while True:
        clock.tick(60)
        gf.check_events(settings, stats, screen, sb, ship, alien_groups,
                            bullets, blockade, play_button)

        if stats.game_active:
            ship.update()
            gf.update_bullets(settings, stats, screen, sb, ship, alien_groups,
                                  bullets, blockade)
            gf.update_aliens(settings, stats, screen, sb, ship, alien_groups,
                                 bullets, blockade)

        gf.update_screen(settings, stats, screen, sb, ship, alien_groups,
                             bullets, blockade, play_button)

run_game()
