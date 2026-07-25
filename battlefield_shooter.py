"""Iron Horizon - a small desktop battlefield shooter.

Install once:  python -m pip install pygame
Run:           python battlefield_shooter.py

Controls: mouse to aim, left-click or Space to fire, P to pause, Esc to quit.
"""
import math
import random
import tempfile
import wave
from array import array
from pathlib import Path

try:
    import pygame
except ImportError as error:
    raise SystemExit("This game needs pygame. Install it with: python -m pip install pygame") from error


WIDTH, HEIGHT = 1100, 680
FPS = 60


def sound_file(name: str, seconds: float, notes: list[tuple[float, float]], volume: float = 0.25) -> str:
    """Create a small WAV sound from sine waves, stored in the temporary folder."""
    sample_rate = 22050
    frames = int(sample_rate * seconds)
    data = array("h")
    for frame in range(frames):
        time = frame / sample_rate
        value = 0.0
        for frequency, start in notes:
            local = time - start
            if 0 <= local < 0.42:
                envelope = min(local * 9, 1) * max(0, 1 - local / 0.42)
                value += math.sin(math.tau * frequency * local) * envelope
        data.append(int(max(-1, min(1, value * volume)) * 32767))
    path = Path(tempfile.gettempdir()) / name
    with wave.open(str(path), "wb") as wav:
        wav.setparams((1, 2, sample_rate, frames, "NONE", "not compressed"))
        wav.writeframes(data.tobytes())
    return str(path)


def make_sounds():
    # A low, repeating, original battlefield ambience; no external audio files required.
    melody = [(55, 0), (73.4, 0.5), (65.4, 1.0), (82.4, 1.5), (55, 2.0), (98, 2.5)]
    music = pygame.mixer.Sound(sound_file("iron_horizon_ambience.wav", 3.0, melody, 0.18))
    shot = pygame.mixer.Sound(sound_file("iron_horizon_shot.wav", 0.13, [(130, 0), (72, 0.01)], 0.7))
    shot.set_volume(0.45)
    return music, shot


class Enemy:
    def __init__(self, wave):
        self.radius = random.randint(22, 34)
        self.x = random.choice((random.randint(45, 280), random.randint(WIDTH - 280, WIDTH - 45)))
        self.y = random.randint(170, HEIGHT - 155)
        self.health = 2 + wave // 3
        self.cooldown = random.uniform(0.7, 2.0)
        self.wobble = random.random() * math.tau

    def update(self, dt, wave):
        self.wobble += dt * 2
        self.x += math.sin(self.wobble) * 13 * dt
        self.cooldown -= dt
        if self.cooldown <= 0:
            self.cooldown = max(0.55, random.uniform(1.0, 2.2) - wave * 0.06)
            return True
        return False

    def draw(self, screen):
        bob = int(math.sin(self.wobble * 1.4) * 3)
        x, y, r = int(self.x), int(self.y + bob), self.radius
        pygame.draw.ellipse(screen, (25, 31, 27), (x - r // 2, y - 1, r, r + 18))
        pygame.draw.circle(screen, (91, 108, 76), (x, y - r // 2), r // 2)
        pygame.draw.rect(screen, (29, 39, 31), (x - r // 2, y, r, r))
        pygame.draw.line(screen, (18, 24, 19), (x + r // 3, y + 8), (x + r, y), 5)
        pygame.draw.rect(screen, (245, 195, 74), (x - 5, y - r // 2 - 2, 10, 3))


def draw_background(screen):
    screen.fill((88, 110, 112))
    pygame.draw.rect(screen, (111, 130, 119), (0, 245, WIDTH, 100))
    # Distant mountains and haze
    mountain = [(0, 270), (110, 185), (235, 258), (355, 160), (490, 255), (645, 190), (800, 268), (930, 155), (1100, 240), (1100, 345), (0, 345)]
    pygame.draw.polygon(screen, (78, 95, 83), mountain)
    pygame.draw.rect(screen, (91, 104, 80), (0, 330, WIDTH, 88))
    pygame.draw.rect(screen, (89, 70, 46), (0, 410, WIDTH, HEIGHT - 410))
    pygame.draw.rect(screen, (204, 170, 104), (0, 405, WIDTH, 4))
    for index in range(27):
        x = (index * 97) % WIDTH
        y = 440 + (index * 41) % 210
        pygame.draw.rect(screen, (58, 48, 34), (x, y, 58, 7))
        pygame.draw.rect(screen, (130, 96, 55), (x + 8, y - 8, 34, 8))


def draw_crosshair(screen, position):
    x, y = position
    color = (245, 244, 210)
    pygame.draw.circle(screen, color, (x, y), 16, 1)
    pygame.draw.line(screen, color, (x - 25, y), (x + 25, y), 1)
    pygame.draw.line(screen, color, (x, y - 25), (x, y + 25), 1)


def main():
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Iron Horizon: Battlefield")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("impact", 42)
    hud_font = pygame.font.SysFont("consolas", 21, bold=True)
    small_font = pygame.font.SysFont("arial", 17)
    music, shot_sound = make_sounds()
    music.play(loops=-1)

    enemies, sparks = [], []
    running, paused = True, False
    health, score, wave, spawn = 100, 0, 1, 0.4
    muzzle = 0

    while running:
        dt = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_SPACE and not paused:
                    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pygame.mouse.get_pos())
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not paused:
                mouse = pygame.mouse.get_pos()
                shot_sound.play()
                muzzle = 0.07
                closest = min(enemies, key=lambda enemy: math.dist((enemy.x, enemy.y), mouse), default=None)
                if closest and math.dist((closest.x, closest.y), mouse) < closest.radius + 26:
                    closest.health -= 1
                    sparks += [[closest.x, closest.y, random.uniform(-120, 120), random.uniform(-100, 45), 0.45] for _ in range(14)]
                    if closest.health <= 0:
                        enemies.remove(closest)
                        score += 100

        if not paused:
            spawn -= dt
            if spawn <= 0:
                enemies.append(Enemy(wave))
                spawn = max(0.42, 1.35 - wave * 0.08)
            for enemy in enemies:
                if enemy.update(dt, wave):
                    health = max(0, health - 8)
            if score >= wave * 800:
                wave += 1
                enemies.clear()
                spawn = 0.7
            muzzle = max(0, muzzle - dt)
            for spark in sparks:
                spark[0] += spark[2] * dt; spark[1] += spark[3] * dt; spark[3] += 200 * dt; spark[4] -= dt
            sparks = [spark for spark in sparks if spark[4] > 0]

        draw_background(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for x, y, _, _, life in sparks:
            pygame.draw.circle(screen, (242, 178, 51), (int(x), int(y)), max(1, int(life * 8)))
        # Gun silhouette at the lower centre
        pygame.draw.polygon(screen, (22, 27, 25), [(WIDTH // 2 - 90, HEIGHT), (WIDTH // 2 - 45, HEIGHT - 90), (WIDTH // 2 + 48, HEIGHT - 90), (WIDTH // 2 + 108, HEIGHT)])
        pygame.draw.rect(screen, (29, 36, 32), (WIDTH // 2 - 18, HEIGHT - 142, 36, 82))
        if muzzle:
            pygame.draw.circle(screen, (255, 211, 97), (WIDTH // 2, HEIGHT - 145), 20)

        pygame.draw.rect(screen, (15, 24, 25), (0, 0, WIDTH, 62))
        screen.blit(title_font.render("IRON HORIZON", True, (237, 176, 57)), (25, 8))
        screen.blit(hud_font.render(f"WAVE {wave}     SCORE {score:04d}", True, (233, 239, 220)), (WIDTH - 295, 21))
        pygame.draw.rect(screen, (35, 48, 42), (24, HEIGHT - 38, 205, 14))
        pygame.draw.rect(screen, (104, 165, 66) if health > 35 else (200, 66, 49), (27, HEIGHT - 35, int(199 * health / 100), 8))
        screen.blit(small_font.render(f"ARMOR {health}", True, (236, 240, 225)), (24, HEIGHT - 62))
        if paused or health == 0:
            message = "PAUSED" if paused else "YOU WERE OVERRUN — press Esc to exit"
            panel = pygame.Surface((650, 94), pygame.SRCALPHA); panel.fill((8, 14, 14, 205)); screen.blit(panel, (225, 285))
            text = title_font.render(message, True, (244, 196, 86)); screen.blit(text, text.get_rect(center=(WIDTH // 2, 330)))
            if health == 0:
                paused = True
        draw_crosshair(screen, pygame.mouse.get_pos())
        pygame.display.flip()
    music.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
