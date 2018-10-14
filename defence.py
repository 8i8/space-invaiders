class Defence():
    """Blockade to stop the aliens."""
    def __init__(self, ai_settings, screen):
        self.settings = ai_settings
        self.screen = screen

        # Create a rectamgle as the basic defence.
        self.rect = pygame.Rect(0, 0, 15, 9)

        self.colour = (80, 50, 50)

