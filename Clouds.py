# ── Clouds.py ─────────────────────────────────────────────────
import pygame
from settings import black, cloud_layer, display_width, display_height
from random import choice, randrange

class Cloud(pygame.sprite.Sprite):
    def __init__(self, game):
        self._layer = cloud_layer
        self.groups = game.all_sprites, game.clouds
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game  = game
        self.image = choice(self.game.cloud_images).copy()
        self.image.set_colorkey(black)
        scale = randrange(50, 101) / 100
        w = int(self.image.get_width()  * scale)
        h = int(self.image.get_height() * scale)
        self.image = pygame.transform.scale(self.image, (w, h))
        self.rect  = self.image.get_rect()
        self.rect.x = randrange(0, display_width - self.rect.width)
        self.rect.y = randrange(-500, -50)

    def update(self):
        if self.rect.top > display_height * 2:
            self.kill()
