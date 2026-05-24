# ── draw_utils.py  ───────────────────────────────────────────
# Все процедурные рисовалки: ГГ, вирусы, платформы, облака, фон
import pygame, math, random
from settings import *

# ─────────────────────────────────────────────────────────────
#  Утилиты
# ─────────────────────────────────────────────────────────────
def glow_circle(surf, color, center, r, glow=18, alpha=120):
    s = pygame.Surface((r*2+glow*2, r*2+glow*2), pygame.SRCALPHA)
    for i in range(glow, 0, -3):
        a = int(alpha * (i / glow) * 0.5)
        pygame.draw.circle(s, (*color, a),
                           (r+glow, r+glow), r+i)
    pygame.draw.circle(s, (*color, 200), (r+glow, r+glow), r)
    surf.blit(s, (center[0]-r-glow, center[1]-r-glow))

def glow_polygon(surf, color, points, glow=8, alpha=100):
    s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for i in range(glow, 0, -2):
        a = int(alpha * (i/glow) * 0.4)
        expanded = []
        cx = sum(p[0] for p in points)/len(points)
        cy = sum(p[1] for p in points)/len(points)
        for px, py in points:
            dx, dy = px-cx, py-cy
            L = math.hypot(dx,dy) or 1
            expanded.append((px + dx/L*i, py + dy/L*i))
        pygame.draw.polygon(s, (*color, a), expanded)
    pygame.draw.polygon(s, (*color, 220), points)
    surf.blit(s, (0,0))

def neon_line(surf, color, p1, p2, w=2, glow=6):
    for i in range(glow, 0, -2):
        a = int(180 * (i/glow) * 0.3)
        s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.line(s, (*color, a), p1, p2, w+i*2)
        surf.blit(s, (0,0))
    pygame.draw.line(surf, color, p1, p2, w)

# ─────────────────────────────────────────────────────────────
#  Фон: звёздное поле + туманность
# ─────────────────────────────────────────────────────────────
class Background:
    def __init__(self, w, h):
        self.w, self.h = w, h
        rng = random.Random(42)
        # статичные звёзды
        self.stars = [
            (rng.randint(0, w), rng.randint(0, h),
             rng.uniform(0.4, 1.8), rng.uniform(0, math.pi*2))
            for _ in range(120)
        ]
        # туманность: несколько больших полупрозрачных кругов
        self.nebula = [
            (rng.randint(0, w), rng.randint(0, h),
             rng.randint(60, 160),
             (rng.randint(0,30), rng.randint(10,60), rng.randint(80,180)),
             rng.randint(15, 40))
            for _ in range(8)
        ]
        self._cache = None
        self._build_cache()

    def _build_cache(self):
        s = pygame.Surface((self.w, self.h))
        # градиент фона
        for y in range(self.h):
            t = y / self.h
            r = int(COL_BG[0]*(1-t) + COL_BG2[0]*t)
            g = int(COL_BG[1]*(1-t) + COL_BG2[1]*t)
            b = int(COL_BG[2]*(1-t) + COL_BG2[2]*t)
            pygame.draw.line(s, (r,g,b), (0,y), (self.w,y))
        # туманность
        for (nx, ny, nr, nc, na) in self.nebula:
            ns = pygame.Surface((nr*2, nr*2), pygame.SRCALPHA)
            for i in range(nr, 0, -4):
                a = int(na * (i/nr)**2)
                pygame.draw.circle(ns, (*nc, a), (nr,nr), i)
            s.blit(ns, (nx-nr, ny-nr))
        self._cache = s

    def draw(self, surf, t, scroll_y):
        surf.blit(self._cache, (0, 0))
        # мерцающие звёзды поверх
        for (sx, sy, sr, sphase) in self.stars:
            bright = 0.5 + 0.5*math.sin(sphase + t*0.002)
            a = int(bright * 220)
            col = (int(180+70*bright), int(200+55*bright), 255)
            r = max(1, int(sr * bright))
            # звёзды немного скроллятся
            draw_y = int((sy - scroll_y*0.04) % self.h)
            if r > 1:
                gs = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
                pygame.draw.circle(gs, (*col, a), (r*2, r*2), r)
                surf.blit(gs, (sx - r*2, draw_y - r*2))
            else:
                ps = pygame.Surface((3,3), pygame.SRCALPHA)
                pygame.draw.circle(ps, (*col, a), (1,1), 1)
                surf.blit(ps, (sx-1, draw_y-1))

# ─────────────────────────────────────────────────────────────
#  Облако: переосмысленное под космос — туманный сгусток
# ─────────────────────────────────────────────────────────────
def draw_cloud(surf, x, y, w, h, t, phase):
    s = pygame.Surface((w+20, h+20), pygame.SRCALPHA)
    pulse = 0.7 + 0.3*math.sin(phase + t*0.0015)
    # несколько эллипсов с прозрачностью
    blobs = [
        (w//2, h//2,    w//2,  h//2),
        (w//4, h//2+2,  w//3,  h//3),
        (3*w//4, h//2+2, w//3, h//3),
    ]
    for (bx, by, bw, bh) in blobs:
        bs = pygame.Surface((bw*2+10, bh*2+10), pygame.SRCALPHA)
        for i in range(4, 0, -1):
            a = int(18 * pulse * i)
            pygame.draw.ellipse(bs, (20, 80, 180, a),
                                (i, i, bw*2-i*2+10, bh*2-i*2+10))
        pygame.draw.ellipse(bs, (30, 100, 200, int(55*pulse)),
                            (4, 4, bw*2+2, bh*2+2))
        s.blit(bs, (bx - bw - 5, by - bh - 5))
    # тонкий контур
    pygame.draw.ellipse(s, (0, 140, 255, int(80*pulse)),
                        (2, 4, w+16, h+12), 1)
    surf.blit(s, (x - w//2 - 10, y - h//2 - 10))

# ─────────────────────────────────────────────────────────────
#  Платформа: неоновая плита
# ─────────────────────────────────────────────────────────────
def draw_platform(surf, x, y, w, h=14, t=0, phase=0, color=None):
    glow_col = color or COL_PLAT_GLOW
    pulse = 0.6 + 0.4*math.sin(phase + t*0.002)
    s = pygame.Surface((w+20, h+20), pygame.SRCALPHA)
    # свечение
    for i in range(8, 0, -2):
        a = int(60 * pulse * (i/8))
        pygame.draw.rect(s, (*glow_col, a),
                         (10-i, 10-i//2, w+i*2, h+i), border_radius=5+i)
    # тело платформы — градиент
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for row in range(h):
        t_row = row/h
        r = int(COL_PLATFORM[0]*(1-t_row) + glow_col[0]*0.15*t_row)
        g = int(COL_PLATFORM[1]*(1-t_row) + glow_col[1]*0.15*t_row)
        b = int(COL_PLATFORM[2]*(1-t_row) + glow_col[2]*0.25*t_row)
        pygame.draw.line(body, (r,g,b,230), (0,row), (w,row))
    # скруглённые края
    pygame.draw.rect(body, (0,0,0,0), (0,0,w,h), border_radius=5)
    s.blit(body, (10, 10))
    # верхняя неоновая линия
    pygame.draw.line(s, (*glow_col, int(220*pulse)),
                     (14, 11), (w+6, 11), 2)
    # декор — маленькие точки по краям
    for i in range(3):
        dx = 18 + i*(w//3)
        pygame.draw.circle(s, (*glow_col, int(180*pulse)), (dx, h+6), 2)
    surf.blit(s, (x-10, y-10))

# ─────────────────────────────────────────────────────────────
#  ГГ: персонаж на основе пикачу-силуэта, рисованный
# ─────────────────────────────────────────────────────────────
def draw_hero(surf, x, y, facing_right, is_jumping, is_attacking, invuln, t):
    """
    x, y — midbottom позиция
    Размер примерно 44×52
    """
    flip = -1 if not facing_right else 1
    cx, cy = x, y - 26   # центр тела

    s = pygame.Surface((80, 80), pygame.SRCALPHA)
    # локальные координаты относительно центра s
    lx, ly = 40, 40

    # мигание при неуязвимости
    if invuln and (int(t/80) % 2 == 0):
        surf_out = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        _draw_hero_inner(surf_out, cx, cy, flip, is_jumping, is_attacking, t)
        surf_out.set_alpha(80)
        surf.blit(surf_out, (0,0))
        return

    _draw_hero_inner(surf, cx, cy, flip, is_jumping, is_attacking, t)

def _draw_hero_inner(surf, cx, cy, flip, is_jumping, is_attacking, t):
    # ── щёки / свечение вокруг тела ──────────────────────────
    for r, a in [(22,18),(18,30),(14,55)]:
        gs = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        pygame.draw.circle(gs, (0, 160, 255, a), (r+2,r+2), r)
        surf.blit(gs, (cx-r-2, cy-r-2))

    # ── уши (треугольники пикачу) ──────────────────────────────
    ear_col   = (255, 210, 0)
    ear_tip   = (40,  30,  0)
    for side in [-1, 1]:
        ex = cx + flip*side*12
        ey = cy - 22
        pts = [(ex, ey), (ex+flip*side*7, ey-20), (ex+flip*side*2, ey-4)]
        pygame.draw.polygon(surf, ear_col, pts)
        # чёрный кончик
        tip_pts = [(ex+flip*side*4, ey-12),
                   (ex+flip*side*7, ey-20),
                   (ex+flip*side*3, ey-8)]
        pygame.draw.polygon(surf, ear_tip, tip_pts)

    # ── тело ─────────────────────────────────────────────────
    body_col = (255, 215, 0)
    # сплющиваем если прыгаем
    bw, bh = (18, 22) if not is_jumping else (20, 18)
    body_rect = pygame.Rect(cx-bw, cy-bh+4, bw*2, bh*2)
    pygame.draw.ellipse(surf, body_col, body_rect)
    # живот — светлее
    pygame.draw.ellipse(surf, (255, 240, 160),
                        (cx-10, cy, 20, 14))

    # ── голова ───────────────────────────────────────────────
    hw = 18
    pygame.draw.circle(surf, body_col, (cx, cy-14), hw)

    # ── щёки пикачу — красные кружочки ────────────────────────
    pygame.draw.circle(surf, (255, 80, 80), (cx+flip*11, cy-10), 5)

    # ── глаза ─────────────────────────────────────────────────
    eye_x = cx + flip*6
    eye_y = cy - 17
    # белок
    pygame.draw.ellipse(surf, (255,255,255), (eye_x-5, eye_y-5, 10, 11))
    # зрачок
    pygame.draw.circle(surf, (20, 20, 60), (eye_x+flip, eye_y+1), 4)
    # блик
    pygame.draw.circle(surf, (255,255,255), (eye_x+flip+1, eye_y-1), 1)
    # второй глаз (дальний, меньше)
    eye2x = cx - flip*4
    pygame.draw.ellipse(surf, (255,255,255), (eye2x-3, eye_y-3, 7, 8))
    pygame.draw.circle(surf, (20,20,60), (eye2x, eye_y+1), 3)

    # ── рот ───────────────────────────────────────────────────
    if is_jumping:
        # открытый рот — восторг
        pygame.draw.ellipse(surf, (180,40,40), (cx-4, cy-8, 8, 6))
    else:
        pygame.draw.arc(surf, (180,40,40),
                        (cx-5, cy-10, 10, 8), math.pi*1.1, math.pi*1.9, 2)

    # ── хвост ─────────────────────────────────────────────────
    tail_pts = [
        (cx - flip*14, cy+10),
        (cx - flip*22, cy-2),
        (cx - flip*28, cy+6),
        (cx - flip*24, cy+18),
        (cx - flip*16, cy+20),
    ]
    if len(tail_pts) >= 3:
        pygame.draw.lines(surf, (255,200,0), False, tail_pts, 4)
    # кончик хвоста — жёлтый треугольник
    ttip = [(cx-flip*26, cy+4),
            (cx-flip*32, cy-2),
            (cx-flip*24, cy+16)]
    pygame.draw.polygon(surf, (255, 220, 0), ttip)

    # ── лапки ────────────────────────────────────────────────
    leg_y = cy + bh + 2
    for side in [-1, 1]:
        lx = cx + flip*side*8
        pygame.draw.ellipse(surf, body_col, (lx-6, leg_y-4, 12, 10))

    # ── аура атаки ────────────────────────────────────────────
    if is_attacking:
        pulse = 0.6 + 0.4*math.sin(t*0.05)
        for r, a in [(30, int(40*pulse)), (22, int(80*pulse))]:
            gs = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (255, 200, 0, a), (r+2,r+2), r)
            surf.blit(gs, (cx-r-2+flip*8, cy-r-2))
        # молния в направлении атаки
        lpts = [(cx+flip*14, cy-10),
                (cx+flip*26, cy-18),
                (cx+flip*22, cy-10),
                (cx+flip*34, cy-20)]
        pygame.draw.lines(surf, (255,240,0), False, lpts, 3)

# ─────────────────────────────────────────────────────────────
#  ВИРУСЫ — каждый со своим уникальным дизайном
# ─────────────────────────────────────────────────────────────
VIRUS_DEFS = {
    # name, color, glow_color, draw_func_name, short_desc
    'virus':    ((200,  30,  60), (255,  60,  90),  'draw_virus_classic',
                 'ВИРУС', 'Заражает файлы\nи размножается'),
    'worm':     (( 80, 180,  60), (120, 255,  80),  'draw_worm',
                 'ЧЕРВЬ', 'Сам распространяется\nпо сетям'),
    'rootkit':  ((100,  60, 220), (140, 100, 255),  'draw_rootkit',
                 'РУТКИТ', 'Скрытый\nудалённый доступ'),
    'bot':      ((  0, 180, 220), ( 40, 220, 255),  'draw_bot',
                 'БОТ', 'Выполняет команды\nбез ведома юзера'),
    'ransomware':((220,120,  20), (255,170,  40),   'draw_ransomware',
                 'ВЫМОГАТЕЛЬ', 'Шифрует данные,\nтребует выкуп'),
    'adware':   ((220, 200,  0 ), (255, 240,  40),  'draw_adware',
                 'РЕКЛАМНОЕ ПО', 'Встраивает рекламу\nв браузер'),
    'spyware':  ((160,  40, 160), (200,  80, 200),  'draw_spyware',
                 'ШПИОНСКОЕ ПО', 'Крадёт пароли\nи данные'),
}
VIRUS_KEYS = list(VIRUS_DEFS.keys())

def get_virus_info(key):
    d = VIRUS_DEFS[key]
    return {'color': d[0], 'glow': d[1],
            'title': d[3], 'desc': d[4]}

def draw_virus(surf, key, cx, cy, t, phase, size=1.0):
    """Диспетчер — вызывает нужную функцию рисования."""
    fn_name = VIRUS_DEFS[key][2]
    fn = globals()[fn_name]
    fn(surf, cx, cy, t, phase, size)

# ── Классический компьютерный вирус: ДНК-спираль + шипы ─────
def draw_virus_classic(surf, cx, cy, t, phase, size):
    col  = (200, 30, 60)
    glow = (255, 60, 90)
    r    = int(18*size)
    ang  = phase + t*0.03
    # свечение
    for gr, ga in [(r+10, 25),(r+6, 45),(r+2, 80)]:
        gs = pygame.Surface((gr*2+4,gr*2+4), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*glow, ga), (gr+2,gr+2), gr)
        surf.blit(gs, (cx-gr-2, cy-gr-2))
    # тело — двойная окружность
    pygame.draw.circle(surf, col, (cx,cy), r)
    pygame.draw.circle(surf, (240,60,90), (cx,cy), r, 2)
    # шипы
    for i in range(8):
        a = ang + i*math.pi/4
        x1 = cx + int(math.cos(a)*r)
        y1 = cy + int(math.sin(a)*r)
        x2 = cx + int(math.cos(a)*(r+8*size))
        y2 = cy + int(math.sin(a)*(r+8*size))
        pygame.draw.line(surf, glow, (x1,y1), (x2,y2), 2)
        pygame.draw.circle(surf, glow, (x2,y2), 2)
    # внутри — двойная спираль
    for strand in [0, math.pi]:
        pts = []
        for i in range(12):
            a2 = ang*2 + strand + i*math.pi/6
            rx = int(cx + math.cos(a2)*6*size)
            ry = int(cy - 7*size + i*1.1*size)
            pts.append((rx, ry))
        if len(pts) > 1:
            pygame.draw.lines(surf, (255,180,180), False, pts, 1)

# ── Червь: сегментированное тело, ползёт ──────────────────────
def draw_worm(surf, cx, cy, t, phase, size):
    col  = (60, 160, 50)
    glow = (100, 230, 70)
    seg_r = int(7*size)
    wave  = math.sin(phase + t*0.04)
    segs  = 5
    # сегменты
    for i in range(segs):
        sx = cx + int((i - segs//2) * seg_r*1.6)
        sy = cy + int(math.sin(phase + t*0.04 + i*0.8) * 5*size)
        # свечение сегмента
        gs = pygame.Surface((seg_r*2+8, seg_r*2+8), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*glow, 50), (seg_r+4,seg_r+4), seg_r+4)
        surf.blit(gs, (sx-seg_r-4, sy-seg_r-4))
        c = col if i%2==0 else (80,190,60)
        pygame.draw.circle(surf, c, (sx,sy), seg_r)
        pygame.draw.circle(surf, glow, (sx,sy), seg_r, 1)
    # голова — последний сегмент, чуть больше
    hx = cx + int((segs//2)*seg_r*1.6)
    hy = cy + int(math.sin(phase + t*0.04 + segs*0.8)*5*size)
    pygame.draw.circle(surf, (90,200,70), (hx,hy), int(seg_r*1.3))
    # глаза
    pygame.draw.circle(surf, (255,255,255), (hx+3,hy-3), 3)
    pygame.draw.circle(surf, (20,20,20),    (hx+4,hy-3), 2)
    # антенны
    for da in [-0.3, 0.3]:
        ax = hx + int(math.cos(da)*12*size)
        ay = hy + int(math.sin(da-math.pi/2)*10*size)
        pygame.draw.line(surf, glow, (hx,hy-seg_r), (ax,ay), 2)
        pygame.draw.circle(surf, glow, (ax,ay), 2)

# ── Руткит: невидимка, фрагментированный, полупрозрачный ──────
def draw_rootkit(surf, cx, cy, t, phase, size):
    col  = (80, 50, 200)
    glow = (120, 80, 255)
    r    = int(16*size)
    ang  = phase + t*0.025
    # полупрозрачное тело (руткит «скрыт»)
    body = pygame.Surface((r*2+16, r*2+16), pygame.SRCALPHA)
    # фрагменты шестиугольника
    for i in range(6):
        a = ang + i*math.pi/3
        bx = r+8 + int(math.cos(a)*r*0.6)
        by = r+8 + int(math.sin(a)*r*0.6)
        pygame.draw.circle(body, (*col, 160), (bx,by), int(r*0.4))
        pygame.draw.circle(body, (*glow, 80), (bx,by), int(r*0.4)+2, 1)
    # центр
    pygame.draw.circle(body, (*glow, 180), (r+8,r+8), int(r*0.35))
    # знак вопроса — «скрытая угроза»
    font = pygame.font.SysFont(None, int(20*size))
    lbl  = font.render('?', True, (200,180,255,200))
    body.blit(lbl, lbl.get_rect(center=(r+8, r+8)))
    surf.blit(body, (cx-r-8, cy-r-8))
    # орбитальные точки
    for i in range(3):
        oa = ang*1.5 + i*math.pi*2/3
        ox = cx + int(math.cos(oa)*(r+6)*size)
        oy = cy + int(math.sin(oa)*(r+6)*size)
        gs = pygame.Surface((10,10), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*glow, 180), (5,5), 4)
        surf.blit(gs, (ox-5, oy-5))

# ── Бот: механический, квадратный, антенна ────────────────────
def draw_bot(surf, cx, cy, t, phase, size):
    col  = (0, 150, 200)
    glow = (0, 220, 255)
    w    = int(28*size)
    h    = int(24*size)
    ang  = phase + t*0.02
    # свечение корпуса
    gs = pygame.Surface((w+16, h+16), pygame.SRCALPHA)
    pygame.draw.rect(gs, (*glow, 40), (2,2,w+12,h+12), border_radius=5)
    surf.blit(gs, (cx-w//2-8, cy-h//2-8))
    # корпус
    pygame.draw.rect(surf, col,  (cx-w//2, cy-h//2, w, h), border_radius=4)
    pygame.draw.rect(surf, glow, (cx-w//2, cy-h//2, w, h), border_radius=4, width=2)
    # экран — мигающие символы
    scr_col = (0,255,200) if int(t/300)%2==0 else (0,180,150)
    pygame.draw.rect(surf, (0,20,40), (cx-w//2+3, cy-h//2+3, w-6, h-6), border_radius=2)
    font = pygame.font.SysFont('monospace', int(9*size))
    lbl  = font.render('BOT', True, scr_col)
    surf.blit(lbl, lbl.get_rect(center=(cx, cy)))
    # антенна
    ant_y = cy - h//2
    pygame.draw.line(surf, glow, (cx, ant_y), (cx, ant_y-12*size), 2)
    pygame.draw.circle(surf, glow, (cx, int(ant_y-12*size)), int(3*size))
    # «глаза» / индикаторы
    for side, ecol in [(-1,(0,255,100)),(1,(255,60,60))]:
        ex = cx + side*int(8*size)
        ey = cy - int(4*size)
        pygame.draw.circle(surf, ecol, (ex,ey), int(3*size))
    # ноги
    for side in [-1, 1]:
        lx = cx + side*int(w//2)
        pygame.draw.line(surf, col,
                         (lx, cy+h//2),
                         (lx+side*int(6*size), cy+h//2+int(8*size)), 3)

# ── Вымогатель: замок + цепи ──────────────────────────────────
def draw_ransomware(surf, cx, cy, t, phase, size):
    col  = (200, 100, 10)
    glow = (255, 160, 30)
    r    = int(14*size)
    ang  = phase + t*0.02
    # свечение
    for gr, ga in [(r+9,25),(r+5,50),(r+1,90)]:
        gs = pygame.Surface((gr*2+4,gr*2+4), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*glow, ga), (gr+2,gr+2), gr)
        surf.blit(gs, (cx-gr-2,cy-gr-2))
    # тело — шестиугольник
    pts = []
    for i in range(6):
        a = ang + i*math.pi/3
        pts.append((cx+int(math.cos(a)*r), cy+int(math.sin(a)*r)))
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.polygon(surf, glow, pts, 2)
    # замок внутри
    lw, lh = int(10*size), int(8*size)
    pygame.draw.rect(surf, glow, (cx-lw//2, cy-lh//2+2, lw, lh), border_radius=2)
    # дуга замка
    pygame.draw.arc(surf, glow,
                    (cx-lw//2+1, cy-lh-1, lw-2, lh), 0, math.pi, 2)
    # цепи вращаются
    for i in range(4):
        ca = ang*2 + i*math.pi/2
        x1 = cx + int(math.cos(ca)*r)
        y1 = cy + int(math.sin(ca)*r)
        x2 = cx + int(math.cos(ca)*(r+9*size))
        y2 = cy + int(math.sin(ca)*(r+9*size))
        pygame.draw.line(surf, glow, (x1,y1),(x2,y2), 2)

# ── Рекламное ПО: кричащие цвета, баннер ─────────────────────
def draw_adware(surf, cx, cy, t, phase, size):
    col  = (200, 180, 0)
    glow = (255, 240, 40)
    # мигание быстрое — раздражает
    blink = int(t/200) % 2
    r = int(14*size)
    ang = phase + t*0.035
    # корпус — звезда (8 лучей)
    pts = []
    for i in range(16):
        a  = ang + i*math.pi/8
        ri = r if i%2==0 else int(r*0.55)
        pts.append((cx+int(math.cos(a)*ri), cy+int(math.sin(a)*ri)))
    bcol = glow if blink else col
    pygame.draw.polygon(surf, bcol, pts)
    pygame.draw.polygon(surf, (255,255,100), pts, 2)
    # «ADS» внутри
    font = pygame.font.SysFont(None, int(12*size))
    lbl  = font.render('ADS', True, (20,20,20) if blink else (255,255,200))
    surf.blit(lbl, lbl.get_rect(center=(cx,cy)))
    # восклицательные знаки летают
    for i in range(3):
        ea = ang*1.8 + i*math.pi*2/3
        ex = cx + int(math.cos(ea)*(r+10)*size)
        ey = cy + int(math.sin(ea)*(r+10)*size)
        f2 = pygame.font.SysFont(None, int(14*size))
        lbl2 = f2.render('!', True, glow)
        surf.blit(lbl2, lbl2.get_rect(center=(ex,ey)))

# ── Шпионское ПО: глаз ────────────────────────────────────────
def draw_spyware(surf, cx, cy, t, phase, size):
    col  = (140, 30, 140)
    glow = (200, 60, 200)
    r    = int(18*size)
    ang  = phase + t*0.02
    # миндалевидный глаз
    eye_w, eye_h = int(34*size), int(20*size)
    # свечение
    for ew, eh, a in [(eye_w+12, eye_h+8, 30),(eye_w+6, eye_h+4, 55),(eye_w, eye_h, 90)]:
        es = pygame.Surface((ew+4, eh+4), pygame.SRCALPHA)
        pygame.draw.ellipse(es, (*glow, a), (2,2,ew,eh))
        surf.blit(es, (cx-ew//2-2, cy-eh//2-2))
    # белок
    pygame.draw.ellipse(surf, (230,230,255), (cx-eye_w//2, cy-eye_h//2, eye_w, eye_h))
    # зрачок — смотрит в сторону движения
    pupil_x = cx + int(math.cos(ang*0.5)*4*size)
    pupil_y = cy + int(math.sin(ang*0.3)*2*size)
    pygame.draw.circle(surf, col, (pupil_x, pupil_y), int(7*size))
    pygame.draw.circle(surf, glow, (pupil_x, pupil_y), int(4*size))
    pygame.draw.circle(surf, (255,255,255), (pupil_x+2,pupil_y-2), int(2*size))
    # контур глаза
    pygame.draw.ellipse(surf, glow, (cx-eye_w//2, cy-eye_h//2, eye_w, eye_h), 2)
    # реснички
    for i in range(5):
        la = -0.6 + i*0.3
        lx1 = cx + int(math.cos(la)*(eye_w//2))
        ly1 = cy + int(math.sin(la)*(eye_h//2)) - eye_h//2
        pygame.draw.line(surf, glow, (lx1,ly1),(lx1,ly1-int(5*size)), 1)

