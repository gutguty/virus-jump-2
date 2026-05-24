# ═══════════════════════════════════════════════════════════════
#  VirusJump v3  —  космический стиль, процедурная графика
#  Запуск:  python main.py
# ═══════════════════════════════════════════════════════════════
import pygame, sys, math, random
from os import path
from settings import *
from draw_utils import (Background, draw_cloud, draw_platform,
                        draw_hero, VIRUS_KEYS, draw_virus,
                        get_virus_info, glow_circle)

vec = pygame.math.Vector2

# ───────────────────────────────────────────────────────────────
#  Утилиты
# ───────────────────────────────────────────────────────────────
def draw_text(surf, text, size, color, x, y, font_name=None, shadow=True):
    font = pygame.font.Font(font_name, size)
    if shadow:
        sh = font.render(text, True, (0,0,0))
        surf.blit(sh, sh.get_rect(midtop=(x+2, y+2)))
    ts = font.render(text, True, color)
    surf.blit(ts, ts.get_rect(midtop=(x, y)))

def draw_multiline(surf, text, size, color, x, y, font_name=None, line_h=None):
    font = pygame.font.Font(font_name, size)
    lh   = line_h or size + 4
    for i, line in enumerate(text.split('\n')):
        ts = font.render(line, True, color)
        surf.blit(ts, ts.get_rect(midtop=(x, y + i*lh)))

# ───────────────────────────────────────────────────────────────
#  Частица
# ───────────────────────────────────────────────────────────────
class Particle:
    __slots__ = ('x','y','vx','vy','r','color','life','decay')
    def __init__(self, x, y, color=(0,180,255)):
        self.x = float(x); self.y = float(y)
        self.vx = random.uniform(-3,3)
        self.vy = random.uniform(-4,-0.5)
        self.r  = random.randint(2,5)
        self.color = color
        self.life  = 1.0
        self.decay = random.uniform(0.03,0.07)
    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += 0.12; self.life -= self.decay
    def draw(self, surf):
        if self.life <= 0: return
        a = max(0, int(self.life*255))
        s = pygame.Surface((self.r*2+2, self.r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a), (self.r+1,self.r+1), self.r)
        surf.blit(s, (int(self.x)-self.r-1, int(self.y)-self.r-1))

# ───────────────────────────────────────────────────────────────
#  Всплывающий текст
# ───────────────────────────────────────────────────────────────
class FloatingText:
    def __init__(self, x, y, text, color=(255,220,0), size=22):
        self.x=x; self.y=float(y); self.text=text
        self.color=color; self.size=size; self.life=1.0
    def update(self): self.y -= 1.1; self.life -= 0.022
    def draw(self, surf, font):
        if self.life<=0: return
        a = max(0, int(self.life*255))
        ts = font.render(self.text, True, self.color)
        ts.set_alpha(a)
        surf.blit(ts, ts.get_rect(center=(self.x, int(self.y))))

# ───────────────────────────────────────────────────────────────
#  Панель определения вируса (показывается при встрече)
# ───────────────────────────────────────────────────────────────
class VirusPanel:
    """Ненавязчивая всплывающая плашка снизу экрана."""
    SHOW_MS = 4500   # сколько показывать

    def __init__(self, key, won):
        info       = get_virus_info(key)
        self.title = info['title']
        self.desc  = info['desc']
        self.color = info['color']
        self.glow  = info['glow']
        self.won   = won
        self.key   = key
        self.start = pygame.time.get_ticks()
        self.h     = 110
        # для анимации
        self.slide = float(self.h)   # начинает снизу

    @property
    def alive(self):
        return pygame.time.get_ticks() - self.start < self.SHOW_MS

    def update(self):
        elapsed = pygame.time.get_ticks() - self.start
        # slide in
        self.slide = max(0.0, self.slide - 6)
        # fade out в последние 800 мс
        remaining = self.SHOW_MS - elapsed
        if remaining < 800:
            self.alpha = max(0, int(255 * remaining / 800))
        else:
            self.alpha = 255

    def draw(self, surf, t):
        w = display_width
        panel_y = display_height - self.h + int(self.slide)
        s = pygame.Surface((w, self.h), pygame.SRCALPHA)

        # фон плашки
        for i in range(self.h):
            fade = 1 - i/self.h
            a    = int(200 * fade * fade)
            pygame.draw.line(s, (*COL_BG2, a), (0,i),(w,i))

        # верхняя неоновая линия
        line_col = self.glow
        pygame.draw.line(s, (*line_col, 200), (0,0),(w,0), 2)

        # иконка вируса (маленькая)
        draw_virus(s, self.key, 32, 44, t, t*0.001, size=0.7)

        # статус
        status_col = (80,255,120) if self.won else (255,80,80)
        status_txt = '✓ УНИЧТОЖЕН' if self.won else '✗ ЗАРАЖЁН'
        f1 = pygame.font.SysFont(None, 20)
        lbl = f1.render(status_txt, True, status_col)
        s.blit(lbl, (70, 6))

        # название
        f2 = pygame.font.SysFont(None, 26)
        title_lbl = f2.render(self.title, True, line_col)
        s.blit(title_lbl, (70, 24))

        # описание
        f3 = pygame.font.SysFont(None, 19)
        for i, line in enumerate(self.desc.split('\n')):
            dl = f3.render(line, True, (180,210,255))
            s.blit(dl, (70, 50 + i*18))

        s.set_alpha(self.alpha)
        surf.blit(s, (0, panel_y))

# ───────────────────────────────────────────────────────────────
#  Облако
# ───────────────────────────────────────────────────────────────
class Cloud:
    def __init__(self):
        self.w = random.randint(50, 110)
        self.h = random.randint(24, 44)
        self.x = random.randint(self.w//2, display_width - self.w//2)
        self.y = float(random.randint(-500, -50))
        self.phase = random.uniform(0, math.pi*2)
        self.speed = random.uniform(0.1, 0.4)
    def draw(self, surf, t):
        draw_cloud(surf, int(self.x), int(self.y), self.w, self.h, t, self.phase)

# ───────────────────────────────────────────────────────────────
#  Платформа
# ───────────────────────────────────────────────────────────────
PLAT_NORMAL  = 0
PLAT_MOVING  = 1
PLAT_BOUNCE  = 2

class Platform:
    H = 14
    def __init__(self, x, y, w, kind=PLAT_NORMAL):
        self.x = float(x); self.y = float(y)
        self.w = w; self.kind = kind
        self.phase = random.uniform(0, math.pi*2)
        # цвет по типу
        self.color = {
            PLAT_NORMAL: COL_PLAT_GLOW,
            PLAT_MOVING: (0, 200, 255),
            PLAT_BOUNCE: (80, 255, 120),
        }[kind]
        self.vx = 0
        if kind == PLAT_MOVING:
            self.vx = random.choice([-1,1]) * random.uniform(1.2, 2.5)
    def update(self):
        if self.kind == PLAT_MOVING:
            self.x += self.vx
            if self.x < 0 or self.x + self.w > display_width:
                self.vx *= -1
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.H)
    def draw(self, surf, t):
        draw_platform(surf, int(self.x), int(self.y), self.w,
                      self.H, t, self.phase, self.color)

# ───────────────────────────────────────────────────────────────
#  Пауэр-ап (ракета / щит)
# ───────────────────────────────────────────────────────────────
PU_ROCKET = 'rocket'
PU_SHIELD = 'shield'

class PowerUp:
    SIZE = 24
    def __init__(self, x, y, kind=PU_ROCKET):
        self.x = float(x); self.y = float(y)
        self.kind  = kind
        self.phase = random.uniform(0, math.pi*2)
    @property
    def rect(self):
        s = self.SIZE
        return pygame.Rect(int(self.x)-s//2, int(self.y)-s//2, s, s)
    def draw(self, surf, t):
        bob = math.sin(self.phase + t*0.004)*4
        cx, cy = int(self.x), int(self.y+bob)
        if self.kind == PU_ROCKET:
            col  = (255,160,0)
            glow = (255,200,60)
            # корпус ракеты
            pts = [(cx, cy-12),(cx-7,cy+8),(cx,cy+4),(cx+7,cy+8)]
            for gg, ga in [(14,25),(8,50),(3,100)]:
                gs = pygame.Surface((gg*2+4,gg*2+4), pygame.SRCALPHA)
                pygame.draw.circle(gs, (*glow,ga),(gg+2,gg+2),gg)
                surf.blit(gs, (cx-gg-2,cy-gg-2))
            pygame.draw.polygon(surf, col, pts)
            # окошко
            pygame.draw.circle(surf, (200,240,255), (cx, cy-4), 3)
            # пламя
            flame_pts = [(cx-4,cy+8),(cx,cy+16),(cx+4,cy+8)]
            pygame.draw.polygon(surf, (255,80,0), flame_pts)
        else:  # shield
            col  = (60,140,255)
            glow = (100,180,255)
            for gg, ga in [(14,25),(8,50),(3,100)]:
                gs = pygame.Surface((gg*2+4,gg*2+4), pygame.SRCALPHA)
                pygame.draw.circle(gs, (*glow,ga),(gg+2,gg+2),gg)
                surf.blit(gs, (cx-gg-2,cy-gg-2))
            # щит — арка
            pygame.draw.arc(surf, col,
                            (cx-11,cy-11,22,22), 0, math.pi, 3)
            pygame.draw.line(surf, col, (cx-11,cy),(cx+11,cy), 3)
            # крест внутри
            pygame.draw.line(surf, glow,(cx,cy-6),(cx,cy+6),2)
            pygame.draw.line(surf, glow,(cx-6,cy),(cx+6,cy),2)

# ───────────────────────────────────────────────────────────────
#  Враг
# ───────────────────────────────────────────────────────────────
class Enemy:
    def __init__(self, score):
        self.key   = random.choice(VIRUS_KEYS)
        self.phase = random.uniform(0, math.pi*2)
        self.size  = random.uniform(0.8, 1.3)
        # спавним слева или справа
        if random.random() < 0.5:
            self.x = float(-60)
            self.vx = random.uniform(1.5, 3.0)
        else:
            self.x = float(display_width + 60)
            self.vx = -random.uniform(1.5, 3.0)
        # скорость растёт с очками
        speed_mult = 1.0 + score / 1000
        self.vx *= speed_mult
        self.y  = float(random.randint(60, display_height//2))
        self.vy = 0.0
        self.dy = random.uniform(0.03, 0.08)
        self.dead = False

    @property
    def rect(self):
        r = int(20 * self.size)
        return pygame.Rect(int(self.x)-r, int(self.y)-r, r*2, r*2)

    def update(self):
        self.x  += self.vx
        self.vy += self.dy
        if abs(self.vy) > 1.5: self.dy *= -1
        self.y  += self.vy
        if self.x > display_width+120 or self.x < -120:
            self.dead = True

    def draw(self, surf, t):
        if self.dead: return
        draw_virus(surf, self.key, int(self.x), int(self.y),
                   t, self.phase, self.size)

# ───────────────────────────────────────────────────────────────
#  HUD
# ───────────────────────────────────────────────────────────────
def draw_hud(surf, score, highscore, attack_cd, attack_total,
             shield_active, rocket_active, font_name, t):
    # верхняя полоска
    bar = pygame.Surface((display_width, 46), pygame.SRCALPHA)
    for y in range(46):
        a = int(180*(1-y/46))
        pygame.draw.line(bar, (2,4,18,a),(0,y),(display_width,y))
    pygame.draw.line(bar, (*COL_NEON, 80),(0,45),(display_width,45),1)
    surf.blit(bar,(0,0))

    # очки — по центру, большие
    font_big = pygame.font.Font(font_name, 26)
    ts = font_big.render(str(score), True, COL_NEON)
    ts_glow = pygame.Surface(ts.get_size(), pygame.SRCALPHA)
    ts_glow.blit(ts, (0,0)); ts_glow.set_alpha(80)
    surf.blit(ts, ts.get_rect(midtop=(display_width//2, 6)))

    # рекорд — маленький, слева
    font_sm = pygame.font.SysFont(None, 20)
    hi_lbl  = font_sm.render(f'HI {highscore}', True, COL_NEON_DIM)
    surf.blit(hi_lbl, (10, 14))

    # кулдаун атаки — полоска + текст
    now     = pygame.time.get_ticks()
    cd_rem  = max(0, attack_cd - now)
    ready   = cd_rem == 0
    bw, bh  = 72, 7
    bx, by  = display_width - bw - 10, 16
    # фон
    pygame.draw.rect(surf,(20,30,60),(bx,by,bw,bh), border_radius=3)
    # заполнение
    fill = int(bw*(1 - cd_rem/attack_total)) if not ready else bw
    fcol = COL_ACCENT if ready else COL_NEON2
    if fill>0:
        pygame.draw.rect(surf, fcol,(bx,by,fill,bh), border_radius=3)
    pygame.draw.rect(surf, COL_NEON_DIM,(bx,by,bw,bh), border_radius=3, width=1)

    hint = 'Z атака' if ready else f'{cd_rem//100/10:.1f}s'
    hl   = font_sm.render(hint, True, fcol if ready else (100,120,160))
    surf.blit(hl, (bx, by+bh+3))

    # иконки активных бонусов
    ix = 10
    if rocket_active:
        r_lbl = font_sm.render('🚀', True, (255,200,0))
        surf.blit(r_lbl, (ix, 26)); ix += 26
    if shield_active:
        s_lbl = font_sm.render('🛡', True, (80,160,255))
        surf.blit(s_lbl, (ix, 26))

# ───────────────────────────────────────────────────────────────
#  Главный класс Game
# ───────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('VirusJump')
        self.screen = pygame.display.set_mode((display_width, display_height))
        self.clock  = pygame.time.Clock()
        self.font_name = pygame.font.match_font(Font_Name)
        self.float_font = pygame.font.SysFont(None, 24)

        self._load_data()
        self.bg = Background(display_width, display_height)
        self._reset()

    # ── ресурсы ────────────────────────────────────────────────
    def _load_data(self):
        base = path.dirname(__file__)
        hs_path = path.join(base, hs_file)
        try:
            with open(hs_path,'r') as f: self.highscore = int(f.read())
        except Exception: self.highscore = 0
        self._hs_path = hs_path

        snd = path.join(base,'sound')
        pygame.mixer.set_num_channels(8)
        try:
            pygame.mixer.music.load(path.join(snd,'background_music.ogg'))
            pygame.mixer.music.set_volume(0.25)
        except Exception: pass
        try:
            self.snd_jump = pygame.mixer.Sound(path.join(snd,'jump.ogg'))
            self.snd_jump.set_volume(0.1)
        except Exception: self.snd_jump = None
        try:
            self.snd_pow = pygame.mixer.Sound(path.join(snd,'pow.wav'))
            self.snd_pow.set_volume(0.35)
        except Exception: self.snd_pow = None

    # ── сброс ──────────────────────────────────────────────────
    def _reset(self):
        self.score       = 0
        self.scroll_y    = 0
        self.game_over   = False
        self.t           = 0
        self.particles   = []
        self.float_texts = []
        self.virus_panel = None   # текущая инфо-плашка

        self.attack_timer    = 0
        self.attack_cooldown = 0
        self.invuln_timer    = 0
        self.shield_active   = False
        self.shield_end      = 0
        self.rocket_active   = False
        self.rocket_end      = 0

        self.enemy_timer     = pygame.time.get_ticks() + enemies_freq
        self.combo           = 0
        self.combo_timer     = 0

        # физика
        self.pos = vec(display_width/2, display_height - 70)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.facing_right = True

        # объекты мира
        self.platforms = []
        self.enemies   = []
        self.powerups  = []
        self.clouds    = [Cloud() for _ in range(10)]
        for c in self.clouds: c.y = random.uniform(0, display_height)

        # стартовые платформы
        self.platforms.append(
            Platform(display_width/2-55, display_height-44, 110))
        starts = [
            (display_width/2-50, display_height-150),
            (display_width/2-100,display_height-300),
            (display_width/2,    display_height-450),
            (60,                 display_height-580),
        ]
        for (px,py) in starts:
            w = random.randint(60,100)
            self.platforms.append(Platform(px, py, w))

    # ── главный цикл ──────────────────────────────────────────
    def run(self):
        try: pygame.mixer.music.play(loops=-1)
        except Exception: pass

        while True:
            dt = self.clock.tick(fps)
            self.t += dt

            self._handle_events()
            if not self.game_over:
                self._update(dt)
            self._draw()

            if self.game_over:
                self._game_over_screen()

        pygame.mixer.music.fadeout(500)

    # ── события ───────────────────────────────────────────────
    def _handle_events(self):
        self.acc = vec(0, gravity)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.acc.x = -player_Acc; self.facing_right=False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.acc.x =  player_Acc; self.facing_right=True

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: self._pause()
                if e.key == pygame.K_z:      self._try_attack()

    # ── физика + логика ───────────────────────────────────────
    def _update(self, dt):
        now = pygame.time.get_ticks()

        # ── физика ────────────────────────────────────────────
        self.acc.x += self.vel.x * player_Fric
        self.vel   += self.acc
        self.vel.x  = max(-9, min(9, self.vel.x))

        # ракетный бонус — тянет вверх
        if self.rocket_active:
            self.vel.y = max(self.vel.y - 0.9, -14)
            if now > self.rocket_end: self.rocket_active = False

        self.pos   += self.vel + 0.5*self.acc

        # обёртка по горизонтали
        if self.pos.x > display_width+20:  self.pos.x = -20
        if self.pos.x < -20:               self.pos.x = display_width+20

        # ── коллизия с платформами ────────────────────────────
        if self.vel.y > 0:
            p_rect = pygame.Rect(int(self.pos.x)-14,
                                 int(self.pos.y)-3, 28, 6)
            for p in self.platforms:
                pr = p.rect
                if (p_rect.colliderect(pr) and
                        self.pos.y - self.vel.y <= pr.top + 4):
                    if p.kind == PLAT_BOUNCE:
                        self.pos.y = pr.top
                        self._do_jump(force=-18)
                        self._add_float(int(self.pos.x),
                                        int(self.pos.y)-30,
                                        'BOUNCE!', (80,255,120))
                    else:
                        self.pos.y = pr.top
                        self._do_jump()
                    break

        # ── пауэр-апы ─────────────────────────────────────────
        player_rect = pygame.Rect(int(self.pos.x)-14,
                                  int(self.pos.y)-40, 28, 40)
        for pu in self.powerups[:]:
            if player_rect.colliderect(pu.rect):
                if self.snd_pow: self.snd_pow.play()
                if pu.kind == PU_ROCKET:
                    self.rocket_active = True
                    self.rocket_end    = now + 3000
                    self._add_float(int(self.pos.x),
                                    int(self.pos.y)-40, '🚀 РАКЕТА!', (255,200,0))
                else:
                    self.shield_active = True
                    self.shield_end    = now + 5000
                    self._add_float(int(self.pos.x),
                                    int(self.pos.y)-40, '🛡 ЩИТ!', (80,160,255))
                self._burst(int(self.pos.x), int(self.pos.y),
                            (255,200,0) if pu.kind==PU_ROCKET else (80,160,255), 12)
                self.powerups.remove(pu)

        # ── щит истёк ─────────────────────────────────────────
        if self.shield_active and now > self.shield_end:
            self.shield_active = False

        # ── враги ─────────────────────────────────────────────
        if now > self.enemy_timer:
            interval = max(2000, enemies_freq - self.score*2)
            self.enemy_timer = now + interval + random.randint(-600,600)
            if self.score > 30:
                self.enemies.append(Enemy(self.score))

        self._check_enemies(now)

        # ── скролл ────────────────────────────────────────────
        threshold = display_height / 3.8
        if self.pos.y < threshold:
            dy = threshold - self.pos.y
            self.pos.y = threshold
            self.scroll_y += dy
            self.score    += int(dy * 0.12)

            for p  in self.platforms: p.y  += dy
            for e  in self.enemies:   e.y  += dy
            for c  in self.clouds:    c.y  += dy * 0.45
            for pu in self.powerups:  pu.y += dy

        # ── новые платформы ───────────────────────────────────
        needed = PLATFORM_BASE_COUNT + min(self.score//300, 4)
        while len(self.platforms) < needed:
            top_y = min(p.y for p in self.platforms) if self.platforms else display_height
            gap   = random.uniform(90, 150)
            ny    = top_y - gap
            nw    = max(50, random.randint(55,105) - self.score//200)
            nx    = random.randint(10, display_width-nw-10)
            # тип платформы
            r = random.random()
            if   self.score>400 and r<0.12: kind=PLAT_BOUNCE
            elif self.score>200 and r<0.22: kind=PLAT_MOVING
            else:                            kind=PLAT_NORMAL
            p = Platform(nx, ny, nw, kind)
            self.platforms.append(p)
            # пауэр-ап
            if random.randint(0,99) < power_up_spawn_freq:
                pk = PU_ROCKET if random.random()<0.6 else PU_SHIELD
                self.powerups.append(PowerUp(nx+nw//2, ny-20, pk))

        # ── убираем то что ушло вниз ──────────────────────────
        self.platforms = [p for p in self.platforms if p.y < display_height+40]
        self.enemies   = [e for e in self.enemies   if not e.dead and e.y < display_height+80]
        self.powerups  = [pu for pu in self.powerups if pu.y < display_height+40]
        # облака
        for c in self.clouds[:]:
            if c.y > display_height+100: self.clouds.remove(c)
        if len(self.clouds) < 12:
            nc = Cloud(); nc.y = float(random.randint(-400,-50))
            self.clouds.append(nc)

        # ── обновляем объекты ─────────────────────────────────
        for p  in self.platforms: p.update()
        for e  in self.enemies:   e.update()
        for pt in self.particles[:]:
            pt.update()
            if pt.life<=0: self.particles.remove(pt)
        for ft in self.float_texts[:]:
            ft.update()
            if ft.life<=0: self.float_texts.remove(ft)
        if self.virus_panel:
            self.virus_panel.update()
            if not self.virus_panel.alive:
                self.virus_panel = None

        # ── combo decay ───────────────────────────────────────
        if self.combo_timer and now > self.combo_timer:
            self.combo = 0

        # ── упал вниз ─────────────────────────────────────────
        if self.pos.y > display_height + 60:
            self.game_over = True

    # ── атака ─────────────────────────────────────────────────
    def _try_attack(self):
        now = pygame.time.get_ticks()
        if now < self.attack_cooldown: return
        self.attack_timer    = now + ATTACK_DURATION
        self.attack_cooldown = now + ATTACK_COOLDOWN
        self._burst(int(self.pos.x), int(self.pos.y)-20,
                    (255,200,50), 16)
        self._add_float(int(self.pos.x), int(self.pos.y)-50,
                         'УДАР!', (255,220,0))

    def _check_enemies(self, now):
        px, py = int(self.pos.x), int(self.pos.y)
        attack_rect = pygame.Rect(px - (36 if self.facing_right else -4),
                                  py - 46, 40, 40)
        player_rect = pygame.Rect(px-14, py-44, 28, 44)
        is_attacking = now < self.attack_timer

        for e in self.enemies[:]:
            er = e.rect
            if player_rect.colliderect(er):
                if is_attacking and attack_rect.colliderect(er):
                    # убили врага
                    e.dead = True
                    self.combo += 1
                    self.combo_timer = now + 2000
                    pts = 50 * self.combo
                    self.score += pts
                    self._burst(int(e.x), int(e.y),
                                VIRUS_DEFS[e.key][1], 20)
                    lbl = f'x{self.combo} COMBO  +{pts}' if self.combo>1 else f'+{pts}'
                    self._add_float(int(e.x), int(e.y)-20, lbl,
                                    (80,255,120) if self.combo>1 else (255,220,50))
                    self.virus_panel = VirusPanel(e.key, won=True)
                    self.enemies.remove(e)

                elif self.shield_active:
                    # щит поглощает
                    e.dead = True
                    self.shield_active = False
                    self._add_float(px, py-50, 'БЛОК!', (80,160,255))
                    self.virus_panel = VirusPanel(e.key, won=True)
                    self.enemies.remove(e)

                elif self.invuln_timer > now:
                    pass   # неуязвимы

                else:
                    # получили урон — game over
                    self.virus_panel = VirusPanel(e.key, won=False)
                    self._burst(px, py-20, (220,30,60), 25)
                    self.game_over = True
                    return

    # ── прыжок ────────────────────────────────────────────────
    def _do_jump(self, force=None):
        self.vel.y = force if force else jump_force
        if self.snd_jump: self.snd_jump.play()
        self._burst(int(self.pos.x), int(self.pos.y),
                    COL_NEON, 6)

    # ── частицы ───────────────────────────────────────────────
    def _burst(self, x, y, color, count):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def _add_float(self, x, y, text, color=(255,220,0)):
        self.float_texts.append(FloatingText(x, y, text, color))

    # ── рисование ─────────────────────────────────────────────
    def _draw(self):
        self.bg.draw(self.screen, self.t, self.scroll_y)

        # облака
        for c in self.clouds: c.draw(self.screen, self.t)

        # платформы
        for p in self.platforms: p.draw(self.screen, self.t)

        # пауэр-апы
        for pu in self.powerups: pu.draw(self.screen, self.t)

        # враги
        for e in self.enemies: e.draw(self.screen, self.t)

        # частицы
        for pt in self.particles: pt.draw(self.screen)

        # щит вокруг игрока
        if self.shield_active:
            now = pygame.time.get_ticks()
            pulse = 0.5 + 0.5*math.sin(self.t*0.01)
            for sr, sa in [(28, int(40*pulse)),(22, int(80*pulse))]:
                ss = pygame.Surface((sr*2+4,sr*2+4), pygame.SRCALPHA)
                pygame.draw.circle(ss, (60,140,255,sa),(sr+2,sr+2),sr)
                pygame.draw.circle(ss, (100,180,255,int(sa*1.5)),(sr+2,sr+2),sr,2)
                self.screen.blit(ss,(int(self.pos.x)-sr-2,
                                     int(self.pos.y)-sr-20))

        # игрок
        now_t = pygame.time.get_ticks()
        is_attacking = now_t < self.attack_timer
        invuln = self.invuln_timer > now_t
        draw_hero(self.screen,
                  int(self.pos.x), int(self.pos.y),
                  self.facing_right,
                  self.vel.y < -2,
                  is_attacking,
                  invuln,
                  self.t)

        # всплывающие тексты
        for ft in self.float_texts:
            ft.draw(self.screen, self.float_font)

        # панель вируса
        if self.virus_panel:
            self.virus_panel.draw(self.screen, self.t)

        # HUD
        draw_hud(self.screen, self.score, self.highscore,
                 self.attack_cooldown, ATTACK_COOLDOWN,
                 self.shield_active, self.rocket_active,
                 self.font_name, self.t)

        pygame.display.flip()

    # ── стартовый экран ───────────────────────────────────────
    def start_screen(self):
        menu_t = 0
        while True:
            dt = self.clock.tick(fps)
            menu_t += dt
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    return

            self.bg.draw(self.screen, menu_t, 0)

            # анимированные вирусы на фоне
            for i, key in enumerate(VIRUS_KEYS):
                bx = 55 + i*(display_width-80)//len(VIRUS_KEYS)
                by = 420 + int(math.sin(menu_t*0.002 + i*0.9)*20)
                draw_virus(self.screen, key, bx, by, menu_t,
                           menu_t*0.001 + i, size=0.85)

            # заголовок с неоновым свечением
            pulse = 0.7 + 0.3*math.sin(menu_t*0.003)
            for size, alpha in [(62,30),(56,60),(50,200)]:
                f  = pygame.font.Font(self.font_name, size)
                ts = f.render('VirusJump', True,
                              tuple(int(c*pulse) for c in COL_NEON))
                ts.set_alpha(alpha)
                self.screen.blit(ts, ts.get_rect(
                    midtop=(display_width//2, 90)))

            draw_text(self.screen,'БЕЗДНА ЖДЁТ',18,(80,160,255),
                      display_width//2, 158, self.font_name, shadow=False)

            # управление
            ctrl = [
                ('← →', 'движение'),
                ('Z',   'атака'),
                ('ESC', 'пауза'),
            ]
            yy = 230
            fm = pygame.font.SysFont(None,22)
            for k, v in ctrl:
                kl = fm.render(k, True, COL_ACCENT)
                vl = fm.render(v, True, (160,200,230))
                self.screen.blit(kl, (display_width//2-60, yy))
                self.screen.blit(vl, (display_width//2+10, yy))
                yy += 24

            if int(menu_t/600)%2==0:
                draw_text(self.screen,'[ нажми любую клавишу ]',18,
                          (180,220,255),display_width//2,310,
                          self.font_name, shadow=False)

            hi_lbl = fm.render(f'Рекорд: {self.highscore}',
                                True, COL_NEON_DIM)
            self.screen.blit(hi_lbl,
                hi_lbl.get_rect(midbottom=(display_width//2, display_height-20)))

            pygame.display.flip()

    # ── game over ─────────────────────────────────────────────
    def _game_over_screen(self):
        # ждём пока пройдёт панель вируса (или 2 сек)
        wait_start = pygame.time.get_ticks()
        while self.virus_panel and self.virus_panel.alive:
            dt = self.clock.tick(fps)
            self.t += dt
            self.virus_panel.update()
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN: break
            self._draw()
            if pygame.time.get_ticks() - wait_start > 3000: break

        # сохраняем рекорд
        if self.score > self.highscore:
            self.highscore = self.score
            try:
                with open(self._hs_path,'w') as f: f.write(str(self.score))
            except Exception: pass

        anim_t = 0
        while True:
            dt = self.clock.tick(fps)
            anim_t += dt
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    self._reset()
                    self.run()
                    return

            self.bg.draw(self.screen, anim_t, self.scroll_y)

            # overlay
            ov = pygame.Surface((display_width, display_height), pygame.SRCALPHA)
            ov.fill((2,4,18,180))
            self.screen.blit(ov,(0,0))

            pulse = 0.6+0.4*math.sin(anim_t*0.004)
            fc = tuple(int(c*pulse) for c in (220,30,60))
            draw_text(self.screen,'СИСТЕМА ЗАРАЖЕНА',34,fc,
                      display_width//2,140, self.font_name)

            draw_text(self.screen, str(self.score),54,COL_NEON,
                      display_width//2,210, self.font_name)
            draw_text(self.screen,'очков',18,(100,160,220),
                      display_width//2,270, self.font_name)

            if self.score >= self.highscore:
                draw_text(self.screen,'◆ НОВЫЙ РЕКОРД ◆',22,(255,220,0),
                          display_width//2,310, self.font_name)
            else:
                draw_text(self.screen,f'Рекорд: {self.highscore}',20,
                          COL_NEON_DIM, display_width//2,310, self.font_name)

            draw_text(self.screen,f'Высота: {int(self.scroll_y//10)} м',18,
                      (100,140,200), display_width//2,360, self.font_name)

            if int(anim_t/600)%2==0:
                draw_text(self.screen,'[ нажми любую клавишу ]',16,
                          (160,200,240),display_width//2,430,
                          self.font_name, shadow=False)

            pygame.display.flip()

    # ── пауза ─────────────────────────────────────────────────
    def _pause(self):
        items  = ['Продолжить', 'Выйти']
        font   = pygame.font.SysFont('Corbel',30)
        ov     = pygame.Surface((display_width,display_height),pygame.SRCALPHA)
        ov.fill((2,4,18,200))
        while True:
            mouse = pygame.mouse.get_pos()
            for e in pygame.event.get():
                if e.type==pygame.QUIT: pygame.quit(); sys.exit()
                if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: return
                if e.type==pygame.MOUSEBUTTONDOWN:
                    for i,item in enumerate(items):
                        bx=display_width//2-80; by=280+i*60
                        if bx<=mouse[0]<=bx+160 and by<=mouse[1]<=by+44:
                            if i==0: return
                            else: pygame.quit(); sys.exit()

            self.screen.blit(ov,(0,0))
            draw_text(self.screen,'ПАУЗА',38,COL_NEON,
                      display_width//2,160,self.font_name)
            for i,item in enumerate(items):
                bx=display_width//2-80; by=280+i*60
                hov=(bx<=mouse[0]<=bx+160 and by<=mouse[1]<=by+44)
                col=(30,80,160) if hov else (15,40,90)
                pygame.draw.rect(self.screen,col,(bx,by,160,44),border_radius=6)
                pygame.draw.rect(self.screen,COL_NEON_DIM,(bx,by,160,44),
                                 border_radius=6,width=1)
                lbl=font.render(item,True,white if hov else (140,180,220))
                self.screen.blit(lbl,lbl.get_rect(center=(display_width//2,by+22)))
            pygame.display.flip()
            self.clock.tick(30)

# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    g = Game()
    g.start_screen()
    g.run()
