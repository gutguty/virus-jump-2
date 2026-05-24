# ── enemies.py ───────────────────────────────────────────────
import pygame
import random
from settings import *
from spritesheets import SpriteSheet

# Словарь мобов: {номер: [[x,y,w,h] up, [x,y,w,h] down, 'text_img']}
dic_mobs = {
    1: [[566, 510, 122, 139], [568, 1543, 122, 135], 'text1.png'],
    2: [[400, 510, 122, 139], [400,  660, 122, 100], 'text2.png'],
    3: [[805, 615, 120, 130], [800,  862, 120, 130], 'text3.png'],
    4: [[420,1684, 150, 150], [412, 1885, 150, 150], 'text4.png'],
    5: [[740,1083, 100, 125], [708, 1264, 100, 138], 'text5.png'],
    6: [[ 46,1463, 120,  91], [ 32, 1560, 110,  90], 'text6.png'],
    7: [[419,1541, 140,  85], [419, 1541, 140,  85], 'text7.png'],
}

class Enemies(pygame.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        n = random.randint(1, 7)
        self.enemyNum_ = n

        ss = SpriteSheet()
        d  = dic_mobs[n]

        self.image_up = ss.imageLoad(*d[0])
        self.image_up.set_colorkey(black)

        self.image_down = ss.imageLoad(*d[1])
        self.image_down.set_colorkey(black)

        self.image = self.image_up
        self.rect  = self.image.get_rect()
        self.mask  = pygame.mask.from_surface(self.image)

        # спавним с левого или правого края
        if random.random() < 0.5:
            self.rect.centerx = -60
            self.vx = random.uniform(1.5, 3.0)
        else:
            self.rect.centerx = display_width + 60
            self.vx = -random.uniform(1.5, 3.0)

        self.rect.y = random.randint(0, display_height // 2)
        self.vy = 0
        self.dy = random.uniform(0.03, 0.07)   # скорость боббинга
        self._bob_amp = random.uniform(0.4, 0.8)

    def update(self):
        self.rect.x += self.vx
        self.vy += self.dy
        if abs(self.vy) > 1.2:
            self.dy = -self.dy
        self.rect.y += self.vy

        center = self.rect.center
        if self.dy < 0:
            self.image = self.image_up
        else:
            self.image = self.image_down
        self.rect      = self.image.get_rect()
        self.rect.center = center
        self.mask      = pygame.mask.from_surface(self.image)

        # убиваем если вышел за экран
        if self.rect.left > display_width + 100 or self.rect.right < -100:
            self.kill()
