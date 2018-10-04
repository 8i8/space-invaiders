import sys
import pygame
from pygame.sprite import Group
from time import sleep

from bullet import FriendlyBullet, AlienBullet
from alien import Alien

def print_aliens(aliens):
    for group in aliens:
        print(group)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Events  
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def check_events(ai_settings, stats, screen, sb, ship, aliens, bullets, play_button):
    """Respond to key presses and mouse events."""
    # Watch for keyboard and mouse events.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, stats, screen, sb, ship, aliens, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ai_settings, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, stats, screen, sb, play_button, ship,
                    aliens, bullets, mouse_x, mouse_y)

def check_keydown_events(event, ai_settings, stats, screen, sb, ship, aliens, bullets):
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
        start_game(ai_settings, stats, screen, sb, ship, aliens, bullets)

def check_keyup_events(event, ai_settings, ship):
    """Respond to key up event."""
    if event.key == pygame.K_LEFT:
        ship.moving_left = False
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Update 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def update_screen(ai_settings, stats, screen, sb, ship, aliens, bullets, play_button):
    """Update objects and flip the new screen."""
    # Redraw the screen during each pass through the loop.
    screen.fill(ai_settings.bg_colour)
    # Draw bullets.
    generate_alien_fire(ai_settings, screen, aliens, bullets)
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    # Draw the ship.
    ship.blitme()
    # Draw aliens.
    for groups in aliens:
        groups.draw(screen)
    # Draw the score information.
    sb.show_score()
    # Draw the play button if the game is inactive.
    if not stats.game_active:
        play_button.draw_button()
    # Make the most recently drawn screen visible.
    pygame.display.flip()

def check_play_button(ai_settings, stats, screen, sb, play_button, ship,
                    aliens, bullets, mouse_x, mouse_y):
    """Start new game when the player clicks play."""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        start_game(ai_settings, stats, screen, sb, ship, aliens, bullets)

def start_game(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Reset all dynamic variables, start a new game."""
    # Reset dynamic settings and statistics, generate prep renders
    ai_settings.initialise_dynamic_settings()
    stats.reset_stats()
    prep_images(sb)

    # Clear old, create a new fleet, center the ship.
    ship.center_ship()
    for group in aliens:
        group.empty()
    bullets.empty()
    create_fleet(ai_settings, screen, ship, aliens)

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

def check_bullet_alien_collision(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Check collisions and remove any aliens that have been hit, under
    standard operation remove also the bullets."""

    # Check if any bullets have hit aliens, remove alien if hit, dependant on
    # game settings remove bullets.
    if ai_settings.powerbullets == True:
        collisions = pygame.sprite.groupcollide(bullets, aliens, False, True)
    else:
        collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)
    
    # Define the front line for alien fire.
    define_frontline(aliens)

    # If the entire fleet is destroyed, start a new level.
    if len(aliens) == 0:
        make_new_level(ai_settings, stats, screen, sb, ship, aliens, bullets)

def make_new_level(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Clear screen and set up next level."""
    # Destroy any existing bullets, speed up the game and create a new fleet.
    bullets.empty()
    ai_settings.increase_speed()
    stats.level += 1
    sb.prep_level()
    create_fleet(ai_settings, screen, ship, aliens)

def check_alien_ship_collision(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Check for alien and ship collision."""
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Ship
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Respond to ship being hit by an alien."""
    # Ship lost or game over.
    stats.ships_left -= 1
    if stats.ships_left:
        ship_lost(ai_settings, screen, sb, ship, aliens, bullets)
    else:
        game_over(stats)

def ship_lost(ai_settings, screen, sb, ship, aliens, bullets):
    """Ship lost on being hit."""
    sb.prep_ships()
    aliens.empty()
    bullets.empty()
    create_fleet(ai_settings, screen, ship, aliens)
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
    elif len(bullets) < ai_settings.bullets_allowd:
        # Create a new bullet and add it to the bullets group.
        new_bullet = FriendlyBullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def fire_bullet_alien(ai_settings, screen, alien, bullets):
    """Alien fire."""
    new_bullet = AlienBullet(ai_settings, screen, alien)
    bullets.add(new_bullet)

def update_bullets(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Update position of bullets and get rid of old bullets."""
    # Update bullet positions
    bullets.update()

    # Remove any bullets that are off screen.
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collision(ai_settings, stats, screen, sb, ship, aliens, bullets)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Aliens  
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def create_fleet(ai_settings, screen, ship, aliens):
    """Create a full fleet of aliens."""
    # Create one alien and then use it to reckon how many aliens can be
    # stored in a row with one aliens width between each.
    alien = Alien(ai_settings, screen)
    number_columns = get_number_columns(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)
    ai_settings.columns = number_columns

    for column_number in range(number_columns):
        new_group = Group()
        for row_number in range(number_rows):
            create_alien(ai_settings, screen, new_group, column_number, row_number)
        aliens.append(new_group)
    return aliens

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

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Create and alien and set it in the row."""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = (alien_width + 2 * alien_width * alien_number +
            ai_settings.shim_h)
    alien.rect.x = alien.x
    alien.rect.y = (alien.rect.height + 2 * alien.rect.height * row_number +
            ai_settings.shim_top)
    alien.row = row_number
    aliens.add(alien)

def check_fleet_edges(ai_settings, aliens):
    """Respond appropriately if any aliens have reached an edge."""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break

def change_fleet_direction(ai_settings, aliens):
    """Drop the entire fleet and change the fleet's direction."""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1

def check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """Check if any aliens have reached the bottom of the screen."""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Treat the same as the ship being hit.
            ship_hit(ai_settings, stats, screen, sb, ship, aliens, bullets)

def update_aliens(ai_settings, stats, screen, sb, ship, aliens, bullets):
    """
    Check if the fleet is at an edge, and then update the positions of all
    aliens in the fleet.
    """
    check_fleet_edges(ai_settings, aliens)
    for group in aliens:
        group.update()

    # Get rid of aliens that are off screen, remove this code when the game
    # ends on reaching the rocket.
    for group in aliens:
        for alien in group.copy():
            if alien.rect.top > ai_settings.screen_hight:
                aliens.remove(alien)

    check_alien_ship_collision(ai_settings, stats, screen, sb, ship, aliens, bullets)
    check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets)

def define_frontline(aliens):
    """Define which aliens should fire back."""
    #TODO NOW sprite group empty.
    for group in aliens:
        alien_column = group.sprites()
        alien = max(alien.row for alien in alien_column)
        alien.front_line = True

def generate_alien_fire(ai_settings, screen, aliens, bullets):
    """Generate frontline alien fire."""
    for groups in aliens:
        for alien in groups:
            if alien.front_line:
                fire_bullet_alien(ai_settings, screen, alien, bullets)

