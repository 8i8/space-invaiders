class GameStats():
    """Track statistics for Alien Invasion."""
    def __init__(self, settings):
        """Initialise statistics."""
        self.settings = settings
        self.reset_stats()
        self.score = 0
        self.high_score = 0

        # Start the game in an inactive state.
        self.game_active = False

        # Retrieve highest score.
        self.read_high_score()

    def reset_stats(self):
        """Initialise statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def write_high_score(self):
        """Store highest score to file."""
        with open('.highscore', 'w') as file_object:
            file_object.write(str(self.high_score))

    def read_high_score(self):
        """Retrieve the highest score from file."""
        try:
            with open('.highscore', 'r') as file_object:
                self.high_score = int(file_object.read())
        except:
            pass
