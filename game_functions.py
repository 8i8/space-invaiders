import sys
import pygame
from pygame.sprite import Group
from random import randint
from time import sleep

from bullet import FriendlyBullet, AlienBullet
from alien import Alien
from block import Block

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Events
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def check_events(settings, stats, screen, sb, ship, alien_groups, bullets,
        blockade, play_button):
    """Respond to key presses and mouse events."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, settings, stats, screen, sb, ship,
                    alien_groups, bullets, blockade)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, settings, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(settings, stats, screen, sb, play_button, ship,
                              alien_groups, bullets, blockade, mouse_x, mouse_y)

def check_keydown_events(event, settings, stats, screen, sb, ship,
        alien_groups, bullets, blockade):
    """Respond to keypress events."""
    if event.key == pygame.K_LEFT:
        ship.moving_left = True
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    if event.key == pygame.K_SPACE:
        fire_bullet_ship(settings, screen, ship, bullets)
    if event.key == pygame.K_q:
        sys.exit()
    if event.key == pygame.K_r:
        settings.rapidfire = not settings.rapidfire
    if event.key == pygame.K_e:
        settings.powerbullets = not settings.powerbullets
    if event.key == pygame.K_w:
        settings.widebullets = not settings.widebullets
    if event.key == pygame.K_p:
        start_game(settings, stats, screen, sb, ship, alien_groups, bullets,
                       blockade)

def check_keyup_events(event, settings, ship):
    """Respond to key up event."""
    if event.key == pygame.K_LEFT:
        ship.moving_left = False
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Update
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def update_screen(settings, stats, screen, sb, ship, alien_groups, bullets,
                      blockade, play_button):
    """Update objects and flip the new screen."""
    # Redraw the screen during each pass through the loop.
    #screen.fill(settings.bg_colour)
    screen.blit(settings.bg_image, (0,0))
    # Draw bullets.
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    # Draw the ship.
    ship.blitme()
    # Draw aliens.
    for alien_column in alien_groups:
        alien_column.draw(screen)
    # Draw the defence.
    for block in blockade:
        block.draw_block()
    # Draw the score information.
    sb.show_score()
    # Draw the play button if the game is inactive.
    if not stats.game_active:
        play_button.draw_button()
    # Make the most recently drawn screen visible.
    pygame.display.flip()

def check_play_button(settings, stats, screen, sb, play_button, ship,
                    alien_groups, bullets, blockade, mouse_x, mouse_y):
    """Start new game when the player clicks play."""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        start_game(settings, stats, screen, sb, ship, alien_groups, bullets,
                       blockade)

def start_game(settings, stats, screen, sb, ship, alien_groups, bullets,
                   blockade):
    """Reset all dynamic variables, start a new game."""
    # Reset dynamic settings and statistics, generate prep renders
    settings.initialise_dynamic_settings()
    stats.reset_stats()
    prep_images(sb)

    # Clear old, create a new fleet, center the ship.
    for alien_column in alien_groups:
        alien_column.empty()
    bullets.empty()
    blockade.empty()
    create_fleet(settings, screen, ship, alien_groups)
    create_defence(settings, screen, blockade)
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

def check_bullet_alien_collision(settings, stats, screen, sb, ship,
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
        if settings.powerbullets == True:
            collisions = pygame.sprite.groupcollide(ships_fire, alien_column, False, True)
        else:
            collisions = pygame.sprite.groupcollide(ships_fire, alien_column, True, True)

        if collisions:
            for alien in collisions.values():
                stats.score += settings.alien_points * len(alien_column)
                sb.prep_score()
                settings.increase_alien_fire()
            check_high_score(stats, sb)

        # Define the front line for alien fire.
        define_frontline(alien_column)

    # If the entire fleet is destroyed, start a new level.
    count = 0
    for alien_column in alien_groups:
        count += len(alien_column)
    if count == 0:
        make_new_level(settings, stats, screen, sb, ship, alien_groups, bullets)

def make_new_level(settings, stats, screen, sb, ship, alien_groups, bullets):
    """Clear screen and set up next level."""
    # Destroy any existing bullets, speed up the game and create a new fleet.
    settings.increase_speed()
    stats.level += 1
    sb.prep_level()
    create_fleet(settings, screen, ship, alien_groups)

def check_bullet_ship_collision(settings, stats, screen, sb, ship,
                                alien_groups, bullets, blockade):
    """Check for collision between alien bullets and the ship."""

    alien_fire = Group()
    for bullet in bullets:
        if bullet.direction == 1:
            alien_fire.add(bullet)

    if pygame.sprite.spritecollideany(ship, alien_fire):
        ship_hit_bullet(settings, stats, screen, sb, ship, alien_groups,
                            bullets, blockade)

def check_alien_ship_collision(settings, stats, screen, sb, ship,
                               alien_groups, bullets, blockade):
    """Check for alien and ship collision."""
    for alien_column in alien_groups:
        if pygame.sprite.spritecollideany(ship, alien_column):
            ship_hit_alien(settings, stats, screen, sb, ship, alien_groups,
                               bullets, blockade)

def check_bullet_blockade_collision(bullets, blockade):
    """Has a shield been hit."""
    pygame.sprite.groupcollide(bullets, blockade, True, True)

def check_alien_blockade_collision(alien_groups, blockade):
    """check to see if any aliens have reached the blockade."""
    for alien_column in alien_groups:
        collision = pygame.sprite.groupcollide(alien_column, blockade, False, True)
        if collision:
            blockade.empty()
            break

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Ship
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def ship_hit_alien(settings, stats, screen, sb, ship, alien_groups, bullets,
                       blockade):
    """Respond to ship being hit by an alien."""
    # Ship lost or game over.
    stats.ships_left -= 1
    if stats.ships_left:
        ship_lost_new_fleet(settings, screen, sb, ship, alien_groups, bullets,
                                blockade)
    else:
        game_over(stats)

def ship_hit_bullet(settings, stats, screen, sb, ship, alien_groups, bullets,
                        blockade):
    """Respond to ship being hit by an alien."""
    # Ship lost or game over.
    stats.ships_left -= 1
    if stats.ships_left:
        ship_lost(settings, screen, sb, ship, alien_groups, bullets, blockade)
    else:
        game_over(stats)

def ship_lost_new_fleet(settings, screen, sb, ship, alien_groups, bullets,
                            blockade):
    """Ship lost on being hit by an alien, create a new fleet."""
    sb.prep_ships()
    for alien_column in alien_groups:
        alien_column.empty()
    create_fleet(settings, screen, ship, alien_groups)
    ship.center_ship()
    sleep(0.5)

def ship_lost(settings, screen, sb, ship, alien_groups, bullets, blockade):
    """Ship lost on being hit by an alien bullet."""
    sb.prep_ships()
    bullets.empty()
    sleep(0.5)

def game_over(stats):
    """Game over, ship lost and no lives left."""
    stats.game_active = False
    pygame.mouse.set_visible(True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Bullets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def fire_bullet_ship(settings, screen, ship, bullets):
    """Friendly fire."""

    # If there are fewer bullets on screen that the max amount.
    if settings.rapidfire == True:
        new_bullet = FriendlyBullet(settings, screen, ship)
        bullets.add(new_bullet)
        return

    bullet_count = 0
    for bullet in bullets.sprites():
        if bullet.direction == -1:
            bullet_count += 1

    if bullet_count < settings.bullets_allowd:
        # Create a new bullet and add it to the bullets group.
        new_bullet = FriendlyBullet(settings, screen, ship)
        bullets.add(new_bullet)


def fire_bullet_alien(settings, screen, alien, bullets):
    """Alien fire."""
    new_bullet = AlienBullet(settings, screen, alien)
    bullets.add(new_bullet)

def update_bullets(settings, stats, screen, sb, ship, alien_groups, bullets,
                       blockade):
    """Update position of bullets and get rid of old bullets."""
    # Update bullet positions
    bullets.update()

    # Remove any bullets that are off screen.
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0 or bullet.rect.top >= settings.screen_height:
            bullets.remove(bullet)

    check_bullet_alien_collision(settings, stats, screen, sb, ship,
                                    alien_groups, bullets)
    check_bullet_ship_collision(settings, stats, screen, sb, ship,
                                    alien_groups, bullets, blockade)
    check_bullet_blockade_collision(bullets, blockade)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Aliens
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def initialise_fleet(settings, screen, ship, alien_groups):
    """Create the pygame sprite groups for alien columns."""
    # Create one alien and then use it to reckon how many aliens can be
    # stored in a row with one aliens width between each.
    alien = Alien(settings, screen)
    number_columns = get_number_columns(settings, alien.rect.width)
    number_rows = get_number_rows(settings, ship.rect.height, alien.rect.height)
    settings.columns = number_columns - settings.alien_columns_removed
    settings.rows = number_rows

    for column_number in range(settings.columns):
        new_group = Group()
        alien_groups.append(new_group)

def create_fleet(settings, screen, ship, alien_groups):
    """Create a full fleet of aliens."""
    # Create one alien and then use it to reckon how many aliens can be
    # stored in a row with one aliens width between each.
    number_columns = settings.columns
    number_rows = settings.rows

    #for column_number in range(number_columns):
    for column_number, alien_column in enumerate(alien_groups):
        for row_number in range(number_rows):
            create_alien(settings, screen, alien_column, column_number,
                             row_number)

def get_number_columns(settings, alien_width):
    """Determine the number of aliens to fit the width."""
    available_space_x = settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 * alien_width))
    return number_aliens_x

def get_number_rows(settings, ship_height, alien_height):
    """Determine the number of alien rows that will fit on the screen."""
    available_space_y = (
            settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height)) / 2
    return int(number_rows / 1)

def create_alien(settings, screen, alien_column, alien_number, row_number):
    """Create and alien and set it in the column."""
    alien = Alien(settings, screen)
    alien_width = alien.rect.width
    alien.x = (alien_width + 2 * alien_width * alien_number +
            settings.shim_x)
    alien.rect.x = alien.x
    alien.rect.y = (alien.rect.height + 2 * alien.rect.height * row_number +
                    settings.shim_y)
    # Row number designates the front line of the enemy, for enemy fire.
    alien.row = row_number
    alien_column.add(alien)

def check_fleet_edges(settings, alien_groups):
    """Respond appropriately if any aliens have reached an edge."""
    for alien_column in alien_groups:
        for alien in alien_column.sprites():
            if alien.check_edges():
                change_fleet_direction(settings, alien_groups)
                break

def change_fleet_direction(settings, alien_groups):
    """Drop the entire fleet and change the fleet's direction."""
    for alien_column in alien_groups:
        for alien in alien_column.sprites():
            alien.rect.y += settings.fleet_drop_speed
        settings.fleet_direction *= -1

def check_aliens_bottom(settings, stats, screen, sb, ship, alien_groups,
                            bullets, blockade):
    """Check if any aliens have reached the bottom of the screen."""
    screen_rect = screen.get_rect()
    for alien_column in alien_groups:
        for alien in alien_column.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat the same as the ship being hit.
                ship_lost(settings, stats, screen, sb, ship, alien_groups,
                              bullets, blockade)

def update_aliens(settings, stats, screen, sb, ship, alien_groups, bullets,
                      blockade):
    """
    Check if the fleet is at an edge, and then update the positions of all
    aliens in the fleet.
    """

    for alien_column in alien_groups:
        alien_column.update()

    check_fleet_edges(settings, alien_groups)
    check_alien_ship_collision(settings, stats, screen, sb, ship,
                               alien_groups, bullets, blockade)
    check_aliens_bottom(settings, stats, screen, sb, ship, alien_groups,
                            bullets, blockade)
    check_alien_blockade_collision(alien_groups, blockade)
    generate_alien_fire(settings, screen, sb, alien_groups, bullets)

def define_frontline(alien_column):
    """Define which aliens should fire back, tag the lowermost alien in each
    column by getting the count of aliens and then looking for that number."""
    if len(alien_column):
        front_line = max(alien.row for alien in alien_column.sprites())
        for alien in alien_column.sprites():
            if alien.row == front_line:
                alien.front_line = True

def generate_alien_fire(settings, screen, sb, alien_groups, bullets):
    """Generate frontline alien fire."""
    # Set the scaling of the random number generation, thus the rate of enemy
    # fire.
    if settings.debug:
        sb.prep_fire_rate(settings.alien_fire_rate)
    # Iterate over all aliens, if in the frontline, then randomly test to see
    # if the alien should fire.
    for alien_column in alien_groups:
        for alien in alien_column:
            if alien.front_line:
                if randint(0, settings.alien_fire_rate) == 0:
                    fire_bullet_alien(settings, screen, alien, bullets)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Blockade
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def create_defence(settings, screen, blockade):
    """Build blockade."""

    rows = [
        (0,0,1,1,1,1,1,1,1,0,0),
        (0,0,1,1,1,1,1,1,1,0,0),
        (0,1,1,1,1,1,1,1,1,1,0),
        (0,1,1,1,1,1,1,1,1,1,0),
        (1,1,1,1,1,1,1,1,1,1,1),
        (1,1,1,1,1,1,1,1,1,1,1),
        (1,1,1,1,1,1,1,1,1,1,1),
        (1,1,1,1,1,1,1,1,1,1,1),
        (1,1,1,1,1,1,1,1,1,1,1),
        (1,1,1,0,0,0,0,0,1,1,1)]

    blockade_w = len(rows[0]) * settings.block_width
    blocks = (settings.screen_width - 2 * blockade_w) / (blockade_w * 3)
    spacer = (settings.screen_width - (blocks * (blockade_w * 3) - 2 * blockade_w)) / 2

    for block in range(0,blocks):
        create_shield(settings, screen, blockade, rows, spacer +
                         3*block*blockade_w, settings.screen_height - 175)

def create_shield(settings, screen, blockade, rows, x, y):
    """Build a block."""
    width = settings.block_width
    height = settings.block_height


    for i, row in enumerate(rows):
        for j, block in enumerate(row):
            if block:
                blockade.add(Block(settings, screen, x+j*width, y+i*height))

