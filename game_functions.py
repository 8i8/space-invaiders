import sys
import pygame
from pygame.sprite import Group
from random import randint
from time import sleep

from bullet import FriendlyBullet, AlienBullet
from alien import Alien

def print_aliens(aliens):
    for group in aliens:
        print(group)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Events  
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def check_events(ai_settings, stats, screen, sb, ship, alien_groups, bullets,
        play_button):
    """Respond to key presses and mouse events."""
    # Watch for keyboard and mouse events.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, stats, screen, sb, ship,
                    alien_groups, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ai_settings, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, stats, screen, sb, play_button, ship,
                    alien_groups, bullets, mouse_x, mouse_y)

def check_keydown_events(event, ai_settings, stats, screen, sb, ship,
        alien_groups, bullets):
    """Respond to keypress."""
    if event.key == pygame.K_LEFT:
        ship.moving_left = True
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    if event.key == pygame.K_SPACE:
        fire_bullet_ship(ai_settings, screen, ship, bullets)
    if event.key == pygame.K_q:
        sys.exit()
    if event.key == pygame.K_r:
        ai_settings.rapidfire = not ai_settings.rapidfire
    if event.key == pygame.K_e:
        ai_settings.powerbullets = not ai_settings.powerbullets
    if event.key == pygame.K_w:
        ai_settings.widebullets = not ai_settings.widebullets
    if event.key == pygame.K_p:
        start_game(ai_settings, stats, screen, sb, ship, alien_groups, bullets)

def check_keyup_events(event, ai_settings, ship):
    """Respond to key up event."""
    if event.key == pygame.K_LEFT:
        ship.moving_left = False
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Update 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def update_screen(ai_settings, stats, screen, sb, ship, alien_groups, bullets, play_button):
    """Update objects and flip the new screen."""
    # Redraw the screen during each pass through the loop.
    screen.fill(ai_settings.bg_colour)
    # Draw bullets.
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    # Draw the ship.
    ship.blitme()
    # Draw aliens.
    for alien_column in alien_groups:
        alien_column.draw(screen)
    # Draw the score information.
    sb.show_score()
    # Draw the play button if the game is inactive.
    if not stats.game_active:
        play_button.draw_button()
    # Make the most recently drawn screen visible.
    pygame.display.flip()

def check_play_button(ai_settings, stats, screen, sb, play_button, ship,
                    alien_groups, bullets, mouse_x, mouse_y):
    """Start new game when the player clicks play."""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        start_game(ai_settings, stats, screen, sb, ship, alien_groups, bullets)

def start_game(ai_settings, stats, screen, sb, ship, alien_groups, bullets):
    """Reset all dynamic variables, start a new game."""
    # Reset dynamic settings and statistics, generate prep renders
    ai_settings.initialise_dynamic_settings()
    stats.reset_stats()
    prep_images(sb)

    # Clear old, create a new fleet, center the ship.
    for alien_column in alien_groups:
        alien_column.empty()
    bullets.empty()
    create_fleet(ai_settings, screen, ship, alien_groups)
    ship.center_ship()

    # Activate the game, hide the mouse cursor.
    stats.game_active = True
    pygame.mouse.set_visible(False)

def prep_images(sb):
    """Generate all required text renders for new game."""
    # Reset scoreboard images.
    sb.prep_score()
    sb.prep_high_score()
    sb.prep_level()
    sb.prep_ships()

def check_high_score(stats, sb):
    """Check to see if there is a new high score."""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()
        stats.write_high_score()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Collisions  
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def check_bullet_alien_collision(ai_settings, stats, screen, sb, ship,
        alien_groups, bullets):
    """Check collisions and remove any aliens that have been hit, under
    standard operation remove also the bullets."""

    ships_fire = Group()
    for bullet in bullets:
        if bullet.direction == -1:
            ships_fire.add(bullet)

    # Check if any bullets have hit aliens, remove alien if hit, dependant on
    # game settings remove bullets.
    for alien_column in alien_groups:
        if ai_settings.powerbullets == True:
            collisions = pygame.sprite.groupcollide(ships_fire, alien_column, False, True)
        else:
            collisions = pygame.sprite.groupcollide(ships_fire, alien_column, True, True)

        if collisions:
            for alien in collisions.values():
                stats.score += ai_settings.alien_points * len(alien_column)
                sb.prep_score()
            check_high_score(stats, sb)
    
        # Define the front line for alien fire.
        define_frontline(alien_column)

    # If the entire fleet is destroyed, start a new level.
    count = 0
    for alien_column in alien_groups:
        count += len(alien_column)
    if count == 0:
        make_new_level(ai_settings, stats, screen, sb, ship, alien_groups, bullets)

def make_new_level(ai_settings, stats, screen, sb, ship, alien_groups, bullets):
    """Clear screen and set up next level."""
    # Destroy any existing bullets, speed up the game and create a new fleet.
    bullets.empty()
    ai_settings.increase_speed()
    stats.level += 1
    sb.prep_level()
    create_fleet(ai_settings, screen, ship, alien_groups)

def check_bullet_ship_collision(ai_settings, stats, screen, sb, ship,
        alien_groups, bullets):
    """Check for collision between alien bullets and the ship."""

    alien_fire = Group()
    for bullet in bullets:
        if bullet.direction == 1:
            alien_fire.add(bullet)

    if pygame.sprite.spritecollideany(ship, alien_fire):
        ship_hit(ai_settings, stats, screen, sb, ship, alien_groups, bullets)

def check_alien_ship_collision(ai_settings, stats, screen, sb, ship,
        alien_groups, bullets):
    """Check for alien and ship collision."""
    for alien_column in alien_groups:
        if pygame.sprite.spritecollideany(ship, alien_column):
            ship_hit(ai_settings, stats, screen, sb, ship, alien_groups, bullets)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Ship
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def ship_hit(ai_settings, stats, screen, sb, ship, alien_groups, bullets):
    """Respond to ship being hit by an alien."""
    # Ship lost or game over.
    stats.ships_left -= 1
    if stats.ships_left:
        ship_lost(ai_settings, screen, sb, ship, alien_groups, bullets)
    else:
        game_over(stats)

def ship_lost(ai_settings, screen, sb, ship, alien_groups, bullets):
    """Ship lost on being hit."""
    sb.prep_ships()
    for alien_column in alien_groups:
        alien_column.empty()
    bullets.empty()
    create_fleet(ai_settings, screen, ship, alien_groups)
    ship.center_ship()
    sleep(0.5)

def game_over(stats):
    """Game over, ship lost and no lives left."""
    stats.game_active = False
    pygame.mouse.set_visible(True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Bullets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def fire_bullet_ship(ai_settings, screen, ship, bullets):
    """Friendly fire."""

    # If there are fewer bullets on screen that the max amount.
    if ai_settings.rapidfire == True:
        new_bullet = FriendlyBullet(ai_settings, screen, ship)
        bullets.add(new_bullet)
        return

    bullet_count = 0
    for bullet in bullets.sprites():
        if bullet.direction == -1:
            bullet_count += 1

    if bullet_count < ai_settings.bullets_allowd:
        # Create a new bullet and add it to the bullets group.
        new_bullet = FriendlyBullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def fire_bullet_alien(ai_settings, screen, alien, bullets):
    """Alien fire."""
    new_bullet = AlienBullet(ai_settings, screen, alien)
    bullets.add(new_bullet)

def update_bullets(ai_settings, stats, screen, sb, ship, alien_groups, bullets):
    """Update position of bullets and get rid of old bullets."""
    # Update bullet positions
    bullets.update()

    # Remove any bullets that are off screen.
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0 or bullet.rect.top >= ai_settings.screen_hight:
            bullets.remove(bullet)

    check_bullet_alien_collision(ai_settings, stats, screen, sb, ship,
            alien_groups, bullets)
    check_bullet_ship_collision(ai_settings, stats, screen, sb, ship,
            alien_groups, bullets)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Aliens  
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def initialise_fleet(ai_settings, screen, ship, alien_groups):
    """Create the pygame sprite groups for alien columns."""
    # Create one alien and then use it to reckon how many aliens can be
    # stored in a row with one aliens width between each.
    alien = Alien(ai_settings, screen)
    number_columns = get_number_columns(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)
    ai_settings.columns = number_columns
    ai_settings.rows = number_rows

    for column_number in range(number_columns):
        new_group = Group()
        alien_groups.append(new_group)

def create_fleet(ai_settings, screen, ship, alien_groups):
    """Create a full fleet of aliens."""
    # Create one alien and then use it to reckon how many aliens can be
    # stored in a row with one aliens width between each.
    number_columns = ai_settings.columns
    number_rows = ai_settings.rows

    #for column_number in range(number_columns):
    for column_number, alien_column in enumerate(alien_groups):
        for row_number in range(number_rows):
            create_alien(ai_settings, screen, alien_column, column_number, row_number)

def get_number_columns(ai_settings, alien_width):
    """Determine the number of aliens to fit the width."""
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x

def get_number_rows(ai_settings, ship_hight, alien_height):
    """Determine the number of alien rows that will fit on the screen."""
    available_space_y = (
            ai_settings.screen_hight - (3 * alien_height) - ship_hight)
    number_rows = int(available_space_y / (2 * alien_height)) / 2
    return int(number_rows / 1)

def create_alien(ai_settings, screen, alien_column, alien_number, row_number):
    """Create and alien and set it in the column."""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = (alien_width + 2 * alien_width * alien_number +
            ai_settings.shim_h)
    alien.rect.x = alien.x
    alien.rect.y = (alien.rect.height + 2 * alien.rect.height * row_number +
            ai_settings.shim_top)
    # Row number designates the front line of the enemy, for enemy fire.
    alien.row = row_number
    alien_column.add(alien)

def check_fleet_edges(ai_settings, alien_groups):
    """Respond appropriately if any aliens have reached an edge."""
    for alien_column in alien_groups:
        for alien in alien_column.sprites():
            if alien.check_edges():
                change_fleet_direction(ai_settings, alien_groups)
                break

def change_fleet_direction(ai_settings, alien_groups):
    """Drop the entire fleet and change the fleet's direction."""
    for alien_column in alien_groups:
        for alien in alien_column.sprites():
            alien.rect.y += ai_settings.fleet_drop_speed
        ai_settings.fleet_direction *= -1

def check_aliens_bottom(ai_settings, stats, screen, sb, ship, alien_groups, bullets):
    """Check if any aliens have reached the bottom of the screen."""
    screen_rect = screen.get_rect()
    for alien_column in alien_groups:
        for alien in alien_column.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat the same as the ship being hit.
                ship_hit(ai_settings, stats, screen, sb, ship, alien_groups, bullets)

def update_aliens(ai_settings, stats, screen, sb, ship, alien_groups, bullets):
    """
    Check if the fleet is at an edge, and then update the positions of all
    aliens in the fleet.
    """

    for alien_column in alien_groups:
        alien_column.update()

    check_fleet_edges(ai_settings, alien_groups)
    check_alien_ship_collision(ai_settings, stats, screen, sb, ship,
            alien_groups, bullets)
    check_aliens_bottom(ai_settings, stats, screen, sb, ship, alien_groups, bullets)
    generate_alien_fire(ai_settings, screen, alien_groups, bullets)

def define_frontline(alien_column):
    """Define which aliens should fire back."""
    if len(alien_column):
        front_line = max(alien.row for alien in alien_column.sprites())
        for alien in alien_column.sprites():
            if alien.row == front_line:
                alien.front_line = True

def generate_alien_fire(ai_settings, screen, alien_groups, bullets):
    """Generate frontline alien fire."""
    for alien_column in alien_groups:
        for alien in alien_column:
            if alien.front_line:
                if randint(0, ai_settings.alien_fire_rate * 1000) == 0:
                    fire_bullet_alien(ai_settings, screen, alien, bullets)

