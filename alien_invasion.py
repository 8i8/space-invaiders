#!/bin/env python3
import pdb
import pygame
from pygame.sprite import Group

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from alien import Alien

import game_functions as gf

def run_game():
    # Initialise pygame, settings and screen object.
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode(
            (ai_settings.screen_width, ai_settings.screen_hight))
    pygame.display.set_caption('Alien Invasion')

    # Make play button, stats and scoreboard.
    play_button = Button(ai_settings, screen, 'Play')
    stats = GameStats(ai_settings)
    sb = Scoreboard(ai_settings, screen, stats)

    # Make a ship a group of bullets and a group of aliens.
    ship = Ship(ai_settings, screen)
    bullets = Group()
    alien_groups = []

    # Create an alien fleet.
    gf.initialise_fleet(ai_settings, screen, ship, alien_groups)
    gf.create_fleet(ai_settings, screen, ship, alien_groups)

    # Start the main loop of the game.
    while True:
        gf.check_events(ai_settings, stats, screen, sb, ship, alien_groups, bullets, play_button)

        if stats.game_active:
            ship.update()
            gf.update_bullets(ai_settings, stats, screen, sb, ship, alien_groups, bullets)
            gf.update_aliens(ai_settings, stats, screen, sb, ship, alien_groups, bullets)

        gf.update_screen(ai_settings, stats, screen, sb, ship, alien_groups, bullets, play_button)

run_game()
