"""
Chrome T-Rex (offline) game - Pygame single-file replica with improved Dino sprite
- Controls: SPACE or UP to jump, DOWN to duck, R to restart after game over, ESC to quit
- Features: running/jump/duck, obstacles, birds, score, speed increase, day/night

Run: python chrome_trex_pygame.py
Requires: pygame (pip install pygame)
"""

import pygame
import random
import sys
import os

WIDTH, HEIGHT = 800, 200
FPS = 60
GROUND_Y = HEIGHT - 40
GRAVITY = 0.9
JUMP_VELOCITY = -14
GAME_TITLE = "Chrome T-Rex - Pygame Replica"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_DAY = (247, 247, 247)
BG_NIGHT = (20, 20, 20)

HS_FILE = "trex_highscore.txt"

class Dino:
    def __init__(self):
        self.x = 50
        self.width = 44
        self.height = 47
        self.y = GROUND_Y - self.height
        self.vy = 0
        self.on_ground = True
        self.ducking = False
        self.anim_time = 0

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
        if self.on_ground:
            self.ducking = val

    def update(self):
        self.vy += GRAVITY
        self.y += self.vy
        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vy = 0
            self.on_ground = True
        if self.on_ground and not self.ducking:
            self.anim_time += 1
        else:
            self.anim_time = 0

    def draw(self, surf):
        r = self.rect()
        head_rect = pygame.Rect(r.x + 20, r.y, 20, 20)
        pygame.draw.rect(surf, BLACK, head_rect)
        pygame.draw.circle(surf, WHITE, (head_rect.x + 15, head_rect.y + 6), 3)
        body_rect = pygame.Rect(r.x, r.y + 15, 30, 20)
        pygame.draw.rect(surf, BLACK, body_rect)
        pygame.draw.polygon(surf, BLACK, [(r.x, r.y + 25), (r.x - 10, r.y + 20), (r.x, r.y + 30)])
        frame = (self.anim_time // 6) % 2
        if frame == 0:
            pygame.draw.rect(surf, BLACK, (r.x + 5, r.y + r.h - 6, 6, 6))
            pygame.draw.rect(surf, BLACK, (r.x + 20, r.y + r.h - 4, 6, 6))
        else:
            pygame.draw.rect(surf, BLACK, (r.x + 5, r.y + r.h - 4, 6, 6))
            pygame.draw.rect(surf, BLACK, (r.x + 20, r.y + r.h - 6, 6, 6))

class Obstacle:
    def __init__(self, x, speed):
        self.x = x
        self.speed = speed
        if random.random() < 0.8:
            self.type = 'cactus'
            h = random.choice([30, 35, 40])
            w = random.choice([12, 18, 22])
            self.rects = []
            groups = random.choice([1, 1, 2])
            px = 0
            for i in range(groups):
                rw = w + random.randint(0, 6)
                rh = h + random.randint(-5, 5)
                r = pygame.Rect(0 + px, GROUND_Y - rh, rw, rh)
                self.rects.append(r)
                px += rw + 3
            self.w = px
            self.h = max(r.h for r in self.rects)
            self.y = GROUND_Y - self.h
        else:
            self.type = 'bird'
            self.w = 46
            self.h = 30
            self.y = GROUND_Y - self.h - random.choice([60, 45, 30])

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.w), int(self.h))

    def update(self):
        self.x -= self.speed

    def draw(self, surf):
        if self.type == 'cactus':
            base_x = int(self.x)
            for seg in self.rects:
                r = pygame.Rect(base_x + seg.x, seg.y, seg.w, seg.h)
                pygame.draw.rect(surf, BLACK, r)
        else:
            r = self.get_rect()
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
        pygame.draw.line(surf, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)
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
        pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), 10, 1)
        pygame.draw.circle(surf, BLACK, (int(self.x + 12), int(self.y - 6)), 12, 1)
        pygame.draw.circle(surf, BLACK, (int(self.x + 24), int(self.y)), 10, 1)

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

def main():
    pygame.init()
    global bg_color
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 18)
    big_font = pygame.font.SysFont('Arial', 24)

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
    bg_is_day = True
    bg_switch_score = 500

    while True:
        dt = clock.tick(FPS)

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
                        score = 0
                        speed = 6.0
                        obstacles.clear()
                        dino = Dino()
                        game_over = False
                        playing = True
                        bg_is_day = True
                if event.key == pygame.K_DOWN:
                    dino.duck(True)
                if event.key == pygame.K_r:
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

        if playing and not game_over:
            if score and score % 100 == 0:
                speed = 6.0 + (score // 100) * 0.5

            spawn_timer += 1
            if spawn_timer >= spawn_interval:
                spawn_timer = 0
                a = max(40, int(90 - speed * 6))
                spawn_interval = random.randint(a, a + 60)
                obstacles.append(Obstacle(WIDTH + 20, speed))

            if random.random() < 0.01:
                clouds.append(Cloud(WIDTH + 30, random.randint(20, 80), speed * 0.08))

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

            dino_rect = dino.rect()
            for ob in obstacles:
                if ob.type == 'cactus':
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

            score += 1
            if score > highscore:
                highscore = score

            if score >= bg_switch_score:
                bg_is_day = not bg_is_day
                bg_switch_score += 500

        bg_color = BG_DAY if bg_is_day else BG_NIGHT
        screen.fill(bg_color)

        for c in clouds:
            c.draw(screen)

        ground.draw(screen)

        for ob in obstacles:
            ob.draw(screen)

        dino.draw(screen)

        score_text = font.render(f"Score: {score}", True, BLACK if bg_is_day else WHITE)
        hs_text = font.render(f"Highscore: {highscore}", True, BLACK if bg_is_day else WHITE)
        screen.blit(score_text, (WIDTH - 140, 10))
        screen.blit(hs_text, (WIDTH - 300, 10))

        if game_over:
            over_text = big_font.render("GAME OVER", True, BLACK if bg_is_day else WHITE)
            restart_text = font.render("Press R or SPACE to restart", True, BLACK if bg_is_day else WHITE)
            screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 20))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))
            save_highscore(highscore)

        pygame.display.flip()

if __name__ == '__main__':
    main()
