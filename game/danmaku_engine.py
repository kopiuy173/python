import pygame
import math
import random

# ==============================
# 1. 子弹类
# ==============================
class Bullet:
    __slots__ = ('x', 'y', 'vx', 'vy', 'radius', 'color', 'life')
    def __init__(self, x, y, vx=0, vy=0, radius=4, color=(255,0,0)):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.life = 0

# ==============================
# 2. 子弹池
# ==============================
class BulletPool:
    """子弹容器，负责添加、更新、绘制和清空"""
    def __init__(self):
        self.bullets = []

    def add(self, bullet):
        self.bullets.append(bullet)

    def update(self, bounds=None):
        """
        更新所有子弹位置
        bounds: (xmin, ymin, xmax, ymax) 超出则删除，为None则永不删除
        """
        if bounds:
            xmin, ymin, xmax, ymax = bounds
            self.bullets = [b for b in self.bullets
                            if xmin <= b.x <= xmax and ymin <= b.y <= ymax]
        for b in self.bullets:
            b.x += b.vx
            b.y += b.vy
            b.life += 1

    def draw(self, surf):
        for b in self.bullets:
            pygame.draw.circle(surf, b.color,
                               (int(b.x), int(b.y)),
                               max(1, int(b.radius)))

    def clear(self):
        self.bullets.clear()

    def __len__(self):
        return len(self.bullets)

    def __iter__(self):
        return iter(self.bullets)

# ==============================
# 3. 弹幕模式基类
# ==============================
class Pattern:
    def generate(self, pool, cx, cy):
        """
        在 (cx, cy) 位置生成子弹，添加到 pool 中
        """
        raise NotImplementedError

# ==============================
# 4. 预定义弹幕模式
# ==============================

class CircularPattern(Pattern):
    """圆形开花弹"""
    def __init__(self, count=16, speed=3, radius=4, color=(255,200,0), angle_offset=0):
        self.count = count
        self.speed = speed
        self.radius = radius
        self.color = color
        self.angle_offset = angle_offset

    def generate(self, pool, cx, cy):
        for i in range(self.count):
            angle = self.angle_offset + 2 * math.pi * i / self.count
            vx = math.cos(angle) * self.speed
            vy = math.sin(angle) * self.speed
            pool.add(Bullet(cx, cy, vx, vy, self.radius, self.color))
        return self  # 支持链式调用

class SpiralPattern(Pattern):
    """螺旋弹幕"""
    def __init__(self, count_per_ring=8, speed=2, radius=4, color=(0,200,255),
                 turn_speed=0.15, initial_phase=0):
        self.count_per_ring = count_per_ring
        self.speed = speed
        self.radius = radius
        self.color = color
        self.turn_speed = turn_speed
        self.phase = initial_phase

    def generate(self, pool, cx, cy):
        for i in range(self.count_per_ring):
            angle = self.phase + 2 * math.pi * i / self.count_per_ring
            vx = math.cos(angle) * self.speed
            vy = math.sin(angle) * self.speed
            pool.add(Bullet(cx, cy, vx, vy, self.radius, self.color))
        self.phase += self.turn_speed
        return self

    def reset_phase(self, new_phase=0):
        self.phase = new_phase
        return self

class AimPattern(Pattern):
    """自机狙"""
    def __init__(self, target_x, target_y, speed=4, spread=0, count=1, radius=4, color=(255,0,0)):
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.spread = spread
        self.count = count
        self.radius = radius
        self.color = color

    def generate(self, pool, cx, cy):
        base = math.atan2(self.target_y - cy, self.target_x - cx)
        for _ in range(self.count):
            angle = base + random.uniform(-self.spread, self.spread)
            spd = self.speed * random.uniform(0.9, 1.1)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            pool.add(Bullet(cx, cy, vx, vy, self.radius, self.color))
        return self

    def set_target(self, tx, ty):
        self.target_x = tx
        self.target_y = ty
        return self

class FanPattern(Pattern):
    """扇形散射弹"""
    def __init__(self, target_x, target_y, speed=4, angle_span=1.2, count=11,
                 radius=4, color=(255,100,255)):
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.angle_span = angle_span
        self.count = count
        self.radius = radius
        self.color = color

    def generate(self, pool, cx, cy):
        base = math.atan2(self.target_y - cy, self.target_x - cx)
        if self.count == 1:
            angles = [0]
        else:
            angles = [(i / (self.count - 1) - 0.5) * self.angle_span for i in range(self.count)]
        for offset in angles:
            angle = base + offset
            vx = math.cos(angle) * self.speed
            vy = math.sin(angle) * self.speed
            pool.add(Bullet(cx, cy, vx, vy, self.radius, self.color))
        return self

    def set_target(self, tx, ty):
        self.target_x = tx
        self.target_y = ty
        return self

# ==============================
# 5. 自定义轨迹模式
# ==============================
class CustomPattern(Pattern):
    """
    自定义弹幕：传入一个函数，该函数返回子弹列表或直接添加子弹
    """
    def __init__(self, generator_func):
        """
        generator_func(pool, cx, cy) 负责向 pool 添加子弹
        """
        self.generator_func = generator_func

    def generate(self, pool, cx, cy):
        self.generator_func(pool, cx, cy)
        return self

# ==============================
# 6. 高级：通过贝塞尔曲线或路径生成子弹
# ==============================
class PathPattern(Pattern):
    """
    沿路径生成子弹（路径点列表），子弹沿路径移动
    每个点是一个 (x, y, speed) 元组
    """
    def __init__(self, path_points, loop=False, radius=4, color=(0,255,255)):
        self.path = path_points  # [(x1,y1), (x2,y2), ...]
        self.loop = loop
        self.radius = radius
        self.color = color
        # 预计算每一段的向量和长度
        self.segments = []
        for i in range(len(path_points)-1):
            x1,y1 = path_points[i]
            x2,y2 = path_points[i+1]
            dx = x2-x1
            dy = y2-y1
            length = math.hypot(dx, dy)
            if length == 0:
                self.segments.append((0,0,0))
            else:
                self.segments.append((dx/length, dy/length, length))
        if loop and len(path_points)>1:
            # 首尾相连
            x1,y1 = path_points[-1]
            x2,y2 = path_points[0]
            dx = x2-x1
            dy = y2-y1
            length = math.hypot(dx, dy)
            if length == 0:
                self.segments.append((0,0,0))
            else:
                self.segments.append((dx/length, dy/length, length))

    def generate(self, pool, cx, cy):
        """
        从路径起点开始，每隔一定距离生成一颗子弹，
        每颗子弹的速度方向为路径在该点的切线方向（即段的方向）
        """
        # 简化：将每段路径等分生成子弹，每段生成1颗
        for i, (vx_unit, vy_unit, seg_len) in enumerate(self.segments):
            if seg_len == 0:
                continue
            # 取路径段的起点作为发射位置（偏移发射点）
            if i < len(self.path)-1:
                x0, y0 = self.path[i]
            else:  # 循环段
                x0, y0 = self.path[-1]
            # 发射位置 = 发射原点 + 路径起点偏移
            sx = cx + x0
            sy = cy + y0
            speed = 2  # 可配置
            vx = vx_unit * speed
            vy = vy_unit * speed
            pool.add(Bullet(sx, sy, vx, vy, self.radius, self.color))
        return self

# ==============================
# 7. 工具函数：组合多个模式
# ==============================
class CompositePattern(Pattern):
    """组合多个模式同时发射"""
    def __init__(self, patterns):
        self.patterns = patterns

    def generate(self, pool, cx, cy):
        for p in self.patterns:
            p.generate(pool, cx, cy)
        return self

# ==============================
# 8. 示例（可直接运行测试）
# ==============================
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    pool = BulletPool()

    # 创建几个弹幕模式实例
    circular = CircularPattern(count=20, speed=3, radius=4, color=(255,200,0))
    spiral = SpiralPattern(count_per_ring=12, speed=2, color=(0,200,255))
    aim = AimPattern(target_x=400, target_y=500, speed=5, spread=0.1, count=3, color=(255,50,50))
    fan = FanPattern(target_x=400, target_y=500, speed=4, angle_span=1.5, count=15, color=(255,100,255))
    path = PathPattern([(0,0), (100,0), (100,100), (0,100)], loop=True, color=(0,255,100))

    # 组合模式
    combo = CompositePattern([circular, spiral, aim])

    # 游戏循环
    running = True
    frame = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 按空格发射一次组合弹幕
                    combo.generate(pool, cx=400, cy=200)

        # 每10帧自动发射螺旋（演示）
        frame += 1
        if frame % 10 == 0:
            spiral.generate(pool, cx=400, cy=300)
        if frame % 30 == 0:
            fan.generate(pool, cx=200, cy=100)
            fan.set_target(400, 500)  # 更新目标

        # 更新（超出边界删除）
        pool.update(bounds=(-50, -50, 850, 650))

        # 绘制
        screen.fill((10, 10, 30))
        pool.draw(screen)

        # 显示子弹数量
        font = pygame.font.Font(None, 24)
        text = font.render(f"Bullets: {len(pool)}", True, (200,200,200))
        screen.blit(text, (10,10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
