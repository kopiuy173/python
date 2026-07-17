"""
Mokou - 10 Stages Bullet Hell Survival
- Stage 1: Windmill (rotation_speed = 0.015)
- Stage 2: Speed-diff Windmill (rotation_speed = 0.015)
- Stage 3: Bloom Talisman (Purple 2.0 / Yellow 1.5)
- Stage 4: Bloom Talisman (Purple 3.0 / Yellow 1.5)
- Stage 5: Bloom Ring (Purple 3.0 / Yellow 1.5)
- Stage 6: Bloom Ring (Purple 4.0 / Yellow 1.5)
- Stage 7: Full Purple Bloom (Purple 5.0, 2x freq)
- Stage 8: Bloom Ring (Purple 5.0 / Yellow 1.5, r100/80)  ← NEW
- Stage 9: Triple Bloom (Purple 6.0 / Yellow 3.0 / Red 1.5) ← NEW
- Stage 10: Quad Bloom (Purple 7.0 / Yellow 5.0 / Red 3.0 / Green 1.5) ← FINAL
- Survive 30s per stage
- Player Speed: High 4.0 / Low 2.0, Q to toggle god mode
- Music: music.wav (loop)
"""

import pygame
import math
import sys
import random

# ==============================
# Import bullet library
# ==============================
try:
    from danmaku_engine import BulletPool, Bullet, Pattern
except ImportError:
    from danmaku_engine import BulletPool, Bullet, Pattern


# ==============================
# Talisman Bullet (rectangle)
# ==============================
class TalismanBullet(Bullet):
    __slots__ = ('x', 'y', 'vx', 'vy', 'radius', 'color', 'life', 'angle', 'width', 'height', 'is_mokou')

    def __init__(self, x, y, vx=0, vy=0, color=(255, 0, 0), angle=0, width=10, height=4):
        super().__init__(x, y, vx, vy, width//2, color)
        self.angle = angle
        self.width = width
        self.height = height
        self.is_mokou = True
        self.life = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life += 1

    def draw(self, surf, offset=(0, 0)):
        ox, oy = offset
        cx = int(self.x + ox)
        cy = int(self.y + oy)
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        hw = self.width / 2
        hh = self.height / 2
        points = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        rotated = []
        for px, py in points:
            rx = px * cos_a - py * sin_a + cx
            ry = px * sin_a + py * cos_a + cy
            rotated.append((rx, ry))
        pygame.draw.polygon(surf, self.color, rotated)
        pygame.draw.polygon(surf, (min(255, self.color[0]+50),
                                   min(255, self.color[1]+50),
                                   min(255, self.color[2]+50)), rotated, 1)


# ==============================
# Stage 1: Windmill (mokou_non1)
# rotation_speed = 0.015
# ==============================
class Stage1Pattern(Pattern):
    def __init__(self):
        self.big_arms = 3
        self.small_arms = 6
        self.colors = [
            (255, 60, 60), (255, 60, 60),
            (60, 60, 255), (60, 60, 255),
            (255, 200, 50), (255, 200, 50)
        ]
        self.small_arm_spread = 8 * math.pi / 180
        self.radial_speed = 3.0
        self.rotation_speed = 0.015
        self.angle = 0.0
        self.max_life = 500
        self.spawn_interval = 5
        self.frame_counter = 0
        self.start_dist = 20

    def generate(self, pool, cx, cy):
        self.angle += self.rotation_speed
        self.frame_counter += 1
        if self.frame_counter % self.spawn_interval != 0:
            return

        for big in range(self.big_arms):
            base_angle = self.angle + big * (2 * math.pi / 3)
            for small in range(self.small_arms):
                offset = (small - 2.5) * self.small_arm_spread
                arm_angle = base_angle + offset
                color = self.colors[small]

                x = cx + math.cos(arm_angle) * self.start_dist
                y = cy + math.sin(arm_angle) * self.start_dist
                vx = math.cos(arm_angle) * self.radial_speed
                vy = math.sin(arm_angle) * self.radial_speed

                bullet = TalismanBullet(x, y, vx, vy, color=color, angle=arm_angle)
                bullet.life = 0
                pool.add(bullet)


# ==============================
# Stage 2: Speed-diff Windmill
# rotation_speed = 0.015
# ==============================
class Stage2Pattern(Pattern):
    def __init__(self):
        self.big_arms = 3
        self.small_arms = 6
        self.colors = [
            (255, 60, 60), (255, 60, 60),
            (60, 60, 255), (60, 60, 255),
            (255, 200, 50), (255, 200, 50)
        ]
        self.color_speed_map = {
            (255, 60, 60): 3.0,
            (60, 60, 255): 5.0,
            (255, 200, 50): 2.0
        }
        self.small_arm_spread = 8 * math.pi / 180
        self.rotation_speed = 0.015
        self.angle = 0.0
        self.max_life = 500
        self.spawn_interval = 5
        self.frame_counter = 0
        self.start_dist = 20

    def generate(self, pool, cx, cy):
        self.angle += self.rotation_speed
        self.frame_counter += 1
        if self.frame_counter % self.spawn_interval != 0:
            return

        for big in range(self.big_arms):
            base_angle = self.angle + big * (2 * math.pi / 3)
            for small in range(self.small_arms):
                offset = (small - 2.5) * self.small_arm_spread
                arm_angle = base_angle + offset
                color = self.colors[small]
                speed = self.color_speed_map.get(color, 3.0)

                x = cx + math.cos(arm_angle) * self.start_dist
                y = cy + math.sin(arm_angle) * self.start_dist
                vx = math.cos(arm_angle) * speed
                vy = math.sin(arm_angle) * speed

                bullet = TalismanBullet(x, y, vx, vy, color=color, angle=arm_angle)
                bullet.life = 0
                pool.add(bullet)


# ==============================
# Stage 3: Bloom Talisman (Purple 2.0 / Yellow 1.5)
# ==============================
class Stage3Pattern(Pattern):
    def __init__(self):
        self.purple_speed = 2.0
        self.purple_count = 60
        self.purple_interval = 20
        self.purple_timer = 0
        self.purple_color = (180, 50, 255)
        self.purple_size = (10, 4)

        self.yellow_speed = 1.5
        self.yellow_count = 60
        self.yellow_interval = 20
        self.yellow_timer = 0
        self.yellow_color = (255, 220, 50)
        self.yellow_size = (10, 4)

        self.max_life = 800

    def generate(self, pool, cx, cy):
        self.purple_timer += 1
        if self.purple_timer >= self.purple_interval:
            self.purple_timer = 0
            start_angle = random.uniform(0, 2 * math.pi)
            for i in range(self.purple_count):
                angle = start_angle + 2 * math.pi * i / self.purple_count
                vx = math.cos(angle) * self.purple_speed
                vy = math.sin(angle) * self.purple_speed
                bullet = TalismanBullet(
                    cx, cy, vx, vy,
                    color=self.purple_color,
                    angle=angle,
                    width=self.purple_size[0],
                    height=self.purple_size[1]
                )
                bullet.life = 0
                pool.add(bullet)

        self.yellow_timer += 1
        if self.yellow_timer >= self.yellow_interval:
            self.yellow_timer = 0
            start_angle = random.uniform(0, 2 * math.pi)
            for i in range(self.yellow_count):
                angle = start_angle + 2 * math.pi * i / self.yellow_count
                vx = math.cos(angle) * self.yellow_speed
                vy = math.sin(angle) * self.yellow_speed
                bullet = TalismanBullet(
                    cx, cy, vx, vy,
                    color=self.yellow_color,
                    angle=angle,
                    width=self.yellow_size[0],
                    height=self.yellow_size[1]
                )
                bullet.life = 0
                pool.add(bullet)


# ==============================
# Stage 4: Bloom Talisman (Purple 3.0 / Yellow 1.5)
# ==============================
class Stage4Pattern(Stage3Pattern):
    def __init__(self):
        super().__init__()
        self.purple_speed = 3.0
        self.purple_count = 60
        self.yellow_speed = 1.5
        self.yellow_count = 60


# ==============================
# Stage 5: Bloom Ring (Purple 3.0 / Yellow 1.5)  ← mokou_non4
# ==============================
class Stage5Pattern(Pattern):
    def __init__(self):
        self.purple_speed = 3.0
        self.purple_count = 60
        self.purple_interval = 20
        self.purple_timer = 0
        self.purple_color = (180, 50, 255)
        self.purple_size = (10, 4)

        self.yellow_speed = 1.5
        self.yellow_count = 60
        self.yellow_interval = 20
        self.yellow_timer = 0
        self.yellow_color = (255, 220, 50)
        self.yellow_size = (10, 4)

        self.center_radius = 50
        self.max_life = 800

    def generate(self, pool, cx, cy):
        # ---- 紫色开花弹（爆炸中心随机） ----
        self.purple_timer += 1
        if self.purple_timer >= self.purple_interval:
            self.purple_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.center_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            for i in range(self.purple_count):
                angle = 2 * math.pi * i / self.purple_count
                vx = math.cos(angle) * self.purple_speed
                vy = math.sin(angle) * self.purple_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.purple_color,
                    angle=angle,
                    width=self.purple_size[0],
                    height=self.purple_size[1]
                )
                bullet.life = 0
                pool.add(bullet)

        # ---- 黄色开花弹（爆炸中心随机） ----
        self.yellow_timer += 1
        if self.yellow_timer >= self.yellow_interval:
            self.yellow_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.center_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            offset_angle = random.uniform(0, 2 * math.pi / self.purple_count)
            for i in range(self.yellow_count):
                angle = offset_angle + 2 * math.pi * i / self.yellow_count
                vx = math.cos(angle) * self.yellow_speed
                vy = math.sin(angle) * self.yellow_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.yellow_color,
                    angle=angle,
                    width=self.yellow_size[0],
                    height=self.yellow_size[1]
                )
                bullet.life = 0
                pool.add(bullet)


# ==============================
# Stage 6: Bloom Ring (Purple 4.0 / Yellow 1.5)  ← mokou_non5
# ==============================
class Stage6Pattern(Stage5Pattern):
    def __init__(self):
        super().__init__()
        self.purple_speed = 4.0
        self.purple_count = 60
        self.yellow_speed = 1.5
        self.yellow_count = 60
        self.center_radius = 50


# ==============================
# Stage 7: Full Purple Bloom (Purple 5.0, 2x freq)  ← mokou_non6
# ==============================
class Stage7Pattern(Pattern):
    def __init__(self):
        self.purple_speed = 5.0
        self.purple_count = 60
        self.purple_interval = 10
        self.purple_timer = 0
        self.purple_color = (180, 50, 255)
        self.purple_size = (10, 4)

        self.center_radius = 80
        self.max_life = 800

    def generate(self, pool, cx, cy):
        self.purple_timer += 1
        if self.purple_timer >= self.purple_interval:
            self.purple_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.center_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            for i in range(self.purple_count):
                angle = 2 * math.pi * i / self.purple_count
                vx = math.cos(angle) * self.purple_speed
                vy = math.sin(angle) * self.purple_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.purple_color,
                    angle=angle,
                    width=self.purple_size[0],
                    height=self.purple_size[1]
                )
                bullet.life = 0
                pool.add(bullet)


# ==============================
# Stage 8: Bloom Ring (Purple 5.0 / Yellow 1.5, r100/80)  ← mokou_non7
# ==============================
class Stage8Pattern(Pattern):
    def __init__(self):
        # 紫弹
        self.purple_speed = 5.0
        self.purple_count = 60
        self.purple_interval = 10
        self.purple_timer = 0
        self.purple_color = (180, 50, 255)
        self.purple_size = (10, 4)
        self.purple_radius = 100

        # 黄弹
        self.yellow_speed = 1.5
        self.yellow_count = 60
        self.yellow_interval = 20
        self.yellow_timer = 0
        self.yellow_color = (255, 220, 50)
        self.yellow_size = (10, 4)
        self.yellow_radius = 80

        self.max_life = 800

    def generate(self, pool, cx, cy):
        # 紫弹
        self.purple_timer += 1
        if self.purple_timer >= self.purple_interval:
            self.purple_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.purple_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            for i in range(self.purple_count):
                angle = 2 * math.pi * i / self.purple_count
                vx = math.cos(angle) * self.purple_speed
                vy = math.sin(angle) * self.purple_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.purple_color,
                    angle=angle,
                    width=self.purple_size[0],
                    height=self.purple_size[1]
                )
                bullet.life = 0
                pool.add(bullet)

        # 黄弹
        self.yellow_timer += 1
        if self.yellow_timer >= self.yellow_interval:
            self.yellow_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.yellow_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            offset_angle = random.uniform(0, 2 * math.pi / self.purple_count)
            for i in range(self.yellow_count):
                angle = offset_angle + 2 * math.pi * i / self.yellow_count
                vx = math.cos(angle) * self.yellow_speed
                vy = math.sin(angle) * self.yellow_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.yellow_color,
                    angle=angle,
                    width=self.yellow_size[0],
                    height=self.yellow_size[1]
                )
                bullet.life = 0
                pool.add(bullet)


# ==============================
# Stage 9: Triple Bloom (Purple 6.0 / Yellow 3.0 / Red 1.5)  ← mokou_non8
# ==============================
class Stage9Pattern(Pattern):
    def __init__(self):
        # 紫弹
        self.purple_speed = 6.0
        self.purple_count = 60
        self.purple_interval = 10
        self.purple_timer = 0
        self.purple_color = (180, 50, 255)
        self.purple_size = (10, 4)
        self.purple_radius = 100

        # 黄弹
        self.yellow_speed = 3.0
        self.yellow_count = 60
        self.yellow_interval = 20
        self.yellow_timer = 0
        self.yellow_color = (255, 220, 50)
        self.yellow_size = (10, 4)
        self.yellow_radius = 80

        # 红弹
        self.red_speed = 1.5
        self.red_count = 60
        self.red_interval = 20
        self.red_timer = 0
        self.red_color = (255, 50, 50)
        self.red_size = (10, 4)
        self.red_radius = 60

        self.max_life = 800

    def generate(self, pool, cx, cy):
        # 紫弹
        self.purple_timer += 1
        if self.purple_timer >= self.purple_interval:
            self.purple_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.purple_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            for i in range(self.purple_count):
                angle = 2 * math.pi * i / self.purple_count
                vx = math.cos(angle) * self.purple_speed
                vy = math.sin(angle) * self.purple_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.purple_color,
                    angle=angle,
                    width=self.purple_size[0],
                    height=self.purple_size[1]
                )
                bullet.life = 0
                pool.add(bullet)

        # 黄弹
        self.yellow_timer += 1
        if self.yellow_timer >= self.yellow_interval:
            self.yellow_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.yellow_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            offset_angle = random.uniform(0, 2 * math.pi / self.purple_count)
            for i in range(self.yellow_count):
                angle = offset_angle + 2 * math.pi * i / self.yellow_count
                vx = math.cos(angle) * self.yellow_speed
                vy = math.sin(angle) * self.yellow_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.yellow_color,
                    angle=angle,
                    width=self.yellow_size[0],
                    height=self.yellow_size[1]
                )
                bullet.life = 0
                pool.add(bullet)

        # 红弹
        self.red_timer += 1
        if self.red_timer >= self.red_interval:
            self.red_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.red_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            offset_angle = random.uniform(0, 2 * math.pi / self.purple_count)
            for i in range(self.red_count):
                angle = offset_angle + 2 * math.pi * i / self.red_count
                vx = math.cos(angle) * self.red_speed
                vy = math.sin(angle) * self.red_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.red_color,
                    angle=angle,
                    width=self.red_size[0],
                    height=self.red_size[1]
                )
                bullet.life = 0
                pool.add(bullet)


# ==============================
# Stage 10: Quad Bloom (Purple 7.0 / Yellow 5.0 / Red 3.0 / Green 1.5)  ← mokou_non9 FINAL
# ==============================
class Stage10Pattern(Pattern):
    def __init__(self):
        # 紫弹（最快，最大范围）
        self.purple_speed = 7.0
        self.purple_count = 60
        self.purple_interval = 10
        self.purple_timer = 0
        self.purple_color = (180, 50, 255)
        self.purple_size = (10, 4)
        self.purple_radius = 120

        # 黄弹（快速，中范围）
        self.yellow_speed = 5.0
        self.yellow_count = 60
        self.yellow_interval = 10
        self.yellow_timer = 0
        self.yellow_color = (255, 220, 50)
        self.yellow_size = (10, 4)
        self.yellow_radius = 80

        # 红弹（中速，中范围）
        self.red_speed = 3.0
        self.red_count = 60
        self.red_interval = 20
        self.red_timer = 0
        self.red_color = (255, 50, 50)
        self.red_size = (10, 4)
        self.red_radius = 80

        # 绿弹（慢速，最大范围）
        self.green_speed = 1.5
        self.green_count = 60
        self.green_interval = 20
        self.green_timer = 0
        self.green_color = (50, 255, 100)
        self.green_size = (10, 4)
        self.green_radius = 120

        self.max_life = 800

    def generate(self, pool, cx, cy):
        # 紫弹
        self.purple_timer += 1
        if self.purple_timer >= self.purple_interval:
            self.purple_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.purple_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            for i in range(self.purple_count):
                angle = 2 * math.pi * i / self.purple_count
                vx = math.cos(angle) * self.purple_speed
                vy = math.sin(angle) * self.purple_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.purple_color,
                    angle=angle,
                    width=self.purple_size[0],
                    height=self.purple_size[1]
                )
                bullet.life = 0
                pool.add(bullet)

        # 黄弹
        self.yellow_timer += 1
        if self.yellow_timer >= self.yellow_interval:
            self.yellow_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.yellow_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            offset_angle = random.uniform(0, 2 * math.pi / self.purple_count)
            for i in range(self.yellow_count):
                angle = offset_angle + 2 * math.pi * i / self.yellow_count
                vx = math.cos(angle) * self.yellow_speed
                vy = math.sin(angle) * self.yellow_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.yellow_color,
                    angle=angle,
                    width=self.yellow_size[0],
                    height=self.yellow_size[1]
                )
                bullet.life = 0
                pool.add(bullet)

        # 红弹
        self.red_timer += 1
        if self.red_timer >= self.red_interval:
            self.red_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.red_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            offset_angle = random.uniform(0, 2 * math.pi / self.purple_count)
            for i in range(self.red_count):
                angle = offset_angle + 2 * math.pi * i / self.red_count
                vx = math.cos(angle) * self.red_speed
                vy = math.sin(angle) * self.red_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.red_color,
                    angle=angle,
                    width=self.red_size[0],
                    height=self.red_size[1]
                )
                bullet.life = 0
                pool.add(bullet)

        # 绿弹
        self.green_timer += 1
        if self.green_timer >= self.green_interval:
            self.green_timer = 0
            center_angle = random.uniform(0, 2 * math.pi)
            center_dist = random.uniform(0, self.green_radius)
            center_x = cx + math.cos(center_angle) * center_dist
            center_y = cy + math.sin(center_angle) * center_dist

            offset_angle = random.uniform(0, 2 * math.pi / self.purple_count)
            for i in range(self.green_count):
                angle = offset_angle + 2 * math.pi * i / self.green_count
                vx = math.cos(angle) * self.green_speed
                vy = math.sin(angle) * self.green_speed
                bullet = TalismanBullet(
                    center_x, center_y, vx, vy,
                    color=self.green_color,
                    angle=angle,
                    width=self.green_size[0],
                    height=self.green_size[1]
                )
                bullet.life = 0
                pool.add(bullet)


# ==============================
# Player
# ==============================
class Player:
    def __init__(self, x, y):
        self.spawn_x = x
        self.spawn_y = y
        self.x = x
        self.y = y
        self.radius = 12
        self.hit_radius = 3
        self.high_speed = 4.0
        self.low_speed = 2.0
        self.speed = self.high_speed
        self.fast_mode = True
        self.alive = True
        self.lives = 4
        self.max_lives = 4
        self.invincible = 0
        self.bombs = 3
        self.god_mode = False

    def toggle_speed(self):
        self.fast_mode = not self.fast_mode
        self.speed = self.high_speed if self.fast_mode else self.low_speed

    def toggle_god(self):
        self.god_mode = not self.god_mode
        print(f"God Mode: {'ON' if self.god_mode else 'OFF'}")

    def update(self, keys, bounds):
        if not self.alive:
            return

        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        self.x += dx
        self.y += dy
        self.x = max(bounds[0] + self.radius, min(bounds[2] - self.radius, self.x))
        self.y = max(bounds[1] + self.radius, min(bounds[3] - self.radius, self.y))

        if self.invincible > 0:
            self.invincible -= 1

    def draw(self, surf):
        if not self.alive:
            return

        if self.invincible > 0 and self.invincible % 6 < 3:
            return

        if self.god_mode:
            color = (255, 215, 0)
        else:
            color = (0, 255, 0) if self.fast_mode else (0, 200, 255)

        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius, 2)

        pygame.draw.line(surf, color,
                         (int(self.x - self.radius * 0.6), int(self.y)),
                         (int(self.x + self.radius * 0.6), int(self.y)), 1)
        pygame.draw.line(surf, color,
                         (int(self.x), int(self.y - self.radius * 0.6)),
                         (int(self.x), int(self.y + self.radius * 0.6)), 1)

        pygame.draw.circle(surf, (255, 50, 50),
                           (int(self.x), int(self.y)), self.hit_radius)

        if not self.fast_mode:
            pygame.draw.circle(surf, (0, 200, 255, 80),
                               (int(self.x), int(self.y)), self.radius + 6, 1)

        if self.god_mode:
            pygame.draw.circle(surf, (255, 215, 0, 80),
                               (int(self.x), int(self.y)), self.radius + 10, 2)

    def check_collision(self, pool):
        if not self.alive:
            return False
        if self.invincible > 0:
            return False
        if self.god_mode:
            return False
        for b in pool.bullets:
            dx = self.x - b.x
            dy = self.y - b.y
            dist_sq = dx*dx + dy*dy
            threshold = self.hit_radius + b.radius
            if dist_sq < threshold * threshold:
                return True
        return False

    def take_damage(self):
        self.lives -= 1
        if self.lives <= 0:
            self.alive = False
            return False
        else:
            self.respawn()
            return True

    def respawn(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.alive = True
        self.invincible = 180

    def use_bomb(self, pool):
        if self.bombs > 0 and self.alive:
            self.bombs -= 1
            pool.clear()
            self.invincible = 60
            return True
        return False

    def reset(self, x, y):
        self.spawn_x = x
        self.spawn_y = y
        self.x = x
        self.y = y
        self.alive = True
        self.lives = 4
        self.invincible = 0
        self.bombs = 3
        self.fast_mode = True
        self.speed = self.high_speed
        self.god_mode = False


# ==============================
# Boss
# ==============================
class Boss:
    def __init__(self):
        self.x = 200
        self.y = 100
        self.radius = 20
        self.color = (255, 50, 50)
        self.move_timer = 0
        self.move_interval = 300
        self.target_x = 200
        self.target_y = 100
        self.speed = 2

    def update(self):
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            self.target_x = random.randint(50, 350)
            self.target_y = random.randint(50, 150)

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            step = min(self.speed, dist)
            self.x += dx / dist * step
            self.y += dy / dist * step

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, (255, 100, 100), (int(self.x), int(self.y)), self.radius-4)
        pygame.draw.circle(surf, (255, 255, 255), (int(self.x)-8, int(self.y)-5), 5)
        pygame.draw.circle(surf, (255, 255, 255), (int(self.x)+8, int(self.y)-5), 5)
        pygame.draw.circle(surf, (0, 0, 0), (int(self.x)-6, int(self.y)-3), 2)
        pygame.draw.circle(surf, (0, 0, 0), (int(self.x)+10, int(self.y)-3), 2)

    def reset(self):
        self.__init__()


# ==============================
# Start Screen (10 Stages)
# ==============================
class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 18)
        self.selected = 0
        self.options = ["Start Game", "Exit"]

    def run(self):
        while True:
            self.screen.fill((10, 10, 30))

            title = self.font.render("Bullet Survival", True, (255, 200, 100))
            title_rect = title.get_rect(center=(200, 60))
            self.screen.blit(title, title_rect)

            subtitle = self.small_font.render("Mokou - 10 Stages", True, (200, 200, 200))
            sub_rect = subtitle.get_rect(center=(200, 100))
            self.screen.blit(subtitle, sub_rect)

            stages_text = [
                "Stage 1: Windmill",
                "Stage 2: Diff-Speed Windmill",
                "Stage 3: Bloom Talisman (P2.0/Y1.5)",
                "Stage 4: Bloom Talisman (P3.0/Y1.5)",
                "Stage 5: Bloom Ring (P3.0/Y1.5)",
                "Stage 6: Bloom Ring (P4.0/Y1.5)",
                "Stage 7: Full Purple (P5.0, 2x)",
                "Stage 8: Bloom Ring (P5.0/Y1.5, r100/80)  ← NEW",
                "Stage 9: Triple Bloom (P6/Y3/R1.5)      ← NEW",
                "Stage 10: Quad Bloom (P7/Y5/R3/G1.5)    ★ FINAL"
            ]
            for i, text in enumerate(stages_text):
                color = (150, 150, 180)
                if "★ FINAL" in text:
                    color = (255, 215, 0)
                elif "NEW" in text:
                    color = (100, 255, 100)
                t = self.tiny_font.render(text, True, color)
                self.screen.blit(t, (30, 130 + i * 19))

            controls = [
                "WASD / Arrows: Move",
                "Shift: Toggle High/Low Speed",
                "B: Bomb (Clear + Invincible)",
                "Q: God Mode (On/Off)",
                "R: Restart Stage"
            ]
            for i, text in enumerate(controls):
                t = self.tiny_font.render(text, True, (120, 120, 120))
                self.screen.blit(t, (60, 340 + i * 22))

            for i, option in enumerate(self.options):
                color = (255, 255, 255) if i == self.selected else (150, 150, 150)
                text = self.small_font.render(option, True, color)
                rect = text.get_rect(center=(200, 500 + i * 40))
                self.screen.blit(text, rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if self.selected == 0:
                            return "start"
                        else:
                            return None
                    elif event.key == pygame.K_ESCAPE:
                        return None

            pygame.time.wait(50)


# ==============================
# Main Game (10 Stages)
# ==============================
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((400, 700))
        pygame.display.set_caption("Mokou - Bullet Survival (10 Stages)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 36)
        self.huge_font = pygame.font.Font(None, 48)

        # Load music
        try:
            pygame.mixer.music.load("music.wav")
            pygame.mixer.music.set_volume(0.7)
            pygame.mixer.music.play(-1)
            print("Music loaded: music.wav")
        except Exception as e:
            print(f"Music load failed: {e}")

        # 10 个关卡
        self.stage_patterns = [
            ("Stage 1", Stage1Pattern),
            ("Stage 2", Stage2Pattern),
            ("Stage 3", Stage3Pattern),
            ("Stage 4", Stage4Pattern),
            ("Stage 5", Stage5Pattern),
            ("Stage 6", Stage6Pattern),
            ("Stage 7", Stage7Pattern),
            ("Stage 8", Stage8Pattern),    # mokou_non7
            ("Stage 9", Stage9Pattern),    # mokou_non8
            ("Stage 10 ★", Stage10Pattern) # mokou_non9 FINAL
        ]
        self.current_stage = 0
        self.target_time = 30
        self.reset_game()

    def reset_game(self):
        self.pool = BulletPool()
        pattern_class = self.stage_patterns[self.current_stage][1]
        self.pattern = pattern_class()
        self.boss = Boss()
        self.player = Player(200, 600)
        self.paused = False
        self.game_over = False
        self.victory = False
        self.hit_cooldown = 0
        self.survival_time = 0
        self.frame_count = 0
        self.stage_complete = False

    def start_game(self):
        self.current_stage = 0
        self.reset_game()
        self.run()

    def next_stage(self):
        self.current_stage += 1
        if self.current_stage >= len(self.stage_patterns):
            self.show_victory_screen()
            return False
        self.reset_game()
        print(f"Enter {self.stage_patterns[self.current_stage][0]}")
        return True

    def show_victory_screen(self):
        while True:
            self.screen.fill((10, 10, 30))
            text = self.big_font.render("All 10 Stages Clear!", True, (255, 215, 0))
            rect = text.get_rect(center=(200, 300))
            self.screen.blit(text, rect)
            sub = self.font.render("Press SPACE or R to restart", True, (200, 200, 200))
            sub_rect = sub.get_rect(center=(200, 350))
            self.screen.blit(sub, sub_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                        self.current_stage = 0
                        self.reset_game()
                        self.run()
                        return
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            pygame.time.wait(50)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_over:
                            self.reset_game()
                        elif self.victory:
                            if not self.next_stage():
                                return
                        else:
                            self.paused = not self.paused
                    elif event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        print("Game reset")
                    elif event.key == pygame.K_b or event.key == pygame.K_x:
                        if not self.paused and not self.game_over and not self.victory and self.player.alive:
                            self.player.use_bomb(self.pool)
                    elif event.key == pygame.K_q:
                        if not self.paused and not self.game_over and not self.victory and self.player.alive:
                            self.player.toggle_god()
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        if not self.paused and not self.game_over and not self.victory and self.player.alive:
                            self.player.toggle_speed()

            if self.paused or self.game_over or self.victory:
                self.draw()
                pygame.display.flip()
                self.clock.tick(60)
                continue

            keys = pygame.key.get_pressed()
            self.player.update(keys, (0, 50, 400, 700))
            self.boss.update()

            self.pattern.generate(self.pool, self.boss.x, self.boss.y)

            for b in self.pool.bullets[:]:
                b.update()
                if b.life > self.pattern.max_life:
                    self.pool.bullets.remove(b)
            self.pool.bullets = [b for b in self.pool.bullets
                                 if -100 < b.x < 500 and -100 < b.y < 800]

            if self.player.check_collision(self.pool):
                if self.hit_cooldown == 0:
                    self.hit_cooldown = 10
                    if not self.player.take_damage():
                        self.game_over = True
                        self.player.alive = False
                    else:
                        self.pool.clear()

            if self.hit_cooldown > 0:
                self.hit_cooldown -= 1

            self.frame_count += 1
            if self.frame_count % 60 == 0:
                self.survival_time += 1
                if self.survival_time >= self.target_time:
                    self.victory = True
                    print(f"{self.stage_patterns[self.current_stage][0]} Clear!")

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def draw(self):
        self.screen.fill((10, 10, 30))
        pygame.draw.line(self.screen, (40, 40, 80), (0, 50), (400, 50), 2)

        for b in self.pool.bullets:
            b.draw(self.screen)

        self.boss.draw(self.screen)
        self.player.draw(self.screen)

        remaining = max(0, self.target_time - self.survival_time)
        time_color = (100, 255, 100) if remaining > 10 else (255, 200, 50) if remaining > 5 else (255, 50, 50)
        time_text = self.huge_font.render(f"{remaining}s", True, time_color)
        self.screen.blit(time_text, (290, 5))

        stage_name = self.stage_patterns[self.current_stage][0]
        name_text = self.font.render(stage_name, True, (200, 200, 255))
        self.screen.blit(name_text, (10, 5))

        lives_text = "♥" * self.player.lives
        mode_text = "High" if self.player.fast_mode else "Low"
        info = [
            f"Lives: {lives_text}",
            f"Bomb: {'★' * self.player.bombs}",
            f"Speed: {mode_text} ({self.player.speed:.1f})",
            f"Bullets: {len(self.pool.bullets)}"
        ]
        for i, line in enumerate(info):
            color = (200, 200, 200)
            if line.startswith("Lives"):
                color = (255, 50, 50)
            elif line.startswith("Bomb"):
                color = (100, 200, 255)
            elif line.startswith("Speed"):
                color = (0, 255, 0) if self.player.fast_mode else (0, 200, 255)
            text = self.font.render(line, True, color)
            self.screen.blit(text, (10, 55 + i * 20))

        if self.player.god_mode:
            god_text = self.font.render("★ GOD MODE ON", True, (255, 215, 0))
            self.screen.blit(god_text, (10, 150))

        tips = "WASD Move | Shift Speed | B Bomb | Q God | R Restart | SPACE Pause"
        tip_text = self.font.render(tips, True, (100, 100, 100))
        self.screen.blit(tip_text, (10, 680))

        if self.paused:
            pause_text = self.big_font.render("PAUSED", True, (255, 255, 255))
            rect = pause_text.get_rect(center=(200, 350))
            self.screen.blit(pause_text, rect)

        if self.game_over:
            overlay = pygame.Surface((400, 700))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            go_text = self.big_font.render("GAME OVER", True, (255, 50, 50))
            go_rect = go_text.get_rect(center=(200, 300))
            self.screen.blit(go_text, go_rect)
            restart_text = self.font.render("Press SPACE to retry", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(200, 350))
            self.screen.blit(restart_text, restart_rect)

        if self.victory:
            overlay = pygame.Surface((400, 700))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            win_text = self.big_font.render("STAGE CLEAR!", True, (255, 215, 0))
            win_rect = win_text.get_rect(center=(200, 280))
            self.screen.blit(win_text, win_rect)
            sub_text = self.font.render("Press SPACE for next stage", True, (255, 255, 255))
            sub_rect = sub_text.get_rect(center=(200, 330))
            self.screen.blit(sub_text, sub_rect)


# ==============================
# Main
# ==============================
def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 700))
    pygame.display.set_caption("Mokou - Bullet Survival (10 Stages)")

    start = StartScreen(screen)
    result = start.run()

    if result == "start":
        game = Game()
        game.start_game()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
