# ── powerup.py ───────────────────────────────────────────────
import pygame
from settings import black
from spritesheets import SpriteSheet

class PowerUps(pygame.sprite.Sprite):
    def __init__(self, platform, game):
        self.groups = game.powerups
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game  = game
        self.plat  = platform
        ss         = SpriteSheet()
        self.image = ss.imageLoad(563, 1843, 133, 160)
        self.image.set_colorkey(black)
        self.rect  = self.image.get_rect()
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom   = self.plat.rect.top - 5

    def update(self):
        # следуем за платформой
        self.rect.centerx = self.plat.rect.centerx
        self.rect.bottom   = self.plat.rect.top - 5
        # убираемся если платформа ушла
        if not self.game.platforms.has(self.plat):
            self.kill()
