import pygame, sys, random, sqlite3
pygame.init()

# ==========================
# BAZA (HIGH SCORE)
# ==========================
conn = sqlite3.connect("highscore.db")      # Ustvari / odpre bazo
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS score (points INTEGER)")
conn.commit()

def save_highscore(score):
    c.execute("INSERT INTO score VALUES (?)", (score,))
    conn.commit()

def get_highscore():
    c.execute("SELECT MAX(points) FROM score")
    r = c.fetchone()[0]
    return r if r else 0

# ==========================
# OSNOVNE NASTAVITVE OKNA
# ==========================
W, H = 800, 400
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Ping Pong EXTREME")

# ==========================
# BARVE
# ==========================
WHITE = (255,255,255)
RED   = (220,50,50)
BLUE  = (50,120,220)
BG    = (15,15,30)

# ==========================
# PISAVE IN URA
# ==========================
font = pygame.font.SysFont(None, 32)
big  = pygame.font.SysFont(None, 70)
clock = pygame.time.Clock()

# ==========================
# FUNKCIJA ZA TEKST
# ==========================
def txt(t, f, x, y):
    s = f.render(t, True, WHITE)
    r = s.get_rect(center=(x, y))
    screen.blit(s, r)

# ==========================
# ZAČETNI ZASLON
# ==========================
def start():
    while True:
        screen.fill(BG)
        txt("PING PONG EXTREME", big, W//2, 140)
        txt(f"HIGH SCORE: {get_highscore()}", font, W//2, 200)
        txt("SPACE - začetek", font, W//2, 250)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                return

# ==========================
# KONEC IGRE
# ==========================
def konec(winner, score):
    save_highscore(score)          # Shrani rezultat
    while True:
        screen.fill(BG)
        txt(f"Zmagal je {winner}!", big, W//2, 150)
        txt(f"Rezultat: {score}", font, W//2, 210)
        txt(f"High score: {get_highscore()}", font, W//2, 250)
        txt("R - znova | ESC - izhod", font, W//2, 300)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

# ==========================
# START
# ==========================
start()

# ==========================
# SPREMENLJIVKE IGRE
# ==========================
lw, lh = 10, 80
lx, ly = 30, H//2 - lh//2
rx, ry = W-40, H//2 - lh//2
speed = 6

bw = 15
bx, by = W//2, H//2
spx, spy = random.choice([-4,4]), random.choice([-3,3])
ball_mult = 1.0
ball_color = [random.randint(50,255) for _ in range(3)]

SL, SR = 0, 0
TIME_LIMIT = 60
start_time = pygame.time.get_ticks()

# ==========================
# GLAVNA ZANKA
# ==========================
while True:
    clock.tick(60)

    elapsed = (pygame.time.get_ticks() - start_time) // 1000
    time_left = max(0, TIME_LIMIT - elapsed)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    # --- KONTROLE ---
    k = pygame.key.get_pressed()
    if k[pygame.K_w]: ly -= speed
    if k[pygame.K_s]: ly += speed
    if k[pygame.K_UP]: ry -= speed
    if k[pygame.K_DOWN]: ry += speed

    ly = max(0, min(H-lh, ly))
    ry = max(0, min(H-lh, ry))

    # --- ŽOGA ---
    bx += spx * ball_mult
    by += spy * ball_mult

    if by <= 0 or by >= H-bw:
        spy *= -1

    miss = 0.15

    if lx < bx < lx+lw and ly < by < ly+lh and random.random() > miss:
        spx *= -1
        ball_mult += 0.2

    if rx < bx+bw < rx+lw and ry < by < ry+lh and random.random() > miss:
        spx *= -1
        ball_mult += 0.2

    # --- TOČKE ---
    if bx < 0:
        SR += 1
        bx, by = W//2, H//2
        ball_mult = 1.0
        spx = abs(spx)
        ball_color = [random.randint(50,255) for _ in range(3)]

    if bx > W:
        SL += 1
        bx, by = W//2, H//2
        ball_mult = 1.0
        spx = -abs(spx)
        ball_color = [random.randint(50,255) for _ in range(3)]

    # --- KONEC ---
    if time_left == 0:
        score = max(SL, SR)
        if SL > SR: konec("Levi igralec", score)
        elif SR > SL: konec("Desni igralec", score)
        else: konec("Neodločeno", score)
        SL = SR = 0
        start_time = pygame.time.get_ticks()
        start()

    # --- RISANJE ---
    screen.fill(BG)
    pygame.draw.rect(screen, RED, (lx, ly, lw, lh))
    pygame.draw.rect(screen, BLUE, (rx, ry, lw, lh))
    pygame.draw.ellipse(screen, ball_color, (bx, by, bw, bw))
    pygame.draw.aaline(screen, WHITE, (W//2,0), (W//2,H))

    screen.blit(font.render(f"{SL}   {SR}", True, WHITE), (W//2-30, 10))
    screen.blit(font.render(f"Čas: {time_left}s", True, WHITE), (20, 10))

    pygame.display.flip()
