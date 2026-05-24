# ── settings.py ──────────────────────────────────────────────
white  = (255, 255, 255)
black  = (0,   0,   0  )
red    = (200, 0,   0  )
green  = (0,   200, 0  )
yellow = (255, 255, 0  )
orange = (255, 196, 0  )

# Цветовая схема: синий космос на чёрном
COL_BG          = (2,   4,  18)    # почти чёрный с синевой
COL_BG2         = (5,   10, 35)
COL_NEON        = (0,   180, 255)  # основной неон — синий
COL_NEON2       = (0,   100, 220)
COL_NEON_DIM    = (0,   60,  140)
COL_PLATFORM    = (10,  30,  80)
COL_PLAT_GLOW   = (0,   140, 255)
COL_ACCENT      = (0,   240, 200)  # бирюзовый акцент
COL_WARN        = (255, 80,  0  )
COL_DANGER      = (220, 0,   60 )

spritesheet_file_name = "spritesheet_jumper.png"
platform_colors = [(0,0,0),(200,0,0),(255,255,255),(0,200,0),(255,255,0),(255,196,0)]

display_width  = 500
display_height = 700
fps            = 60

player_Acc    = 0.7
player_Fric   = -0.13
gravity       = 0.38
jump_force    = -15          # быстрее прыжок

Font_Name = "scoreboard"
hs_file   = "highscore.txt"

power_up_boost      = -24
power_up_spawn_freq = 10

enemies_freq = 4500
cloud_layer  = 0

ATTACK_COOLDOWN  = 2000
ATTACK_DURATION  = 400
INVULN_DURATION  = 1500

# Платформы: базовое кол-во растёт с высотой
PLATFORM_BASE_COUNT = 8
