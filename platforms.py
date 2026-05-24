# ── platforms.py ─────────────────────────────────────────────
import pygame
from settings import *
from spritesheets import SpriteSheet
from random import choice, randrange

class Platform(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game

    def getPlatform(self, x, y, images):
        self.image = choice(images).copy()
        self.image.set_colorkey(black)
        self.rect  = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # спавн пауэр-апа
        if randrange(100) < power_up_spawn_freq:
            from powerup import PowerUps
            PowerUps(self, self.game)

    def getImages(self):
        ss = SpriteSheet()
        images = [
            ss.imageLoad(0,   768,  380, 94),
            ss.imageLoad(213, 1662, 201, 100),
        ]
        for img in images:
            img.set_colorkey(black)
        return images
