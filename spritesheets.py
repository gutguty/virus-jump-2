# ── spritesheets.py ──────────────────────────────────────────
import pygame
from settings import spritesheet_file_name, black

class SpriteSheet:
    def __init__(self):
        self.spritesheet = pygame.image.load(spritesheet_file_name).convert()

    def imageLoad(self, x, y, width, height, scale=3):
        """Вырезает спрайт из листа и масштабирует (делит на scale)."""
        image = pygame.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (width // scale, height // scale))
        return image
