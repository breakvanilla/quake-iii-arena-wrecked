import math
import os
import random
import struct
import sys

SEED = 1337


def write_tga(path, size, pixels):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    header = struct.pack('<BBBHHBHHHHBB', 0, 0, 2, 0, 0, 0, 0, 0, size, size, 32, 0x08)
    rows = []
    for y in range(size - 1, -1, -1):
        row = bytearray()
        for x in range(size):
            r, g, b, a = pixels[y * size + x]
            row += bytes((clamp(b), clamp(g), clamp(r), clamp(a)))
        rows.append(bytes(row))
    with open(path, 'wb') as f:
        f.write(header)
        f.write(b''.join(rows))


def clamp(v):
    return max(0, min(255, int(round(v))))


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


class Noise:
    def __init__(self, seed):
        rng = random.Random(seed)
        self.perm = list(range(256))
        rng.shuffle(self.perm)
        self.vals = [rng.random() for _ in range(256)]

    def _v(self, x, y):
        return self.vals[self.perm[(self.perm[x & 255] + y) & 255]]

    def value(self, x, y):
        x0, y0 = math.floor(x), math.floor(y)
        fx, fy = x - x0, y - y0
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        a = self._v(x0, y0) + (self._v(x0 + 1, y0) - self._v(x0, y0)) * sx
        b = self._v(x0, y0 + 1) + (self._v(x0 + 1, y0 + 1) - self._v(x0, y0 + 1)) * sx
        return a + (b - a) * sy

    def fbm(self, x, y, octaves=4):
        total, amp, norm = 0.0, 1.0, 0.0
        for _ in range(octaves):
            total += self.value(x, y) * amp
            norm += amp
            x, y, amp = x * 2.03, y * 2.03, amp * 0.5
        return total / norm


def polar(size, x, y):
    u = (x + 0.5) / size * 2 - 1
    v = (y + 0.5) / size * 2 - 1
    return u, v, math.hypot(u, v), math.atan2(v, u)


def rock(size, tint=(1.05, 0.96, 0.86), glow=False):
    """Broken rock for the inside of craters and for chunks; tiles in both directions.
    With glow, how brightly rock shines when it is red hot: uneven, soft patches
    with no cracks, so it sits on any wall material."""
    noise = Noise(SEED + 7)
    grain = Noise(SEED + 9)
    rng = random.Random(SEED + 8)
    cells = 11
    # one random point per cell of a wrapping grid; the rock splits where cells meet
    points = [[(i + rng.random(), j + rng.random()) for j in range(cells)] for i in range(cells)]
    shades = [[rng.uniform(0.75, 1.2) for _ in range(cells)] for _ in range(cells)]

    def tiled(fn, u, v):
        total = 0.0
        for ox in (0, 1):
            for oy in (0, 1):
                w = (1 - abs(u - ox)) * (1 - abs(v - oy))
                total += w * fn(u - ox, v - oy)
        return total

    pixels = []
    for y in range(size):
        for x in range(size):
            u, v = x / size, y / size
            px, py = u * cells, v * cells
            near = []
            for i in range(int(px) - 1, int(px) + 2):
                for j in range(int(py) - 1, int(py) + 2):
                    qx, qy = points[i % cells][j % cells]
                    near.append((math.hypot(px - qx - (i - i % cells), py - qy - (j - j % cells)), i % cells, j % cells))
            near.sort()
            gap = near[1][0] - near[0][0]
            shade = shades[near[0][1]][near[0][2]]

            n = tiled(lambda a, b: noise.fbm(a * 5 + 50, b * 5 + 50, 5), u, v)
            ridge = 1 - abs(tiled(lambda a, b: grain.fbm(a * 9 + 7, b * 9 + 7, 4), u, v) * 2 - 1)
            g = (100 + 110 * (n - 0.5) + 35 * (ridge - 0.5) + 25 * (grain.value(x * 1.7, y * 1.7) - 0.5)) * shade
            # thin, broken cracks between the faces
            broken = grain.value(x * 0.25 + 3, y * 0.25 + 3) > 0.35
            if glow:
                hot = 0.25 + 0.75 * smoothstep(0.35, 0.7, n) + 0.15 * (ridge - 0.5)
                pixels.append((255 * hot, 255 * hot, 255 * hot, 255))
                continue
            if gap < 0.035 and broken:
                g *= 0.55 + 0.45 * gap / 0.035
            pixels.append((g * tint[0], g * tint[1], g * tint[2], 255))
    return pixels


def spark(size):
    pixels = []
    for y in range(size):
        for x in range(size):
            _, _, r, _ = polar(size, x, y)
            i = math.exp(-r * r * 9) * (1.0 if r < 0.97 else 0.0)
            pixels.append((255 * i, 255 * i, 255 * i, 255))
    return pixels


def fireball(size):
    """A billowing puff of flame: lumpy and brighter inside, soft at the edge.
    Drawn additively, so black is see-through."""
    noise = Noise(SEED + 21)
    pixels = []
    for y in range(size):
        for x in range(size):
            u, v, r, _ = polar(size, x, y)
            n = noise.fbm(u * 3 + 10, v * 3 + 10, 5)
            edge = 1 - smoothstep(0.45 + 0.35 * n, 0.95, r)
            i = edge * (0.45 + 0.75 * smoothstep(0.3, 0.75, n)) * (1 - 0.35 * r)
            pixels.append((255 * i, 255 * i, 255 * i, 255))
    return pixels


def ring(size):
    """A thin, broken ring of light for shock waves."""
    noise = Noise(SEED + 23)
    pixels = []
    for y in range(size):
        for x in range(size):
            u, v, r, a = polar(size, x, y)
            band = math.exp(-((r - 0.86) / 0.06) ** 2) + 0.12 * math.exp(-((r - 0.7) / 0.18) ** 2)
            i = band * (0.55 + 0.45 * noise.value(math.cos(a) * 6 + 20, math.sin(a) * 6 + 20)) * (r < 0.99)
            pixels.append((255 * i, 255 * i, 255 * i, 255))
    return pixels


def soot(size):
    """Black soot blown out over a wall, streaked outwards. White is darkest:
    the mark shader darkens the wall by it."""
    noise = Noise(SEED + 25)
    pixels = []
    for y in range(size):
        for x in range(size):
            u, v, r, a = polar(size, x, y)
            streaks = noise.fbm(math.cos(a) * 4 + 30, math.sin(a) * 4 + 30, 4)
            blotch = noise.fbm(u * 4 + 40, v * 4 + 40, 5)
            reach = 0.55 + 0.4 * streaks
            i = (1 - smoothstep(reach * 0.35, reach, r)) * (0.55 + 0.45 * blotch) * 0.9
            pixels.append((255 * i, 255 * i, 255 * i, 255))
    return pixels


def cracks(size):
    """Cracks running out from the middle, forking as they go, with fine
    hairline cracks off them. White is darkest, like soot."""
    rng = random.Random(SEED + 27)
    img = [0.0] * (size * size)

    def plot(x, y, w):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                px, py = int(x) + dx, int(y) + dy
                if 0 <= px < size and 0 <= py < size:
                    d = math.hypot(px + 0.5 - x, py + 0.5 - y)
                    k = max(0.0, 1 - d / max(w, 0.6))
                    img[py * size + px] = max(img[py * size + px], k)

    def crack(x, y, ang, length, width, depth):
        step = 1.0
        travelled = 0.0
        while travelled < length:
            ang += rng.gauss(0, 0.18)
            x += math.cos(ang) * step
            y += math.sin(ang) * step
            travelled += step
            w = width * (1 - travelled / length) + 0.4
            plot(x, y, w)
            if depth < 3 and rng.random() < 0.025:
                crack(x, y, ang + rng.choice((-1, 1)) * rng.uniform(0.4, 1.0),
                      (length - travelled) * rng.uniform(0.35, 0.7), w * 0.7, depth + 1)
            if math.hypot(x - size / 2, y - size / 2) > size * 0.48:
                break

    c = size / 2
    count = 9
    for k in range(count):
        ang = 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / count
        start = size * rng.uniform(0.12, 0.2)
        crack(c + math.cos(ang) * start, c + math.sin(ang) * start, ang,
              size * rng.uniform(0.25, 0.4), rng.uniform(1.2, 2.0), 0)

    pixels = []
    for y in range(size):
        for x in range(size):
            _, _, r, _ = polar(size, x, y)
            i = img[y * size + x] * 0.85 * (1 - smoothstep(0.75, 0.98, r))
            pixels.append((255 * i, 255 * i, 255 * i, 255))
    return pixels


def smoke(size, seed):
    """A thick, lumpy ball of smoke made of a few overlapping billows, lit
    from above so it looks round. Alpha is how dense it is."""
    rng = random.Random(seed)
    noise = Noise(seed)
    blobs = [(rng.uniform(-0.28, 0.28), rng.uniform(-0.28, 0.28), rng.uniform(0.28, 0.42)) for _ in range(7)]

    def density(u, v):
        d = sum(math.exp(-2.2 * ((u - bx) ** 2 + (v - by) ** 2) / (br * br)) for bx, by, br in blobs)
        n = noise.fbm(u * 2.5 + 5, v * 2.5 + 5, 5)
        edge = 1 - smoothstep(0.62, 0.98, math.hypot(u, v))
        return max(0.0, min(1.0, d * (0.45 + 0.75 * n) * edge - 0.08))

    grid = [[density((x + 0.5) / size * 2 - 1, (y + 0.5) / size * 2 - 1) for x in range(size)] for y in range(size)]
    pixels = []
    for y in range(size):
        for x in range(size):
            d = grid[y][x]
            # facing up (towards row 0) is lit, facing down is in shadow
            above = grid[max(y - 5, 0)][x]
            below = grid[min(y + 5, size - 1)][x]
            light = 0.72 + 0.8 * (below - above)
            g = 255 * max(0.42, min(1.0, light))
            a = 255 * smoothstep(0.0, 0.7, d) * 0.92
            pixels.append((g, g, g, a))
    return pixels


def main(out_dir):
    gfx = os.path.join(out_dir, 'gfx', 'wrecked-quake-iii-arena')
    write_tga(os.path.join(gfx, 'spark.tga'), 16, spark(16))
    write_tga(os.path.join(gfx, 'rock.tga'), 128, rock(128))
    write_tga(os.path.join(gfx, 'chunk.tga'), 128, rock(128, (0.62, 0.52, 0.44)))
    write_tga(os.path.join(gfx, 'glow.tga'), 128, rock(128, glow=True))
    write_tga(os.path.join(gfx, 'fireball.tga'), 128, fireball(128))
    write_tga(os.path.join(gfx, 'ring.tga'), 128, ring(128))
    write_tga(os.path.join(gfx, 'soot.tga'), 128, soot(128))
    write_tga(os.path.join(gfx, 'cracks.tga'), 256, cracks(256))
    for i in range(3):
        write_tga(os.path.join(gfx, 'smoke%d.tga' % (i + 1)), 128, smoke(128, SEED + 40 + i))


if __name__ == '__main__':
    main(sys.argv[1])
