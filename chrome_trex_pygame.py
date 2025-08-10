"""
Chrome T-Rex (offline) game - Pygame single-file replica
- No external assets required (everything drawn procedurally)
- Controls: SPACE or UP to jump, DOWN to duck, R to restart after game over, ESC to quit
- Features: running/jump/duck, obstacles (cacti), birds, score, speed increase, day/night

Run: python chrome_trex_pygame.py
Requires: pygame (pip install pygame)

This is an educational, single-file implementation intended to closely mimic the look &
feel of the Chrome T-Rex runner while keeping code clear and easy to modify.
"""

import pygame
import random
import sys
import os

# --------- Configuration ----------
WIDTH, HEIGHT = 800, 200
FPS = 60
GROUND_Y = HEIGHT - 40
GRAVITY = 0.9
JUMP_VELOCITY = -14
GAME_TITLE = "Chrome T-Rex - Pygame Replica"

# Colors (monochrome-ish like original)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_DAY = (247, 247, 247)
BG_NIGHT = (20, 20, 20)

# Paths
HS_FILE = "trex_highscore.txt"

# --------- Game Objects ----------
class Dino:
    def __init__(self):
        self.x = 50
        self.width = 44
        self.height = 47
        self.y = GROUND_Y - self.height
        self.vy = 0
        self.on_ground = True
        self.ducking = False
        # animation frames (we'll toggle leg positions)
        self.anim_time = 0
        self.alive = True

    def rect(self):
        h = self.height if not self.ducking else self.height * 0.6
        y = self.y + (self.height - h)
        return pygame.Rect(self.x, int(y), int(self.width), int(h))

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_VELOCITY
            self.on_ground = False
            self.ducking = False

    def duck(self, val: bool):
        # only allow duck when on ground
        if self.on_ground:
            self.ducking = val

    def update(self):
        # physics
        self.vy += GRAVITY
        self.y += self.vy
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vy = 0
            self.on_ground = True
        # animation time
        if self.on_ground and not self.ducking:
            self.anim_time += 1
        else:
            self.anim_time = 0

    def draw(self, surf):
        r = self.rect()
        # body
        pygame.draw.rect(surf, BLACK, r)
        # eye
        eye = (r.x + r.w - 12, r.y + 10)
        pygame.draw.circle(surf, WHITE if bg_color == BLACK else WHITE, eye, 3)
        # legs animation (simple)
        if self.on_ground and not self.ducking:
            frame = (self.anim_time // 6) % 2
            leg1 = pygame.Rect(r.x + 8, r.y + r.h - 6, 6, 6)
            leg2 = pygame.Rect(r.x + 26, r.y + r.h - 6, 6, 6)
            if frame == 0:
                leg1.y += 2
            else:
                leg2.y += 2
            pygame.draw.rect(surf, BLACK, leg1)
            pygame.draw.rect(surf, BLACK, leg2)
        else:
            # standing legs
            leg1 = pygame.Rect(r.x + 10, r.y + r.h - 6, 6, 6)
            leg2 = pygame.Rect(r.x + 26, r.y + r.h - 6, 6, 6)
            pygame.draw.rect(surf, BLACK, leg1)
            pygame.draw.rect(surf, BLACK, leg2)


class Obstacle:
    def __init__(self, x, speed):
        self.x = x
        self.speed = speed
        # choose cactus or bird
        if random.random() < 0.8:
            # cactus groups with random heights
            self.type = 'cactus'
            h = random.choice([30, 35, 40])
            w = random.choice([12, 18, 22])
            self.rects = []
            # some cactuses have multiple segments
            groups = random.choice([1, 1, 2])
            px = 0
            for i in range(groups):
                rw = w + random.randint(0, 6)
                rh = h + random.randint(-5, 5)
                r = pygame.Rect(0 + px, GROUND_Y - rh, rw, rh)
                self.rects.append(r)
                px += rw + 3
            # total width used for collision rect
            self.w = px
            self.h = max(r.h for r in self.rects)
            self.y = GROUND_Y - self.h
        else:
            self.type = 'bird'
            self.w = 46
            self.h = 30
            # birds at different heights
            self.y = GROUND_Y - self.h - random.choice([60, 45, 30])

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.w), int(self.h))

    def update(self):
        self.x -= self.speed

    def draw(self, surf):
        if self.type == 'cactus':
            # draw each segment
            base_x = int(self.x)
            for seg in self.rects:
                r = pygame.Rect(base_x + seg.x, seg.y, seg.w, seg.h)
                pygame.draw.rect(surf, BLACK, r)
                # little arms
                if seg.h > 28 and random.random() > 0.5:
                    arm = pygame.Rect(r.x - 6, r.y + r.h//3, 6, 3)
                    pygame.draw.rect(surf, BLACK, arm)
        else:
            r = self.get_rect()
            # simple bird: body + wing
            body = pygame.Rect(r.x, r.y + 8, r.w - 20, r.h - 10)
            wing = [(r.x + 6, r.y + 8), (r.x + 22, r.y), (r.x + 30, r.y + 8)]
            pygame.draw.rect(surf, BLACK, body)
            pygame.draw.polygon(surf, BLACK, wing)


class Ground:
    def __init__(self, speed):
        self.speed = speed
        self.x = 0
        self.image_w = WIDTH

    def update(self):
        self.x -= self.speed
        if self.x <= -self.image_w:
            self.x = 0

    def draw(self, surf):
        # draw simple dashed line ground to mimic pixel art
        pygame.draw.line(surf, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
        # small rocks/dashes
        for i in range(-20, WIDTH + 20, 40):
            x = (i + int(self.x)) % (WIDTH + 40) - 20
            pygame.draw.rect(surf, BLACK, (x, GROUND_Y - 6, 6, 6))


class Cloud:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def update(self):
        self.x -= self.speed

    def draw(self, surf):
        # simple cloud using circles
        pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), 10, 1)
        pygame.draw.circle(surf, BLACK, (int(self.x + 12), int(self.y - 6)), 12, 1)
        pygame.draw.circle(surf, BLACK, (int(self.x + 24), int(self.y)), 10, 1)


# ---------- Helpers ----------

def load_highscore():
    try:
        with open(HS_FILE, 'r') as f:
            return int(f.read().strip())
    except Exception:
        return 0


def save_highscore(hs):
    try:
        with open(HS_FILE, 'w') as f:
            f.write(str(int(hs)))
    except Exception:
        pass


# ---------- Main Game ----------

def main():
    pygame.init()
    global bg_color
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 18)
    big_font = pygame.font.SysFont('Arial', 24)

    # game state
    speed = 6.0
    spawn_timer = 0
    spawn_interval = 90
    obstacles = []
    clouds = [Cloud(WIDTH - 20, 40, 0.5), Cloud(WIDTH - 200, 30, 0.3)]
    ground = Ground(speed)
    dino = Dino()
    score = 0
    highscore = load_highscore()
    playing = True
    game_over = False
    # day/night toggle variables
    bg_is_day = True
    bg_switch_score = 500

    # sound (optional) - only add if available
    # jump_sound = None

    # main loop
    tick = 0
    while True:
        dt = clock.tick(FPS)
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_highscore(highscore)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if playing and not game_over:
                        dino.jump()
                    elif game_over:
                        # restart
                        score = 0
                        speed = 6.0
                        obstacles.clear()
                        dino = Dino()
                        game_over = False
                        playing = True
                        bg_is_day = True
                    else:
                        pass
                if event.key == pygame.K_DOWN:
                    dino.duck(True)
                if event.key == pygame.K_r:
                    # restart
                    score = 0
                    speed = 6.0
                    obstacles.clear()
                    dino = Dino()
                    game_over = False
                    playing = True
                    bg_is_day = True
                if event.key == pygame.K_ESCAPE:
                    save_highscore(highscore)
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    dino.duck(False)

        # update only when playing
        if playing and not game_over:
            # difficulty scaling
            if score and score % 100 == 0:
                # tiny bump at exact multiples only once per frame multiple
                speed = 6.0 + (score // 100) * 0.5

            # spawn obstacles
            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                # randomize next interval with speed
a = max(40, int(90 - speed * 6))
                spawn_interval = random.randint(a, a + 60)
                obstacles.append(Obstacle(WIDTH + 20, speed))

            # spawn clouds occasionally
            if random.random() < 0.01:
                clouds.append(Cloud(WIDTH + 30, random.randint(20, 80), speed * 0.08))

            # update objects
            for ob in obstacles:
                ob.speed = speed
                ob.update()
            obstacles = [o for o in obstacles if o.x + o.w > -50]

            for c in clouds:
                c.update()
            clouds = [c for c in clouds if c.x > -60]

            ground.speed = speed
            ground.update()
            dino.update()

            # collisions
            dino_rect = dino.rect()
            for ob in obstacles:
                if ob.type == 'cactus':
                    # check segments
                    base_x = int(ob.x)
                    for seg in ob.rects:
                        seg_rect = pygame.Rect(base_x + seg.x, seg.y, seg.w, seg.h)
                        if dino_rect.colliderect(seg_rect):
                            game_over = True
                            playing = False
                else:
                    if dino_rect.colliderect(ob.get_rect()):
                        game_over = True
                        playing = False

            # update score
            score += 1
            if score > highscore:
                highscore = score

            # day/night toggle
            if score >= bg_switch_score:
                bg_is_day = not bg_is_day
                bg_switch_score += 500

        # drawing
        bg_color = BG_DAY if bg_is_day else BG_NIGHT
        screen.fill(bg_color)

        # clouds (drawn in lighter color if day, reversed for night)
        for c in clouds:
            c.draw(screen)

        ground.draw(screen)

        for ob in obstacles:
            ob.draw(screen)

        dino.draw(screen)

        # HUD - score and highscore
        score_text = font.render(f"Score: {score}", True, BLACK if bg_is_day else WHITE)
        hs_text = font.render(f"Highscore: {highscore}", True, BLACK if bg_is_day else WHITE)
        screen.blit(score_text, (WIDTH - 140, 10))
        screen.blit(hs_text, (WIDTH - 300, 10))

        # if game over show overlay
        if game_over:
            over_text = big_font.render("GAME OVER", True, BLACK if bg_is_day else WHITE)
            restart_text = font.render("Press R or SPACE to restart", True, BLACK if bg_is_day else WHITE)
            screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 20))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))

        pygame.display.flip()

        # small delay after game over so collision isn't instant restart
        if game_over:
            save_highscore(highscore)


if __name__ == '__main__':
    main()
