"""Road Rush - a simple Python driving game with generated sound effects.

Install pygame once: python -m pip install pygame
Run:                 python road_rush.py
Controls: A/D or arrows steer; W/S or arrows accelerate/brake; R restarts; Esc quits.
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
    raise SystemExit("Install pygame first: python -m pip install pygame") from error

W, H, FPS = 900, 700, 60


def create_wav(filename, duration, generator, sample_rate=22050):
    """Build a short mono wave file entirely in Python."""
    samples = array("h")
    for i in range(int(duration * sample_rate)):
        samples.append(int(max(-1, min(1, generator(i / sample_rate))) * 32767))
    target = Path(tempfile.gettempdir()) / filename
    with wave.open(str(target), "wb") as output:
        output.setparams((1, 2, sample_rate, len(samples), "NONE", "not compressed"))
        output.writeframes(samples.tobytes())
    return str(target)


def load_audio():
    # Low engine pulse, wind/road noise and a brief crash thump—no external assets.
    engine = create_wav("road_rush_engine.wav", 1.2, lambda t: (math.sin(math.tau * 58 * t) * .20 + math.sin(math.tau * 116 * t) * .11 + math.sin(math.tau * 174 * t) * .05))
    wind = create_wav("road_rush_wind.wav", .8, lambda t: (math.sin(math.tau * 2437 * t) + math.sin(math.tau * 1391 * t)) * .035)
    crash = create_wav("road_rush_crash.wav", .32, lambda t: math.sin(math.tau * (90 - t * 180) * t) * max(0, 1 - t / .32) * .75)
    return pygame.mixer.Sound(engine), pygame.mixer.Sound(wind), pygame.mixer.Sound(crash)


def car_surface(color):
    surface = pygame.Surface((58, 105), pygame.SRCALPHA)
    # pygame.draw.rect uses border_radius; pygame.draw.rounded_rect does not exist.
    pygame.draw.rect(surface, (15, 17, 19), (3, 6, 52, 94), border_radius=15)
    pygame.draw.rect(surface, color, (8, 3, 42, 98), border_radius=13)
    pygame.draw.polygon(surface, (151, 203, 217), [(15, 27), (43, 27), (48, 55), (10, 55)])
    pygame.draw.rect(surface, (27, 37, 43), (13, 57, 32, 21))
    pygame.draw.rect(surface, (245, 226, 154), (12, 8, 12, 5)); pygame.draw.rect(surface, (245, 226, 154), (34, 8, 12, 5))
    pygame.draw.rect(surface, (222, 44, 35), (11, 89, 13, 5)); pygame.draw.rect(surface, (222, 44, 35), (34, 89, 13, 5))
    return surface


def main():
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Road Rush")
    clock = pygame.time.Clock()
    title = pygame.font.SysFont("impact", 44)
    font = pygame.font.SysFont("consolas", 20, bold=True)
    engine, wind, crash = load_audio()
    engine.play(-1); wind.play(-1)

    player = car_surface((201, 49, 41))
    player_x, player_y = W / 2, H - 150
    speed, distance, road_offset, health = 0.0, 0.0, 0.0, 100
    traffic, game_over = [], False
    spawn = .8

    while True:
        dt = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); return
                if event.key == pygame.K_r and game_over:
                    player_x, speed, distance, health, traffic, game_over = W / 2, 0, 0, 100, [], False

        keys = pygame.key.get_pressed()
        if not game_over:
            accelerating = keys[pygame.K_w] or keys[pygame.K_UP]
            braking = keys[pygame.K_s] or keys[pygame.K_DOWN]
            steer = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
            speed += (110 if accelerating else -37) * dt
            if braking: speed -= 180 * dt
            speed = max(0, min(260, speed))
            player_x += steer * (150 + speed * .82) * dt
            player_x = max(W * .26, min(W * .74, player_x))
            distance += speed * dt
            road_offset = (road_offset + speed * dt) % 80
            spawn -= dt
            if spawn <= 0 and speed > 20:
                traffic.append([random.choice((W * .36, W * .5, W * .64)), -130, random.choice((75, 95, 110)), car_surface(random.choice(((36, 112, 190), (230, 179, 46), (65, 155, 96), (111, 74, 151))))])
                spawn = random.uniform(.75, 1.5) - speed / 850
            for vehicle in traffic:
                vehicle[1] += (speed + vehicle[2]) * dt
            traffic = [vehicle for vehicle in traffic if vehicle[1] < H + 140]
            player_box = player.get_rect(center=(player_x, player_y))
            for vehicle in traffic[:]:
                if player_box.colliderect(vehicle[3].get_rect(center=(vehicle[0], vehicle[1]))):
                    traffic.remove(vehicle); health -= 34; speed *= .35; crash.play()
                    if health <= 0: game_over = True

        engine.set_volume(.13 + speed / 520); wind.set_volume(speed / 1000)
        # Landscape
        screen.fill((97, 169, 202))
        pygame.draw.rect(screen, (74, 129, 72), (0, 155, W, H - 155))
        for x in range(-40, W + 70, 105):
            pygame.draw.circle(screen, (45, 96, 55), (x + 25, 167), 42)
            pygame.draw.rect(screen, (77, 58, 34), (x + 20, 170, 10, 58))
        # Perspective road
        pygame.draw.polygon(screen, (42, 45, 48), [(W*.33, 155), (W*.67, 155), (W*.87, H), (W*.13, H)])
        pygame.draw.polygon(screen, (229, 204, 115), [(W*.325,155), (W*.33,155), (W*.14,H), (W*.13,H)])
        pygame.draw.polygon(screen, (229, 204, 115), [(W*.67,155), (W*.675,155), (W*.87,H), (W*.86,H)])
        for lane in (W*.445, W*.555):
            for y in range(-40, H, 80):
                yy = y + road_offset
                scale = max(.15, (yy - 120) / H)
                pygame.draw.rect(screen, (239, 231, 191), (lane - 4 * scale, yy, 8 * scale, 38 * scale))
        for vehicle in traffic:
            screen.blit(vehicle[3], vehicle[3].get_rect(center=(vehicle[0], vehicle[1])))
        screen.blit(player, player.get_rect(center=(player_x, player_y)))
        pygame.draw.rect(screen, (12, 18, 24), (0, 0, W, 64))
        screen.blit(title.render("ROAD RUSH", True, (255, 192, 55)), (25, 8))
        screen.blit(font.render(f"SPEED {int(speed * .9):03d} km/h     DISTANCE {int(distance):05d} m", True, (237, 243, 238)), (W - 510, 22))
        pygame.draw.rect(screen, (38, 49, 48), (24, H - 35, 220, 14))
        pygame.draw.rect(screen, (76, 181, 86) if health > 35 else (218, 64, 45), (27, H - 32, health * 2.14, 8))
        screen.blit(font.render(f"CAR {health}%", True, (250, 250, 237)), (24, H - 61))
        if game_over:
            shade = pygame.Surface((W, H), pygame.SRCALPHA); shade.fill((0, 0, 0, 155)); screen.blit(shade, (0, 0))
            message = title.render("CAR WRECKED", True, (250, 188, 55)); screen.blit(message, message.get_rect(center=(W/2, H/2 - 22)))
            hint = font.render("Press R to drive again   •   Esc to quit", True, (244, 244, 232)); screen.blit(hint, hint.get_rect(center=(W/2, H/2 + 30)))
        pygame.display.flip()


if __name__ == "__main__":
    main()
