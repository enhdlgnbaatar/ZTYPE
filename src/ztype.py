import json
import math
import os
import random
import sys

import pygame
try:
    from wonderwords import RandomWord as _RW
    _rw = _RW()
    def _ww_words(min_l, max_l, count=80):
        try:
            return _rw.random_words(count, word_min_length=min_l, word_max_length=max_l)
        except Exception:
            return []
    _WW_AVAILABLE = True
except ImportError:
    _WW_AVAILABLE = False
    def _ww_words(min_l, max_l, count=80):
        return []


WIDTH  = 800
HEIGHT = 600
FPS    = 60

LANE_TOP     = 74
DANGER_Y     = 400
DEATH_LINE_Y = 550
SHIP_X = WIDTH  // 2
SHIP_Y = HEIGHT - 42

BLACK      = (4,   5,   14)
WHITE      = (232, 245, 255)
MUTED      = (95,  120, 150)
CYAN       = (0,   230, 255)
PINK       = (255, 55,  210)
GREEN      = (30,  255, 140)
YELLOW     = (255, 230, 70)
RED        = (255, 62,  88)
PURPLE     = (160, 80,  255)
ORANGE     = (255, 135, 45)

HIGHSCORE_FILE = "highscore.json"


def get_font_path():
    base_dir = os.path.dirname(__file__)
    bundled_fonts = [
        "NotoSans-Regular.ttf",
        "DejaVuSans.ttf",
        "arial.ttf",
    ]
    for filename in bundled_fonts:
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            return path

    system_fonts = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\seguiemj.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in system_fonts:
        if os.path.exists(path):
            return path

    for font_name in ("notosans", "dejavusans", "arialunicode", "arial"):
        matched_font = pygame.font.match_font(font_name)
        if matched_font:
            return matched_font

    raise FileNotFoundError(
        "Кирилл үсэг дэмждэг font олдсонгүй. ztype.py файлтай нэг хавтсанд "
        "NotoSans-Regular.ttf эсвэл arial.ttf хуулж тавина уу."
    )


_EN_FALLBACK_SHORT = [
    "bit","cpu","ram","code","node","loop","byte","ship","void","star",
    "grid","data","ping","core","wave","hack","port","flux","key","map",
    "net","run","set","arc","dot","hex","ion","jet","lab","max","ore",
    "ray","sky","ten","use","web","zen","aim","box","cut","dim","end",
]
_EN_FALLBACK_MEDIUM = [
    "python","pygame","matrix","cyber","rocket","plasma","vector","signal",
    "module","target","neon","system","orbit","kernel","render","shader",
    "syntax","packet","sensor","fusion","binary","cursor","daemon","engine",
    "filter","gadget","hacker","inject","jitter","keymap","legacy","memory",
    "neural","output","photon","quartz","reboot","server","turret","uplink",
]
_EN_FALLBACK_LONG = [
    "firewall","overload","interface","algorithm","hyperdrive","terminal",
    "protocol","subroutine","datastream","blackout","encryption","starship",
    "processor","navigation","transistor","collision","simulation","cybernetic",
    "bootstrap","broadcast","database","download","endpoint","firmware",
    "generate","hardware","language","malware","notebook","overflow","password",
]
_EN_FALLBACK_EXTREME = [
    "synchronizer","nanoprocess","cryptograph","interstellar","virtualization",
    "countermeasure","transmission","architecture","hypervelocity","microkernel",
    "parallelism","segmentation","optimization","computation","abstraction",
    "multithreading","initialization","interpolation","decompression",
    "authentication","authorization","configuration","orchestration",
]

def _build_en_pool(min_l, max_l, fallback):
    """wonderwords ашиглаж үг авна; байхгүй бол fallback."""
    words = _ww_words(min_l, max_l, count=120)
    if len(words) < 20:
        words = [w for w in fallback if min_l <= len(w) <= max_l]
        if not words:
            words = list(fallback)
    return list(set(words))   # давхардалт арилгах

_MN_FALLBACK = {
    "short": [
        "гэр", "уул", "гал", "мод", "нүд", "тал", "ус", "сар", "нар", "од", "гол",
        "зам", "ном", "гад", "мал", "хүн", "эм", "эр", "өв", "тар", "хол", "ойр",
        "тус", "юм", "буу", "хас", "нэг", "хоёр", "гурав", "дөрөв", "тав", "зургаа",
        "дагуу", "цус", "бүр", "аав", "ээж", "ах", "эгүү", "өв", "тар",
    ],
    "medium": [
        "баатар", "монгол", "зүрх", "нутаг", "дэлхий", "тэнгэр", "цагаан",
        "улаан", "хүрэн", "ногоон", "хөх", "сайхан", "удаан", "их", "бага",
        "гарах", "ирэх", "явах", "унших", "бичих", "цэцэг", "наран",
        "сарнай", "арслан", "бүргэд", "далай", "агаар", "баяраа", "энхжин",
        "солонго", "наранцэцэг", "гантөмөр", "энхболд", "доржпалам",
    ],
    "long": [
        "улаанбаатар", "дархан", "эрдэнэт", "чойбалсан", "баянхонгор",
        "өвөрхангай", "дорноговь", "хөвсгөл", "дундговь", "архангай",
        "сэлэнгэ", "завхан", "ховд", "увс", "сүхбаатар", "өмнөговь", "хэнтий",
        "монголын", "түүхийн", "дэлхийн", "хурдан", "цагаансар", "наадам",
        "эрдэнийн", "өдрийн", "өнөөдөр", "маргааш", "ирээдүй", "өдөр", "шөнө",
    ],
    "extreme": [
        "улаанбаатар-хот", "монголын-ардчилал", "хөндлөнгийн-барилга",
        "эрчим-хүчний-систем", "холбооны-гараг", "шинжлэх-ухааны",
        "боловсролын-яам", "эрүү-гурван-гол", "монголын-байгаль",
        "эрдэнийн-өндөр", "цагаан-агуй", "говь-талын-салхинд",
        "өндөр-уулын-оргил", "монголын-түүх", "баялгийн-газар",
    ],
}

def _load_mn_words():

    path = os.path.join(os.path.dirname(__file__), "words_mn.txt")
    if not os.path.isfile(path):
        return _MN_FALLBACK

    result = {"short": [], "medium": [], "long": [], "extreme": []}
    with open(path, encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if not w or w.startswith("#"):
                continue
            l = len(w)
            if l <= 5:
                result["short"].append(w)
            elif l <= 8:
                result["medium"].append(w)
            elif l <= 11:
                result["long"].append(w)
            else:
                result["extreme"].append(w)

    for cat in result:
        if len(result[cat]) < 10:
            result[cat] += _MN_FALLBACK[cat]
    return result


class InfiniteWordPool:
    def __init__(self, words):
        self._master = list(set(words)) if words else ["word"]
        self._deck   = []
        self._shuffle()

    def _shuffle(self):
        self._deck = list(self._master)
        random.shuffle(self._deck)

    def next(self):
        if not self._deck:
            self._shuffle()
        return self._deck.pop()


def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            data = json.load(f)
            return int(data.get("highscore", 0))
    except Exception:
        return 0

def save_highscore(score):
    try:
        current = load_highscore()
        if score > current:
            with open(HIGHSCORE_FILE, "w") as f:
                json.dump({"highscore": score}, f)
    except Exception:
        pass

class AudioManager:
    SOUNDS = {
        "laser":    "sfx_laser.wav",
        "explode":  "sfx_explode.wav",
        "bomb":     "sfx_bomb.wav",
        "levelup":  "sfx_levelup.wav",
        "wrong":    "sfx_wrong.wav",
        "combo":    "sfx_combo.wav",
    }

    def __init__(self):
        self._sounds = {}
        self._enabled = False
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._enabled = True
            for key, fname in self.SOUNDS.items():
                path = os.path.join(os.path.dirname(__file__), fname)
                if os.path.isfile(path):
                    try:
                        self._sounds[key] = pygame.mixer.Sound(path)
                    except Exception:
                        pass
        except Exception:
            pass

    def play(self, key, volume=0.7):
        if not self._enabled:
            return
        snd = self._sounds.get(key)
        if snd:
            try:
                snd.set_volume(volume)
                snd.play()
            except Exception:
                pass


_neon_cache: dict = {}   # (text, color, font_id) → (surface, rect_size)

def draw_neon_text(surface, font, text, color, center=None, topleft=None):

    cache_key = (text, color, id(font))
    if cache_key not in _neon_cache:
        core     = font.render(text, True, WHITE)
        colored  = font.render(text, True, color)
        w, h     = core.get_size()
        pad      = 12
        composite = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)

        # Glow давхаргууд
        for radius, alpha in [(5, 45), (2, 90)]:
            layer = pygame.Surface((w + radius * 4, h + radius * 4), pygame.SRCALPHA)
            layer.blit(colored, (radius * 2, radius * 2))
            layer.set_alpha(alpha)
            composite.blit(layer, (pad - radius * 2, pad - radius * 2))

        composite.blit(colored, (pad + 1, pad + 1))   # өнгөт shadow
        composite.blit(core,    (pad,     pad))        # цагаан core
        _neon_cache[cache_key] = composite

    surf = _neon_cache[cache_key]
    pad  = 12
    rect = surf.get_rect()
    if center is not None:
        rect.center = center
        rect.move_ip(-pad, -pad)
    else:
        rect.topleft = (topleft[0] - pad, topleft[1] - pad)
    surface.blit(surf, rect)
    # Буцах rect: pad-гүй хэсэг
    inner = pygame.Rect(rect.x + pad, rect.y + pad,
                        surf.get_width()  - pad * 2,
                        surf.get_height() - pad * 2)
    return inner


def draw_glow_line(surface, start, end, color, width):
    for extra_width, alpha in [(12, 45), (7, 70), (3, 120)]:
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(glow, color + (alpha,), start, end, width + extra_width)
        surface.blit(glow, (0, 0))
    pygame.draw.line(surface, color, start, end, width)
    pygame.draw.line(surface, WHITE, start, end, max(1, width // 2))


def clamp(value, low, high):
    return max(low, min(high, value))

class StarField:

    LAYERS = [
        {"count": 60, "size": 1, "speed": 18,  "color": MUTED},
        {"count": 40, "size": 2, "speed": 55,  "color": CYAN},
        {"count": 20, "size": 3, "speed": 130, "color": WHITE},
    ]

    def __init__(self):
        self.stars = []
        for layer in self.LAYERS:
            for _ in range(layer["count"]):
                self.stars.append({
                    "x":     random.randint(0, WIDTH),
                    "y":     random.randint(0, HEIGHT),
                    "speed": layer["speed"] + random.uniform(-5, 5),
                    "size":  layer["size"],
                    "color": layer["color"],
                })

    def update(self, dt):
        for s in self.stars:
            s["y"] += s["speed"] * dt
            if s["y"] > HEIGHT:
                s["y"] = 0
                s["x"] = random.randint(0, WIDTH)

    def draw(self, surface):
        for s in self.stars:
            pygame.draw.circle(surface, s["color"],
                               (int(s["x"]), int(s["y"])), s["size"])

class Spaceship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.engine_phase = 0

    def update(self, dt):
        self.engine_phase += dt * 10

    def nose(self):
        return (self.x, self.y - 33)

    def draw(self, surface):
        body    = [(self.x, self.y-34),(self.x-34, self.y+28),(self.x+34, self.y+28)]
        cockpit = [(self.x, self.y-16),(self.x-10,  self.y+12),(self.x+10,  self.y+12)]

        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(glow, CYAN + (52,), body)
        pygame.draw.polygon(glow, PINK + (35,),
            [(self.x, self.y-42),(self.x-46, self.y+36),(self.x+46, self.y+36)])
        surface.blit(glow, (0,0))

        pygame.draw.polygon(surface, (9,24,43), body)
        pygame.draw.polygon(surface, CYAN,  body,    2)
        pygame.draw.polygon(surface, GREEN, cockpit, 2)
        pygame.draw.line(surface, WHITE, (self.x, self.y-31),(self.x, self.y+16), 2)

        fh = 16 + int(math.sin(self.engine_phase)*5)
        flame = [(self.x-10, self.y+28),(self.x+10, self.y+28),(self.x, self.y+28+fh)]
        pygame.draw.polygon(surface, YELLOW, flame)
        pygame.draw.polygon(surface, PINK,   flame, 2)


class Word:
    def __init__(self, text, x, y, speed, shooter=False, shoot_interval=0):
        self.original_text  = text
        self.remaining_text = text
        self.x = x
        self.y = y
        self.speed          = speed
        self.targeted       = False
        self.shooter        = shooter
        self.shoot_interval = shoot_interval
        self.shoot_timer    = random.uniform(0.8, max(0.9, shoot_interval))
        self.wobble         = random.uniform(0, math.pi * 2)
        self.color          = random.choice([CYAN, PINK, GREEN, YELLOW, PURPLE])

        # Cache
        self._cached_text  = None
        self._cached_color = None
        self._cached_surf  = None   # glow layer
        self._cached_core  = None   # core text
        self._cached_shad  = None   # shadow text

    def _rebuild_cache(self, font, color):
        text = self.remaining_text
        core = font.render(text, True, WHITE)
        shad = font.render(text, True, color)
        w, h = core.get_size()

        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        rect = core.get_rect(center=(int(self.x), int(self.y)))
        for inflate, alpha in [(28, 30),(14, 60),(4, 110)]:
            box = rect.inflate(inflate, inflate // 2)
            pygame.draw.rect(glow, color + (alpha,), box, 1)
        if self.shooter:
            pygame.draw.circle(glow, ORANGE+(120,),(rect.left-16, rect.centery), 8, 2)
            pygame.draw.circle(glow, ORANGE+(120,),(rect.right+16,rect.centery), 8, 2)
        glow_text = font.render(text, True, color)
        glow.blit(glow_text, rect)
        glow.set_alpha(140)

        self._cached_text  = text
        self._cached_color = color
        self._cached_surf  = glow
        self._cached_core  = core
        self._cached_shad  = shad

    def update(self, dt):
        self.y += self.speed * dt
        self.wobble += dt * 3
        self.x += math.sin(self.wobble) * 0.18
        if self.shooter:
            self.shoot_timer -= dt

    def ready_to_fire(self):
        return (self.shooter and self.shoot_timer <= 0
                and LANE_TOP < self.y < DEATH_LINE_Y - 80)

    def reset_fire_timer(self):
        self.shoot_timer = self.shoot_interval

    def first_letter_matches(self, letter):
        return len(self.remaining_text) > 0 and self.remaining_text[0] == letter

    def type_letter(self, letter):
        if self.first_letter_matches(letter):
            hit_pos = (self.x - 8 * len(self.remaining_text), self.y)
            self.remaining_text = self.remaining_text[1:]
            self._cached_text = None   # cache-г хүчингүй болгоно
            return hit_pos
        return None

    def completed(self):
        return len(self.remaining_text) == 0

    def in_danger_zone(self):
        return self.y >= DANGER_Y

    def reached_death_line(self):
        return self.y >= DEATH_LINE_Y

    def draw(self, surface, font):
        color = GREEN if self.targeted else self.color
        if self.shooter:
            color = ORANGE if not self.targeted else RED
        if self.in_danger_zone() and not self.targeted:
            color = RED

        # Cache шалгана: текст эсвэл өнгө өөрчлөгдсөн бол дахин үүсгэнэ
        if self._cached_text != self.remaining_text or self._cached_color != color:
            self._rebuild_cache(font, color)

        cx, cy = int(self.x), int(self.y)
        rect = self._cached_core.get_rect(center=(cx, cy))
        surface.blit(self._cached_surf, (0, 0))
        surface.blit(self._cached_shad, rect.move(1, 1))
        surface.blit(self._cached_core, rect)

class Projectile:
    def __init__(self, letter, start_pos, target_pos, speed):
        self.letter = letter
        self.x = float(start_pos[0])
        self.y = float(start_pos[1])
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = max(1.0, math.sqrt(dx*dx + dy*dy))
        self.vx     = dx / dist * speed
        self.vy     = dy / dist * speed
        self.radius = 16
        self.trail  = []

    def update(self, dt):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)
        self.x += self.vx * dt
        self.y += self.vy * dt

    def matches(self, letter):
        return self.letter == letter

    def hit_ship(self, ship):
        dx = self.x - ship.x
        dy = self.y - ship.y
        return math.sqrt(dx*dx + dy*dy) <= 34

    def off_screen(self):
        return self.x < -40 or self.x > WIDTH+40 or self.y < -40 or self.y > HEIGHT+40

    def draw(self, surface, font):
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i, pos in enumerate(self.trail):
            alpha = int(25 + i * 18)
            pygame.draw.circle(layer, PINK+(alpha,),(int(pos[0]),int(pos[1])),5+i//2)
        pygame.draw.circle(layer, RED+(80,),    (int(self.x),int(self.y)), self.radius+8)
        pygame.draw.circle(layer, YELLOW+(180,),(int(self.x),int(self.y)), self.radius, 2)
        surface.blit(layer, (0,0))
        draw_neon_text(surface, font, self.letter.upper(), YELLOW,
                       center=(int(self.x), int(self.y)))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def burst(self, pos, count, color, power, size_range):
        for _ in range(count):
            angle = random.uniform(0, math.pi*2)
            speed = random.uniform(power*0.35, power)
            self.particles.append({
                "x": pos[0], "y": pos[1],
                "vx": math.cos(angle)*speed,
                "vy": math.sin(angle)*speed,
                "life":     random.uniform(0.35, 0.9),
                "max_life": random.uniform(0.55, 1.0),
                "size":  random.randint(size_range[0], size_range[1]),
                "color": color,
            })

    def update(self, dt):
        alive = []
        for p in self.particles:
            p["life"] -= dt
            p["x"]   += p["vx"] * dt
            p["y"]   += p["vy"] * dt
            p["vy"]  += 70 * dt
            p["vx"]  *= 0.985
            if p["life"] > 0:
                alive.append(p)
        self.particles = alive

    def draw(self, surface):
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for p in self.particles:
            alpha = int(255 * clamp(p["life"] / p["max_life"], 0, 1))
            color = p["color"] + (alpha,)
            pos   = (int(p["x"]), int(p["y"]))
            pygame.draw.circle(layer, color, pos, p["size"]+3)
            pygame.draw.circle(layer, WHITE+(alpha,), pos, max(1, p["size"]//2))
        surface.blit(layer, (0,0))


class BombEffect:
    def __init__(self):
        self.active   = False
        self.time     = 0
        self.duration = 0.42
        self.radius   = 0

    def trigger(self):
        self.active = True
        self.time   = 0
        self.radius = 0

    def update(self, dt):
        if not self.active:
            return
        self.time  += dt
        self.radius = 70 + 760 * (self.time / self.duration)
        if self.time >= self.duration:
            self.active = False

    def shake_offset(self):
        if not self.active:
            return (0, 0)
        strength = int(12 * (1 - self.time / self.duration))
        return (random.randint(-strength, strength), random.randint(-strength, strength))

    def draw(self, surface, origin):
        if not self.active:
            return
        ratio = 1 - self.time / self.duration
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(4):
            radius = int(self.radius - i * 22)
            if radius > 0:
                alpha = int(120 * ratio / (i + 1))
                pygame.draw.circle(layer, CYAN+(alpha,), origin, radius, 3)
                pygame.draw.circle(layer, PINK+(alpha,), origin, radius+8, 1)
        surface.blit(layer, (0,0))


class WrongFlash:
    def __init__(self):
        self.life     = 0.0
        self.duration = 0.22

    def trigger(self):
        self.life = self.duration

    def update(self, dt):
        if self.life > 0:
            self.life = max(0.0, self.life - dt)

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(180 * (self.life / self.duration))
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # Ирмэгийг улаанаар будна (4 тал)
        thickness = 22
        layer.fill((255, 30, 30, alpha), (0,            0, WIDTH, thickness))
        layer.fill((255, 30, 30, alpha), (0, HEIGHT-thickness, WIDTH, thickness))
        layer.fill((255, 30, 30, alpha), (0,            0, thickness, HEIGHT))
        layer.fill((255, 30, 30, alpha), (WIDTH-thickness, 0, thickness, HEIGHT))
        surface.blit(layer, (0, 0))


class ComboSystem:

    THRESHOLDS = [0, 10, 25, 50, 100]   # streak ийн босго
    MAX_MULTI  = 5

    def __init__(self):
        self.streak     = 0    # дараалсан зөв үсгийн тоо
        self.multiplier = 1
        self.anim_t     = 0.0  # multiplier ахиулсны дараа flash анимаци

    def hit(self):
        """Зөв үсэг — streak нэмнэ, multiplier шалгана."""
        self.streak += 1
        old = self.multiplier
        for i, thresh in enumerate(self.THRESHOLDS):
            if self.streak >= thresh:
                self.multiplier = i + 1
        self.multiplier = min(self.multiplier, self.MAX_MULTI)
        if self.multiplier > old:
            self.anim_t = 0.5   # UI flash

    def miss(self):
        """Буруу үсэг — бүгдийг тэгэлнэ."""
        self.streak     = 0
        self.multiplier = 1

    def apply(self, base_score):
        return base_score * self.multiplier

    def update(self, dt):
        if self.anim_t > 0:
            self.anim_t = max(0.0, self.anim_t - dt)


def lerp(a, b, t):
    return a + (b - a) * clamp(t, 0.0, 1.0)


def draw_corner_frame(surface, rect, color, alpha=190, corner=22, width=2):
    layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    x, y, w, h = rect
    c = color + (alpha,)
    pts = [
        ((x, y + corner), (x, y), (x + corner, y)),
        ((x + w - corner, y), (x + w, y), (x + w, y + corner)),
        ((x, y + h - corner), (x, y + h), (x + corner, y + h)),
        ((x + w - corner, y + h), (x + w, y + h), (x + w, y + h - corner)),
    ]
    for a, b, d in pts:
        pygame.draw.line(layer, c, a, b, width)
        pygame.draw.line(layer, c, b, d, width)
    surface.blit(layer, (0, 0))


def draw_segmented_bar(surface, rect, value, color, segments=24):
    x, y, w, h = rect
    pygame.draw.rect(surface, (24, 34, 58), rect, 1)
    gap = 3
    seg_w = (w - gap * (segments - 1)) / float(segments)
    filled = value * segments
    for i in range(segments):
        sx = int(x + i * (seg_w + gap))
        sw = max(2, int(seg_w))
        active = i + 1 <= filled
        partial = clamp(filled - i, 0, 1)
        if active or partial > 0:
            alpha = int(70 + 150 * partial)
            layer = pygame.Surface((sw, h), pygame.SRCALPHA)
            layer.fill(color + (alpha,))
            surface.blit(layer, (sx, y))
            pygame.draw.rect(surface, WHITE, (sx, y, sw, h), 1)
        else:
            pygame.draw.rect(surface, (35, 45, 68), (sx, y, sw, h), 1)


def draw_glitch_text(surface, font, text, color, center=None, topleft=None, intensity=4, ticks=0):
    rect = font.render(text, True, color).get_rect()
    if center:
        rect.center = center
    else:
        rect.topleft = topleft
    offsets = [(-intensity, 0, RED), (intensity, 1, CYAN), (0, 0, color)]
    for ox, oy, col in offsets:
        jitter = int(math.sin(ticks * 0.018 + ox * 3) * max(1, intensity // 2))
        img = font.render(text, True, col)
        surface.blit(img, rect.move(ox + jitter, oy))
    draw_neon_text(surface, font, text, color, center=rect.center)


class UI:
    def __init__(self):
        font_path = get_font_path()
        self.font_path = font_path
        self.font  = pygame.font.Font(font_path, 18)
        self.font.set_bold(True)
        self.small = pygame.font.Font(font_path, 14)
        self.big   = pygame.font.Font(font_path, 44)
        self.big.set_bold(True)
        self.mega  = pygame.font.Font(font_path, 58)
        self.mega.set_bold(True)
        self.combo_font = pygame.font.Font(font_path, 28)
        self.combo_font.set_bold(True)
        self.display_score = 0.0
        self.display_wpm = 0.0
        self.display_progress = 0.0
        self.last_ticks = pygame.time.get_ticks()
        self.scanlines = self._make_scanlines()
        self.grid = self._make_grid()

    def _make_scanlines(self):
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(layer, (255, 255, 255, 18), (0, y), (WIDTH, y))
        return layer

    def _make_grid(self):
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x in range(0, WIDTH, 40):
            pygame.draw.line(layer, CYAN + (18,), (x, 70), (x, HEIGHT))
        for y in range(72, HEIGHT, 40):
            pygame.draw.line(layer, PURPLE + (16,), (0, y), (WIDTH, y))
        return layer

    def frame_gameplay(self, surface):
        surface.blit(self.grid, (0, 0))
        draw_corner_frame(surface, (10, 76, WIDTH - 20, HEIGHT - 92), CYAN, 120, 34, 2)
        draw_neon_text(surface, self.small, "[ HUD ]", CYAN, topleft=(20, 76))
        draw_neon_text(surface, self.small, "[ COMBAT AREA ]", MUTED, topleft=(WIDTH - 150, 76))

    def draw_crt_overlay(self, surface, critical=False):
        surface.blit(self.scanlines, (0, 0))
        if critical:
            ticks = pygame.time.get_ticks()
            for _ in range(5):
                y = random.randint(0, HEIGHT - 3)
                color = random.choice([RED, CYAN, PINK])
                pygame.draw.line(surface, color, (0, y), (WIDTH, y + random.randint(-1, 1)), 1)
            if ticks % 140 < 70:
                glitch = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                glitch.fill((255, 40, 80, 18))
                surface.blit(glitch, (random.randint(-3, 3), 0))

    def draw_panel(self, surface):
        panel = pygame.Surface((WIDTH, 76), pygame.SRCALPHA)
        panel.fill((5, 9, 24, 230))
        pygame.draw.line(panel, CYAN+(170,), (0, 74), (WIDTH, 74), 2)
        pygame.draw.line(panel, PINK+(80,), (0, 70), (WIDTH, 70), 1)
        surface.blit(panel, (0,0))
        draw_corner_frame(surface, (8, 8, WIDTH - 16, 58), CYAN, 150, 18, 2)
        draw_neon_text(surface, self.small, "[ SHIP DASHBOARD ]", MUTED, topleft=(18, 8))

    def draw_progress(self, surface, progress):
        x, y, w, h = 272, 34, 286, 14
        draw_neon_text(surface, self.small, "LEVEL SYNC", MUTED, topleft=(272, 14))
        draw_segmented_bar(surface, (x, y, w, h), progress, GREEN, 26)
        pulse_x = x + int(w * clamp(progress, 0, 1))
        pygame.draw.circle(surface, CYAN, (pulse_x, y + h // 2), 4)
        pygame.draw.line(surface, CYAN, (x, y+h+6),(x+w, y+h+6), 1)

    def draw_bombs(self, surface, bombs):
        base_x = 596
        draw_neon_text(surface, self.small, "PANIC CORE", YELLOW, topleft=(base_x, 12))
        for i in range(3):
            x = base_x + 20 + i*38
            y = 43
            color = YELLOW if i < bombs else (55, 55, 70)
            glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow, color+(70,), (x, y), 15)
            surface.blit(glow, (0,0))
            pygame.draw.circle(surface, color, (x, y), 14, 2)
            tri = [(x, y - 10), (x - 10, y + 8), (x + 10, y + 8)]
            pygame.draw.polygon(surface, color, tri, 2)
            pygame.draw.line(surface, PINK if i < bombs else MUTED, (x, y-5),(x, y+6), 1)

    def draw_combo(self, surface, combo):
        if combo.multiplier <= 1 and combo.streak == 0:
            return
        mx = combo.multiplier
        color = [GREEN, CYAN, YELLOW, ORANGE, PINK][mx - 1]
        ticks = pygame.time.get_ticks()
        pulse = 1.0 + 0.10 * math.sin(ticks * 0.018)
        shake = 0
        if mx >= 5:
            shake = random.randint(-3, 3)
        if combo.anim_t > 0:
            scale = pulse + 0.45 * (combo.anim_t / 0.5)
            fnt = pygame.font.Font(self.font_path, int(28*scale))
        else:
            fnt = pygame.font.Font(self.font_path, int(28*pulse))
        fnt.set_bold(True)
        label = f"x{mx}  COMBO"
        streak_label = f"streak  {combo.streak}"
        cx, cy = WIDTH - 95 + shake, HEIGHT - 82 + shake
        for i in range(min(12, combo.streak // 2)):
            ang = ticks * 0.006 + i
            px = cx + int(math.cos(ang) * (54 + i * 2))
            py = cy + int(math.sin(ang) * 20)
            pygame.draw.circle(surface, color, (px, py), 2)
        draw_corner_frame(surface, (WIDTH - 194, HEIGHT - 126, 174, 92), color, 150, 16, 2)
        draw_neon_text(surface, fnt, label, color, center=(cx, cy))
        draw_neon_text(surface, self.small, streak_label, MUTED,
                       center=(WIDTH - 95, HEIGHT - 55))

    def draw(self, surface, game):
        now = pygame.time.get_ticks()
        dt = max(0.001, (now - self.last_ticks) / 1000.0)
        self.last_ticks = now
        self.display_score = lerp(self.display_score, game.score, min(1.0, dt * 8))
        self.display_wpm = lerp(self.display_wpm, game.current_wpm(), min(1.0, dt * 6))
        self.display_progress = lerp(self.display_progress, game.level_progress(), min(1.0, dt * 7))

        self.draw_panel(surface)
        draw_neon_text(surface, self.font,  f"LVL {game.level:02d}", CYAN,  topleft=(20,  28))
        draw_neon_text(surface, self.font,  f"SCORE {int(self.display_score):06d}", GREEN, topleft=(104, 28))
        draw_neon_text(surface, self.font,  f"WPM {int(self.display_wpm):03d}", PINK,  topleft=(704, 34))
        draw_neon_text(surface, self.small, f"HI {game.highscore}", YELLOW, topleft=(704, 14))
        self.draw_progress(surface, self.display_progress)
        self.draw_bombs(surface, game.bombs)
        self.draw_combo(surface, game.combo)

    def draw_level_up(self, surface, level, countdown):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 10, 20, 178))
        surface.blit(overlay, (0,0))
        ticks = pygame.time.get_ticks()
        scan_y = int((1.0 - clamp(countdown / 2.5, 0, 1)) * HEIGHT)
        for y in range(0, HEIGHT, 18):
            pygame.draw.line(surface, CYAN if y < scan_y else PURPLE, (0, y), (WIDTH, y), 1)
        pygame.draw.rect(surface, GREEN, (90, 220, 620, 112), 2)
        draw_corner_frame(surface, (90, 220, 620, 112), CYAN, 220, 32, 3)
        draw_glitch_text(surface, self.big, "SYSTEM UPGRADE COMPLETE", GREEN,
                         center=(WIDTH//2, 258), intensity=5, ticks=ticks)
        draw_neon_text(surface, self.font, f"LEVEL {level:02d} ONLINE  //  {max(0.0, countdown):.1f}s",
                       YELLOW, center=(WIDTH//2, 310))

    def draw_game_over(self, surface, game):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 215))
        surface.blit(overlay, (0,0))
        ticks = pygame.time.get_ticks()
        draw_corner_frame(surface, (104, 116, 592, 366), RED, 230, 34, 3)
        pygame.draw.rect(surface, (9, 14, 30), (122, 138, 556, 326))
        pygame.draw.rect(surface, CYAN, (122, 138, 556, 326), 1)
        draw_glitch_text(surface, self.big, "CRITICAL SYSTEM FAILURE", RED,
                         center=(WIDTH//2, 178), intensity=6, ticks=ticks)
        draw_neon_text(surface, self.small, "[ DIAGNOSTIC REPORT // PILOT TERMINAL ]",
                       MUTED, center=(WIDTH//2, 216))
        rows = [
            ("FINAL SCORE", f"{game.score}"),
            ("HIGH SCORE", f"{game.highscore}"),
            ("LEVEL REACHED", f"{game.level}"),
            ("PEAK WPM", f"{getattr(game, 'peak_wpm', game.current_wpm())}"),
            ("ACCURACY", "{:.1f}%".format(game.accuracy())),
            ("WORDS DESTROYED", f"{game.total_destroyed}"),
        ]
        x0, y0, rw, rh = 190, 246, 420, 28
        for i, (key, val) in enumerate(rows):
            y = y0 + i * rh
            pygame.draw.rect(surface, (18, 24, 44), (x0, y, rw, rh - 3), 1)
            draw_neon_text(surface, self.small, key, MUTED, topleft=(x0 + 12, y + 5))
            draw_neon_text(surface, self.small, val, WHITE, topleft=(x0 + 265, y + 5))
        new_hi = game.score >= game.highscore and game.score > 0
        if new_hi:
            draw_neon_text(surface, self.font, "NEW HIGH SCORE", YELLOW, center=(WIDTH//2, 430))
        pulse = 1.0 + 0.10 * math.sin(ticks * 0.012)
        prompt_font = pygame.font.Font(self.font_path, int(18 * pulse))
        prompt_font.set_bold(True)
        draw_neon_text(surface, prompt_font, "PRESS [R] TO REBOOT SYSTEM",
                       YELLOW, center=(WIDTH//2, 456))

# ──────────────────────────────────────────────────────
#  MAIN MENU
# ──────────────────────────────────────────────────────
class MainMenu:
    def __init__(self, screen, clock, starfield):
        self.screen    = screen
        self.clock     = clock
        self.starfield = starfield
        font_path = get_font_path()
        self.font_title = pygame.font.Font(font_path, 52)
        self.font_title.set_bold(True)
        self.font_sub   = pygame.font.Font(font_path, 22)
        self.font_sub.set_bold(True)
        self.font_hint  = pygame.font.Font(font_path, 15)
        self.selected   = 0
        self.blink_t    = 0.0
        self.highscore  = load_highscore()
        self.ui_fx      = UI()
        self.hover_mix  = [0.0, 0.0]

    def _draw_bg(self):
        self.screen.fill(BLACK)
        self.starfield.draw(self.screen)
        ticks = pygame.time.get_ticks()
        horizon = 110 + int(math.sin(ticks * 0.0015) * 4)
        for y in range(horizon, HEIGHT, 34):
            alpha_color = (16, 95, 120) if y % 68 == 0 else (18, 42, 74)
            pygame.draw.line(self.screen, alpha_color, (0,y),(WIDTH,y),1)
        slide = int((ticks * 0.03) % 70)
        for x in range(-WIDTH + slide, WIDTH*2, 70):
            pygame.draw.line(self.screen, (34,24,82),(WIDTH//2,horizon),(x,HEIGHT),1)
        draw_corner_frame(self.screen, (54, 54, WIDTH - 108, HEIGHT - 108), CYAN, 90, 40, 2)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.blink_t += dt
            self.starfield.update(dt)
            mouse = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    for i, rect in enumerate([pygame.Rect(144, 260, 236, 72), pygame.Rect(420, 260, 236, 72)]):
                        if rect.collidepoint(event.pos):
                            self.selected = i
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.Rect(144, 260, 236, 72).collidepoint(event.pos):
                        return "en"
                    if pygame.Rect(420, 260, 236, 72).collidepoint(event.pos):
                        return "mn"
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_TAB):
                        self.selected ^= 1
                    elif event.key == pygame.K_RETURN:
                        return "en" if self.selected == 0 else "mn"
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    elif event.key == pygame.K_1:
                        return "en"
                    elif event.key == pygame.K_2:
                        return "mn"

            self._draw_bg()
            ticks = pygame.time.get_ticks()
            draw_glitch_text(self.screen, self.font_title,
                             "CYBERPUNK  Z-TYPE", CYAN, center=(WIDTH//2, 128),
                             intensity=3 + (2 if ticks % 900 < 90 else 0), ticks=ticks)
            if self.highscore > 0:
                draw_neon_text(self.screen, self.font_hint,
                               f"BEST SCORE : {self.highscore}", YELLOW,
                               center=(WIDTH//2, 185))
            draw_neon_text(self.screen, self.font_sub,
                           "[ SELECT LANGUAGE ]  //  [ ХЭЛ СОНГОНО УУ ]",
                           MUTED, center=(WIDTH//2, 215))

            options = [("1  ENGLISH","en"),("2  МОНГОЛ","mn")]
            btn_w, btn_h, gap = 236, 72, 40
            start_x = 144

            for i, (label, _) in enumerate(options):
                bx = start_x + i*(btn_w+gap)
                by = 260
                rect = pygame.Rect(bx, by, btn_w, btn_h)
                chosen = (self.selected == i) or rect.collidepoint(mouse)
                self.hover_mix[i] = lerp(self.hover_mix[i], 1.0 if chosen else 0.0, dt * 8)
                bc = CYAN if chosen else MUTED
                fa = int(35 + 90 * self.hover_mix[i])
                fill = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                fill.fill((0,200,255,fa) if chosen else (50,50,80,35))
                self.screen.blit(fill, rect)
                pygame.draw.rect(self.screen, bc, rect, 1)
                slide = int(18 * self.hover_mix[i])
                draw_corner_frame(self.screen, (bx - slide, by - slide//2, btn_w + slide*2, btn_h + slide), bc, 190, 22, 2)
                draw_neon_text(self.screen, self.font_sub, label,
                               WHITE if chosen else MUTED,
                               center=rect.center)

            if int(self.blink_t*2) % 2 == 0:
                draw_neon_text(self.screen, self.font_hint,
                               "[← →] NAVIGATE      [ENTER] CONFIRM",
                               YELLOW, center=(WIDTH//2, 370))

            hints = [
                ("TYPE letters", "destroy falling words"),
                ("ENTER",        "use BOMB (clears danger zone)"),
                ("ESC",          "quit"),
            ]
            y0 = 410
            for k, v in hints:
                draw_neon_text(self.screen, self.font_hint,
                               f"{k:<14}  {v}", MUTED, center=(WIDTH//2, y0))
                y0 += 22

            self.ui_fx.draw_crt_overlay(self.screen, critical=False)
            pygame.display.flip()

# ──────────────────────────────────────────────────────
#  GAME
# ──────────────────────────────────────────────────────
class Game:
    LEVEL_UP_PAUSE = 2.5

    def __init__(self, language="en", starfield=None):
        pygame.init()
        pygame.display.set_caption("Cyberpunk ZType  v3")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock  = pygame.time.Clock()

        self.language  = language
        self.starfield = starfield or StarField()
        self.ship      = Spaceship(SHIP_X, SHIP_Y)
        self.particles = ParticleSystem()
        self.bomb_effect = BombEffect()
        self.wrong_flash = WrongFlash()
        self.combo       = ComboSystem()
        self.audio       = AudioManager()
        self.ui          = UI()

        font_path = get_font_path()
        self.word_font       = pygame.font.Font(font_path, 26)
        self.word_font.set_bold(True)
        self.projectile_font = pygame.font.Font(font_path, 22)
        self.projectile_font.set_bold(True)

        self.highscore = load_highscore()
        self._build_pools()
        self.reset()

    # ── Pools ────────────────────────────────
    def _build_pools(self):
        if self.language == "en":
            self._pool_short   = InfiniteWordPool(_build_en_pool(3,  5,  _EN_FALLBACK_SHORT))
            self._pool_medium  = InfiniteWordPool(_build_en_pool(5,  8,  _EN_FALLBACK_MEDIUM))
            self._pool_long    = InfiniteWordPool(_build_en_pool(8,  11, _EN_FALLBACK_LONG))
            self._pool_extreme = InfiniteWordPool(_build_en_pool(11, 16, _EN_FALLBACK_EXTREME))
        else:
            mn = _load_mn_words()
            self._pool_short   = InfiniteWordPool(mn["short"])
            self._pool_medium  = InfiniteWordPool(mn["medium"])
            self._pool_long    = InfiniteWordPool(mn["long"])
            self._pool_extreme = InfiniteWordPool(mn["extreme"])

    # ── Reset ────────────────────────────────
    def reset(self):
        self.words       = []
        self.projectiles = []
        self.lasers      = []
        self.target      = None
        self.score       = 0
        self.level       = 1
        self.destroyed_this_level = 0
        self.total_destroyed      = 0
        self.bombs       = 3
        self.spawn_timer = 0
        self.shooters_spawned_this_level = 0
        self.game_over   = False
        self.typed_chars = 0
        self.correct_chars = 0
        self.attempted_chars = 0
        self.peak_wpm = 0
        self.start_ticks = pygame.time.get_ticks()
        self.bomb_effect.active = False
        self.wrong_flash = WrongFlash()
        self.combo       = ComboSystem()
        self.used_words_this_level: set = set()
        self.level_up_pause = False
        self.level_up_timer = 0.0

    # ── Level тооцоо ─────────────────────────
    def words_needed_for_level(self):
        return self.level * 5

    def level_progress(self):
        return float(self.destroyed_this_level) / self.words_needed_for_level()

    def current_wpm(self):
        elapsed = max((pygame.time.get_ticks() - self.start_ticks) / 60000.0, 0.01)
        return int((self.typed_chars / 5.0) / elapsed)

    def accuracy(self):
        if self.attempted_chars <= 0:
            return 100.0
        return 100.0 * float(self.correct_chars) / float(self.attempted_chars)

    # ── Difficulty ───────────────────────────
    def difficulty(self):
        lv = self.level
        if lv <= 3:
            return {"word_speed": 26+lv*5, "spawn_interval": 2.15-lv*0.15,
                    "simultaneous":1,"word_min":3,"word_max":5,
                    "shooter_quota":0,"shooter_interval":0,"projectile_speed":0}
        if lv <= 7:
            t = lv - 4
            return {"word_speed": 46+t*9,
                    "spawn_interval": max(1.05, 1.45-t*0.09),
                    "simultaneous":1,"word_min":4,"word_max":7,
                    "shooter_quota":1,
                    "shooter_interval": random.uniform(2.7, 3.8),
                    "projectile_speed": 135+t*15}
        if lv <= 10:
            t = lv - 8
            panic = 2.25 if lv == 10 else 1.0
            return {"word_speed": (74+t*12)*panic,
                    "spawn_interval": max(0.34 if lv==10 else 0.72, 0.86-t*0.08),
                    "simultaneous": 2,
                    "word_min":6,"word_max":11,
                    "shooter_quota":2,"shooter_interval":1.95,
                    "projectile_speed": 190+t*26}
        e = lv - 10
        return {"word_speed": 235+e*14,
                "spawn_interval": max(0.24, 0.42-e*0.004),
                "simultaneous": min(4, 2+e//5),
                "word_min":7,"word_max":13,
                "shooter_quota": 2+e//6,
                "shooter_interval": max(1.35, 1.85-e*0.018),
                "projectile_speed": 235+e*9}

    # ── Word pick ────────────────────────────
    def _pick(self, pool, min_l, max_l):
        for _ in range(30):
            w = pool.next()
            if min_l <= len(w) <= max_l and w not in self.used_words_this_level:
                self.used_words_this_level.add(w)
                return w
        self.used_words_this_level.clear()
        return pool.next()

    def _pool_for(self, min_l, max_l):
        if max_l <= 5:  return self._pool_short
        if max_l <= 8:  return self._pool_medium
        if max_l <= 11: return self._pool_long
        return self._pool_extreme

    def choose_word(self):
        s = self.difficulty()
        return self._pick(self._pool_for(s["word_min"], s["word_max"]),
                          s["word_min"], s["word_max"])

    def choose_shooter_word(self):
        s    = self.difficulty()
        mn_l = max(s["word_min"]+1, 6)
        pool = self._pool_long if s["word_max"] >= 8 else self._pool_medium
        return self._pick(pool, mn_l, s["word_max"])

    def spawn_x_for_text(self, text):
        word_width, _ = self.word_font.size(text)
        margin = max(70, word_width // 2 + 24)
        if margin >= WIDTH // 2:
            return WIDTH // 2
        return random.randint(margin, WIDTH - margin)

    # ── Spawn ────────────────────────────────
    def spawn_word(self):
        s = self.difficulty()
        for _ in range(s["simultaneous"]):
            is_shooter = self.shooters_spawned_this_level < s["shooter_quota"]
            text  = self.choose_shooter_word() if is_shooter else self.choose_word()
            x     = self.spawn_x_for_text(text)
            y     = random.randint(-50, -16)
            speed = s["word_speed"] + random.uniform(-5, 12)
            if is_shooter:
                self.shooters_spawned_this_level += 1
                speed *= 0.92
                self.words.append(Word(text, x, y, speed,
                                       shooter=True, shoot_interval=s["shooter_interval"]))
            else:
                self.words.append(Word(text, x, y, speed))

    # ── Targeting & Shooting ─────────────────
    def lock_target(self, letter):
        matches = [w for w in self.words if w.first_letter_matches(letter)]
        if not matches:
            # Буруу оролдлого — combo алдана, flash
            self.combo.miss()
            self.wrong_flash.trigger()
            self.audio.play("wrong", 0.5)
            return
        self.target = max(matches, key=lambda w: w.y)
        self.target.targeted = True
        self.shoot(letter)

    def shoot(self, letter):
        if self.target is None:
            return
        hit_pos = self.target.type_letter(letter)
        if hit_pos is None:
            # Буруу үсэг (target байгаа ч таарахгүй)
            self.combo.miss()
            self.wrong_flash.trigger()
            self.audio.play("wrong", 0.5)
            return

        self.combo.hit()
        self.typed_chars += 1
        self.correct_chars += 1
        self.audio.play("laser", 0.6)

        self.lasers.append({"from": self.ship.nose(),
                            "to":   (int(self.target.x), int(self.target.y)),
                            "life": 0.11})
        self.particles.burst(hit_pos, random.randint(5,10),
                             random.choice([CYAN,PINK,GREEN,YELLOW]), 145, (1,3))

        if self.target.completed():
            self.destroy_word(self.target, bomb=False)
            self.target = None

    def fire_projectile_from(self, word):
        s      = self.difficulty()
        letter = random.choice("abcdefghijklmnopqrstuvwxyz")
        start  = (int(word.x), int(word.y+18))
        self.projectiles.append(Projectile(letter, start, self.ship.nose(),
                                           s["projectile_speed"]))
        self.particles.burst(start, 12, ORANGE, 120, (1,3))
        word.reset_fire_timer()

    def try_destroy_projectile(self, letter):
        matches = [p for p in self.projectiles if p.matches(letter)]
        if not matches:
            return False
        proj = max(matches, key=lambda p: p.y)
        self.projectiles.remove(proj)
        self.combo.hit()
        self.typed_chars += 1
        self.correct_chars += 1
        base = 18 + self.level * 3
        self.score += self.combo.apply(base)
        self.audio.play("laser", 0.6)
        self.particles.burst((proj.x, proj.y), 22, YELLOW, 210, (1,4))
        self.lasers.append({"from": self.ship.nose(),
                            "to":   (int(proj.x), int(proj.y)),
                            "life": 0.10})
        return True

    def destroy_word(self, word, bomb):
        pos   = (word.x, word.y)
        count = 46 if not bomb else 34
        self.particles.burst(pos, count,
                             random.choice([CYAN,PINK,GREEN,YELLOW,RED]), 250, (1,4))
        if word in self.words:
            self.words.remove(word)
        if not bomb:
            base = len(word.original_text)*10 + self.level*8
            self.score += self.combo.apply(base)
            self.audio.play("explode", 0.7)
            self.destroyed_this_level += 1
            self.total_destroyed      += 1
            self.check_level_up()

    def check_level_up(self):
        if self.destroyed_this_level >= self.words_needed_for_level():
            self.level  += 1
            self.score  += self.level * 75
            self.projectiles  = []
            self.words        = []
            self.target       = None
            self.shooters_spawned_this_level = 0
            self.destroyed_this_level        = 0
            self.used_words_this_level       = set()
            self.level_up_pause = True
            self.level_up_timer = self.LEVEL_UP_PAUSE
            self.spawn_timer    = 0
            self.particles.burst((WIDTH//2,120), 80, CYAN, 320, (2,5))
            self.audio.play("levelup", 0.9)

    def use_bomb(self):
        if self.bombs <= 0:
            return
        self.bombs -= 1
        self.bomb_effect.trigger()
        self.audio.play("bomb", 1.0)
        danger = [w for w in self.words if w.in_danger_zone()]
        for p in list(self.projectiles):
            self.particles.burst((p.x, p.y), 18, YELLOW, 180, (1,3))
        self.projectiles = []
        for word in danger:
            if word == self.target:
                self.target = None
            self.score += max(20, len(word.original_text)*4)
            self.destroy_word(word, bomb=True)

    # ── Events ───────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type != pygame.KEYDOWN:
                continue

            if self.game_over:
                if event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                continue

            if self.level_up_pause:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                continue

            if event.key == pygame.K_RETURN:
                self.use_bomb(); continue
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

            letter = event.unicode.lower()
            if len(letter) != 1 or not letter.isalpha():
                continue
            self.attempted_chars += 1
            if self.try_destroy_projectile(letter):
                continue
            if self.target is None:
                self.lock_target(letter)
            else:
                self.shoot(letter)

    # ── Update ───────────────────────────────
    def update(self, dt):
        self.starfield.update(dt)
        self.ship.update(dt)
        self.particles.update(dt)
        self.bomb_effect.update(dt)
        self.wrong_flash.update(dt)
        self.combo.update(dt)
        self.peak_wpm = max(self.peak_wpm, self.current_wpm())

        if self.level_up_pause:
            self.level_up_timer -= dt
            if self.level_up_timer <= 0:
                self.level_up_pause = False
            return

        for proj in list(self.projectiles):
            proj.update(dt)
            if proj.hit_ship(self.ship):
                self.game_over = True
                self.particles.burst((proj.x, proj.y), 60, RED, 320, (2,5))
            elif proj.off_screen():
                self.projectiles.remove(proj)

        for laser in self.lasers:
            laser["life"] -= dt
        self.lasers = [l for l in self.lasers if l["life"] > 0]

        if self.game_over:
            save_highscore(self.score)
            if self.score > self.highscore:
                self.highscore = self.score
            return

        s = self.difficulty()
        self.spawn_timer += dt
        if self.spawn_timer >= s["spawn_interval"]:
            self.spawn_timer = 0
            self.spawn_word()

        for word in list(self.words):
            word.update(dt)
            if word.ready_to_fire():
                self.fire_projectile_from(word)
            if word.reached_death_line():
                self.game_over = True

    # ── Draw ─────────────────────────────────
    def _draw_background(self, surface):
        surface.fill(BLACK)
        self.starfield.draw(surface)
        for y in range(90, HEIGHT, 44):
            pygame.draw.line(surface, (20,70,95),(0,y),(WIDTH,y),1)
        for x in range(-WIDTH, WIDTH*2, 70):
            pygame.draw.line(surface, (28,24,70),(WIDTH//2,92),(x,HEIGHT),1)
        draw_glow_line(surface,(0,DANGER_Y),    (WIDTH,DANGER_Y),    YELLOW, 1)
        draw_glow_line(surface,(0,DEATH_LINE_Y),(WIDTH,DEATH_LINE_Y), RED,    2)

    def _draw_lasers(self, surface):
        for laser in self.lasers:
            draw_glow_line(surface, laser["from"], laser["to"], RED, 2)

    def draw(self):
        world = pygame.Surface((WIDTH, HEIGHT))
        self._draw_background(world)
        self._draw_lasers(world)

        for word in self.words:
            word.draw(world, self.word_font)
        for proj in self.projectiles:
            proj.draw(world, self.projectile_font)

        self.ship.draw(world)
        self.bomb_effect.draw(world, self.ship.nose())
        self.particles.draw(world)
        self.ui.frame_gameplay(world)
        self.ui.draw(world, self)

        if self.level_up_pause:
            self.ui.draw_level_up(world, self.level, self.level_up_timer)
        if self.game_over:
            self.ui.draw_game_over(world, self)

        # Wrong flash — хамгийн сүүлд (дээрх бүх зүйлийн дэргэд)
        self.wrong_flash.draw(world)
        self.ui.draw_crt_overlay(world, critical=self.game_over or self.wrong_flash.life > 0 or self.level_up_pause)

        offset = self.bomb_effect.shake_offset()
        self.screen.fill(BLACK)
        self.screen.blit(world, offset)
        pygame.display.flip()

    # ── Loop ─────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

# ──────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    screen    = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cyberpunk ZType  v3")
    clock     = pygame.time.Clock()
    starfield = StarField()   # menu болон game хуваалцана

    while True:
        menu     = MainMenu(screen, clock, starfield)
        language = menu.run()
        game     = Game(language=language, starfield=starfield)
        game.run() 
