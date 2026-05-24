# ── lowPlatform.py ────────────────────────────────────────────
import pygame
from settings import green

class lowPlatform(pygame.sprite.Sprite):
    """Стартовая платформа на дне экрана."""
    def __init__(self, x, y, w, h):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((w, h))
        self.image.fill(green)
        self.rect  = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
