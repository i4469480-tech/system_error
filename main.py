import pygame
import random
import time
import sys

# --- ИНИЦИАЛИЗАЦИЯ ---
pygame.init()
info = pygame.display.Info()
# Берем размеры экрана устройства
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

# Цвета (RGB)
BG = (5, 5, 15)
GLITCH_GREEN = (0, 255, 150)
VIRUS_RED = (255, 0, 50)
ERROR_RED = (255, 40, 40)
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)
WARNING_YELLOW = (255, 255, 0)

# Состояния игры
STATE_MENU, STATE_GAME, STATE_DEAD, STATE_PROMO, STATE_SKINS, STATE_HELP = 0, 1, 2, 3, 4, 5
current_state = STATE_MENU

# Настройка шрифтов
font_title = pygame.font.SysFont("monospace", 60, bold=True)
font_ui = pygame.font.SysFont("monospace", 45, bold=True)
font_small = pygame.font.SysFont("monospace", 22)

# --- ИГРОВЫЕ ПЕРЕМЕННЫЕ ---
player_size = WIDTH // 10
player_pos = [WIDTH // 2, HEIGHT // 2]
particles, hunters = [], []
data_points = [[random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100)] for _ in range(3)]
score, highscore, shake_amount = 0, 0, 0
is_invisible, invis_timer = False, 0
clock = pygame.time.Clock()

# Система скинов и промокодов
promo_input = ""
current_skin_color = GLITCH_GREEN
unlocked_red_virus = False

# Загрузка рекорда из файла
try:
    with open("score.txt", "r") as f:
        highscore = int(f.read())
except:
    highscore = 0

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.size = random.randint(3, 8)
        self.life = 1.0
        self.vel_x, self.vel_y = random.uniform(-4, 4), random.uniform(-4, 4)
    def update(self):
        self.x += self.vel_x; self.y += self.vel_y; self.life -= 0.04
    def draw(self, surface):
        if self.life > 0:
            s = int(self.size * self.life)
            pygame.draw.rect(surface, self.color, (self.x, self.y, s, s))

def save_highscore(new_score):
    global highscore
    if new_score > highscore:
        highscore = new_score
        try:
            with open("score.txt", "w") as f:
                f.write(str(highscore))
        except: pass

def reset_game():
    global score, hunters, particles, player_pos, current_state
    score, hunters, particles = 0, [], []
    player_pos = [WIDTH // 2, HEIGHT // 2]
    current_state = STATE_GAME

# --- ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ ---
while True:
    mx, my = pygame.mouse.get_pos()
    # Эффект тряски экрана
    off_x, off_y = (random.randint(-shake_amount, shake_amount), random.randint(-shake_amount, shake_amount)) if shake_amount > 0 else (0,0)
    if shake_amount > 0: shake_amount -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            tx, ty = event.pos
            
            if current_state == STATE_MENU:
                if WIDTH - 110 < tx < WIDTH - 30 and 30 < ty < 110: current_state = STATE_HELP
                elif WIDTH//2 - 150 < tx < WIDTH//2 + 150:
                    if 280 < ty < 370: reset_game()
                    elif 400 < ty < 490: current_state = STATE_SKINS
                    elif 520 < ty < 610: current_state = STATE_PROMO
            
            elif current_state == STATE_HELP: current_state = STATE_MENU
            
            elif current_state == STATE_SKINS:
                if ty < 200: current_state = STATE_MENU
                elif 250 < ty < 350: current_skin_color = GLITCH_GREEN; current_state = STATE_MENU
                elif 400 < ty < 500 and unlocked_red_virus: current_skin_color = VIRUS_RED; current_state = STATE_MENU
            
            elif current_state == STATE_PROMO:
                # Простая клавиатура для ввода промокода
                for i, l in enumerate(["Ч", "Е", "Л", "CLR", "OK"]):
                    bx, by = 50 + (i%3)*150, 350 + (i//3)*120
                    if bx < tx < bx+130 and by < ty < by+100:
                        if l == "CLR": promo_input = ""
                        elif l == "OK":
                            if promo_input == "ЧЕЛ": unlocked_red_virus = True; current_skin_color = VIRUS_RED
                            promo_input = ""; current_state = STATE_MENU
                        else: promo_input += l
                if ty < 100: current_state = STATE_MENU
            
            elif current_state == STATE_GAME and not is_invisible:
                # Активация невидимости при тапе
                is_invisible = True; invis_timer = time.time() + 1.2; shake_amount = 10
            
            elif current_state == STATE_DEAD: current_state = STATE_MENU

    screen.fill(BG)

    if current_state == STATE_MENU:
        title = font_title.render("SYSTEM.ERROR", 1, current_skin_color)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        hs_txt = font_small.render(f"BEST RECORD: {highscore}%", 1, CYAN)
        screen.blit(hs_txt, (WIDTH//2 - hs_txt.get_width()//2, 180))
        for txt, y in [("START", 280), ("SKINS", 400), ("PROMO", 520)]:
            pygame.draw.rect(screen, WHITE, (WIDTH//2-150, y, 300, 90), 2)
            s = font_ui.render(txt, 1, WHITE)
            screen.blit(s, (WIDTH//2-s.get_width()//2, y+20))
        # Кнопка справки
        pygame.draw.circle(screen, WARNING_YELLOW, (WIDTH-70, 70), 40, 2)
        screen.blit(font_ui.render("?", 1, WARNING_YELLOW), (WIDTH-85, 45))

    elif current_state == STATE_GAME:
        lvl = (score // 100) + 1
        # Плавное движение игрока за пальцем/мышкой
        player_pos[0] += (mx - player_size//2 - player_pos[0]) * 0.2
        player_pos[1] += (my - player_size//2 - player_pos[1]) * 0.2
        
        if is_invisible and time.time() > invis_timer: is_invisible = False

        # Спавн охотников (красные линии)
        if len(hunters) < lvl + 1:
            hunters.append({'x': -100, 'speed': random.randint(12+lvl*2, 22+lvl*2), 'state': 'warning', 'timer': 40, 'y_m': random.randint(100, HEIGHT-100)})
        
        for h in hunters[:]:
            if h['state'] == 'warning':
                if h['timer'] % 10 < 5: screen.blit(font_ui.render("!", 1, WARNING_YELLOW), (30+off_x, h['y_m']+off_y))
                h['timer'] -= 1
                if h['timer'] <= 0: h['state'] = 'attack'
            else:
                h['x'] += h['speed']
                l_col = WHITE if is_invisible else ERROR_RED
                pygame.draw.line(screen, l_col, (h['x']+off_x, 0), (h['x']+off_x, HEIGHT), 7+lvl)
                # Проверка столкновения
                if not is_invisible and abs(player_pos[0]+player_size//2 - h['x']) < 25:
                    save_highscore(score); current_state = STATE_DEAD; shake_amount = 30
                if h['x'] > WIDTH: hunters.remove(h)

        # Сбор данных (точки)
        for d in data_points:
            pygame.draw.rect(screen, CYAN, (d[0]+off_x, d[1]+off_y, 25, 25), 2)
            if abs(player_pos[0]-d[0]) < player_size and abs(player_pos[1]-d[1]) < player_size:
                score += 10; shake_amount = 10; d[0], d[1] = random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100)

        # Частицы за игроком
        if random.random() > 0.4: particles.append(Particle(player_pos[0]+player_size//2, player_pos[1]+player_size//2, current_skin_color))
        for p in particles[:]:
            p.update(); p.draw(screen)
            if p.life <= 0: particles.remove(p)

        p_col = WHITE if is_invisible else current_skin_color
        pygame.draw.rect(screen, p_col, (player_pos[0]+off_x, player_pos[1]+off_y, player_size, player_size))
        screen.blit(font_ui.render(f"DATA: {score}%", 1, p_col), (40, 40))

    elif current_state == STATE_DEAD:
        screen.fill((0, 0, 150)) # Синий экран смерти
        screen.blit(font_title.render(":( KERNEL PANIC", 1, WHITE), (50, 200))
        screen.blit(font_ui.render(f"SCORE: {score}%", 1, WHITE), (50, 320))
        screen.blit(font_small.render("TAP TO MENU", 1, WHITE), (50, 400))

    elif current_state == STATE_SKINS:
        screen.fill(BG)
        screen.blit(font_ui.render("SKINS", 1, WHITE), (50, 80))
        pygame.draw.rect(screen, GLITCH_GREEN, (100, 250, 100, 100))
        screen.blit(font_small.render("DEFAULT", 1, GLITCH_GREEN), (220, 285))
        c = VIRUS_RED if unlocked_red_virus else (40, 40, 40)
        pygame.draw.rect(screen, c, (100, 400, 100, 100))
        label = "VIRUS RED" if unlocked_red_virus else "LOCKED"
        screen.blit(font_small.render(label, 1, c), (220, 435))
        screen.blit(font_small.render("TAP TOP TO BACK", 1, CYAN), (50, HEIGHT-80))

    elif current_state == STATE_PROMO:
        screen.fill(BG)
        screen.blit(font_ui.render(f"CODE: {promo_input}", 1, CYAN), (50, 200))
        for i, l in enumerate(["Ч", "Е", "Л", "CLR", "OK"]):
            bx, by = 50 + (i%3)*150, 350 + (i//3)*120
            pygame.draw.rect(screen, WHITE, (bx, by, 130, 100), 2)
            screen.blit(font_ui.render(l, 1, WHITE), (bx + 20, by + 25))

    elif current_state == STATE_HELP:
        overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(200); overlay.fill((0,0,0))
        screen.blit(overlay, (0,0))
        lines = ["ИНСТРУКЦИЯ:", "1. Тяни пальцем Квадрат", "2. Собирай синие точки", "3. Видишь '!' - ТАПАЙ,", "чтобы исчезнуть!", "", "ТАПНИ ДЛЯ ВЫХОДА"]
        for i, l in enumerate(lines):
            screen.blit(font_small.render(l, 1, WHITE), (50, 150 + i*45))

    pygame.display.flip()
    clock.tick(60)
