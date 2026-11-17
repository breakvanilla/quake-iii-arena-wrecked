"""Writes the sounds of rock breaking up under a rocket, and of the stones it throws out landing. Stone hardly rings, so they are made of filtered noise rather than tones."""
import math
import os
import random
import struct
import sys
import wave

SEED = 777
RATE = 22050
NUM_ROCK_SOUNDS = 6


class Band:
    """A two-pole band-pass filter."""

    def __init__(self, freq, q):
        w = 2 * math.pi * freq / RATE
        alpha = math.sin(w) / (2 * q)
        a0 = 1 + alpha
        self.b0, self.b2 = alpha / a0, -alpha / a0
        self.a1, self.a2 = -2 * math.cos(w) / a0, (1 - alpha) / a0
        self.x1 = self.x2 = self.y1 = self.y2 = 0.0

    def __call__(self, x):
        y = self.b0 * x + self.b2 * self.x2 - self.a1 * self.y1 - self.a2 * self.y2
        self.x2, self.x1, self.y2, self.y1 = self.x1, x, self.y1, y
        return y


def mix(dest, src, at):
    for i, s in enumerate(src):
        if 0 <= at + i < len(dest):
            dest[at + i] += s


def grain(rng, size):
    """One tiny stone ticking off another: a few milliseconds of bright noise."""
    band = Band(rng.uniform(1800, 4200) / (0.6 + size), 1.2)
    tau = 0.0015 + 0.003 * size
    return [band(rng.uniform(-1, 1)) * math.exp(-i / RATE / tau) for i in range(int(tau * 6 * RATE))]


def knock(rng, gain=1.0):
    """A stone landing on stone: a dull knock with a short crunch of grit after it."""
    n = int(0.22 * RATE)
    out = [0.0] * n
    body = [Band(rng.uniform(450, 800), 1.4), Band(rng.uniform(1200, 2200), 1.8)]
    weights = (1.0, rng.uniform(0.5, 0.8))
    thud = Band(rng.uniform(130, 200), 0.9)
    click = Band(rng.uniform(2800, 4500), 0.8)
    tau = rng.uniform(0.02, 0.038)
    for i in range(n):
        t = i / RATE
        x = rng.uniform(-1, 1)
        env = min(1.0, t / 0.0008) * math.exp(-t / tau)
        s = sum(w * b(x) for w, b in zip(weights, body)) * env
        s += 1.6 * thud(x) * min(1.0, t / 0.002) * math.exp(-t / (tau * 1.3))
        s += 0.8 * click(x) * math.exp(-t / 0.002)
        out[i] = s
    # bits knocked off it scatter for a moment
    for _ in range(rng.randint(3, 8)):
        at = 0.006 + rng.expovariate(1 / 0.035)
        mix(out, [s * rng.uniform(0.08, 0.3) for s in grain(rng, rng.random())], int(at * RATE))
    return [s * gain for s in out]


def blast(rng, length):
    """Rock giving way to a rocket: a sharp crack, a heavy thump, a crunch of
    stone breaking up and a short patter of bits coming down, over by the time
    the bang of the rocket is."""
    n = int(length * RATE)
    out = [0.0] * n
    crack = Band(3200, 0.5)
    split = Band(1100, 0.9)
    thump = Band(75, 0.8)
    for i in range(n):
        t = i / RATE
        x = rng.uniform(-1, 1)
        s = 3.0 * crack(x) * math.exp(-t / 0.005)
        s += 1.6 * split(x) * min(1.0, t / 0.002) * math.exp(-t / 0.05)
        s += 4.0 * thump(x) * min(1.0, t / 0.004) * math.exp(-t / 0.12)
        out[i] = s
    for _ in range(26):
        at = rng.expovariate(1 / 0.05)
        mix(out, knock(rng, rng.uniform(0.4, 0.9) * math.exp(-at / 0.15)), int(at * RATE))
    for _ in range(9):
        at = 0.15 + rng.expovariate(1 / 0.2)
        if at < length - 0.25:
            mix(out, knock(rng, rng.uniform(0.2, 0.4) * math.exp(-(at - 0.15) / 0.3)), int(at * RATE))
    for _ in range(160):
        at = 0.1 + rng.expovariate(1 / 0.18)
        if at < length - 0.05:
            mix(out, [s * rng.uniform(0.1, 0.3) * math.exp(-at / 0.25) for s in grain(rng, rng.random())], int(at * RATE))
    # fade the end out so nothing stops dead
    for i in range(n):
        out[i] *= min(1.0, (n - i) / (0.25 * RATE))
    return out


def write_wav(path, samples, peak, drive=2.5):
    # squash the peaks so the body of the sound comes through louder
    top = max(abs(s) for s in samples) or 1.0
    samples = [math.tanh(drive * s / top) for s in samples]
    top = max(abs(s) for s in samples) or 1.0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(b''.join(struct.pack('<h', int(s / top * peak * 32767)) for s in samples))


def main(out_dir):
    rng = random.Random(SEED)
    snd = os.path.join(out_dir, 'sound', 'wrecked-quake-iii-arena')
    for i in range(NUM_ROCK_SOUNDS):
        write_wav(os.path.join(snd, 'rock%d.wav' % (i + 1)), knock(rng), 0.8, 1.5)
    write_wav(os.path.join(snd, 'blast.wav'), blast(rng, 1.1), 0.95, 2.0)


if __name__ == '__main__':
    main(sys.argv[1])
