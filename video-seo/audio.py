#!/usr/bin/env python3
"""Bande-son de la vidéo « le SEO expliqué » : musique, bruitages et voix off.

La musique (120 BPM) et les bruitages sont synthétisés avec numpy (libres de droits).
La musique baisse automatiquement sous la voix (ducking). Les bruitages sont placés
sur les repères exportés par render.js (build/cues.json).

    python3 audio.py build/cues.json build/voice.wav build/audio.wav [--no-music]
"""
import json
import sys
import wave

import numpy as np
import soundfile as sf

SR = 48000
rng = np.random.default_rng(11)

cues_file, voice_file, out_file = sys.argv[1:4]
NO_MUSIC = '--no-music' in sys.argv
data = json.load(open(cues_file))
DUR = float(data['duration'])
CUES = data['cues']
MARKS = data['marks']
N = int((DUR + 0.5) * SR)

BEAT = 0.5
BAR = 2.0

# ---------------------------------------------------------------- helpers
def T(d):
    return np.arange(int(d * SR)) / SR


def noise(n):
    return rng.standard_normal(n)


NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def hz(name):
    semi = NAMES[name[0]]
    i = 1
    if name[i:i + 1] == '#':
        semi, i = semi + 1, i + 1
    elif name[i:i + 1] == 'b':
        semi, i = semi - 1, i + 1
    midi = 12 * (int(name[i:]) + 1) + semi
    return 440.0 * 2 ** ((midi - 69) / 12)


def fft_filter(x, gain):
    n = len(x)
    nf = 1 << (n - 1).bit_length()
    f = np.fft.rfftfreq(nf, 1 / SR)
    return np.fft.irfft(np.fft.rfft(x, nf) * gain(f), nf)[:n]


def lp(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order))


def hp(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-6)) ** (2 * order))


def bp(fc, q=1.0):
    return lambda f: 1 / np.sqrt(1 + (q * (f / fc - fc / np.maximum(f, 1e-6))) ** 2)


def svf(x, fc, q=0.7, mode='bp'):
    """Zero-delay-feedback state variable filter with a time-varying cutoff."""
    n = len(x)
    fc = np.broadcast_to(np.asarray(fc, float), (n,))
    g = np.tan(np.pi * np.clip(fc, 20, SR * 0.45) / SR)
    k = 1.0 / q
    a1 = 1.0 / (1.0 + g * (g + k))
    a2, xs = g * a1, x.tolist()
    a3 = (g * a2).tolist()
    a1, a2 = a1.tolist(), a2.tolist()
    ic1 = ic2 = 0.0
    out = [0.0] * n
    for i in range(n):
        v3 = xs[i] - ic2
        v1 = a1[i] * ic1 + a2[i] * v3
        v2 = ic2 + a2[i] * ic1 + a3[i] * v3
        ic1, ic2 = 2 * v1 - ic1, 2 * v2 - ic2
        out[i] = v1 if mode == 'bp' else v2 if mode == 'lp' else xs[i] - k * v1 - v2
    return np.array(out)


def norm(x, peak=1.0):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def saw(f, t, nh=30, roll=1.0):
    out = np.zeros_like(t)
    for k in range(1, int(min(nh, (SR / 2 - 1000) / f)) + 1):
        out += np.sin(2 * np.pi * k * f * t + 0.7 * k) / k ** roll
    return out


class Bus:
    def __init__(self):
        self.L = np.zeros(N)
        self.R = np.zeros(N)

    def add(self, sig, t0, gain=1.0, pan=0.0):
        l, r = (sig, sig) if np.ndim(sig) == 1 else sig
        a = (pan + 1) * np.pi / 4
        gl, gr = np.cos(a) * np.sqrt(2), np.sin(a) * np.sqrt(2)
        i0 = int(round(t0 * SR))
        if i0 < 0:
            l, r, i0 = l[-i0:], r[-i0:], 0
        n = min(len(l), N - i0)
        if n <= 0:
            return
        self.L[i0:i0 + n] += l[:n] * gain * gl
        self.R[i0:i0 + n] += r[:n] * gain * gr

    def mix(self, other, gain=1.0):
        self.L += other.L * gain
        self.R += other.R * gain

    def scale(self, env):
        self.L *= env
        self.R *= env

    def rms(self):
        x = np.concatenate([self.L, self.R])
        x = x[np.abs(x) > 1e-4]
        return np.sqrt(np.mean(x ** 2)) if len(x) else 0.0

    def level(self, db):
        r = self.rms()
        if r > 0:
            self.scale(10 ** (db / 20) / r)


# ---------------------------------------------------------------- instruments
def kick(soft=False):
    t = T(0.45)
    f = 52 + 120 * np.exp(-t / 0.03)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.12 if soft else 0.16))
    click = norm(fft_filter(noise(len(t)), bp(3000, 0.7))) * np.exp(-t / 0.004)
    s = s + click * (0.06 if soft else 0.16)
    return np.tanh(1.8 * s) / np.tanh(1.8)


def clap():
    t = T(0.4)
    n = norm(fft_filter(noise(len(t)), bp(1500, 0.8)))
    env = np.zeros_like(t)
    for d in (0.0, 0.011, 0.023):
        env += (t >= d) * np.exp(-np.maximum(t - d, 0) / 0.006)
    env += (t >= 0.03) * np.exp(-np.maximum(t - 0.03, 0) / 0.12) * 0.75
    return n * env


def hat(open_=False):
    t = T(0.35 if open_ else 0.08)
    n = norm(fft_filter(noise(len(t)), hp(7500, 3)))
    return n * np.exp(-t / (0.09 if open_ else 0.016))


def bass(f, dur):
    t = T(dur + 0.03)
    s = 0.6 * np.sin(2 * np.pi * f * t) + 0.6 * saw(f, t, nh=20, roll=1.0)
    env = np.minimum(1, t / 0.005) * np.exp(-t / 0.6) * np.clip((dur + 0.03 - t) / 0.03, 0, 1)
    return fft_filter(s * env, lambda fr: lp(1400, 2)(fr) * hp(38, 2)(fr))


def pad(notes, dur, bright=2600, release=0.5):
    t = T(dur + release)
    L = np.zeros_like(t)
    R = np.zeros_like(t)
    for f in map(hz, notes):
        for cents, pan in ((-9, -0.7), (0, 0.0), (9, 0.7)):
            v = saw(f * 2 ** (cents / 1200), t, nh=14, roll=1.35)
            a = (pan + 1) * np.pi / 4
            L += v * np.cos(a)
            R += v * np.sin(a)
    env = np.minimum(1, t / 0.18) * np.where(t < dur, 1.0, np.exp(-(t - dur) / (release / 3)))
    return fft_filter(L * env, lp(bright, 2)), fft_filter(R * env, lp(bright, 2))


def pluck(f, dur=0.7, bright=1.0):
    t = T(dur)
    s = (np.sin(2 * np.pi * f * t)
         + 0.5 * bright * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.05)
         + 0.25 * bright * np.sin(6 * np.pi * f * t) * np.exp(-t / 0.03))
    return s * np.minimum(1, t / 0.002) * np.exp(-t / 0.2)


def bell(f, dur=1.6, idx=1.8, ratio=3.5, tau=0.55):
    t = T(dur)
    m = idx * np.exp(-t / 0.18) * np.sin(2 * np.pi * f * ratio * t)
    return np.sin(2 * np.pi * f * t + m) * np.minimum(1, t / 0.002) * np.exp(-t / tau)


def riser(dur):
    t = T(dur)
    x = t / dur
    s = norm(svf(noise(len(t)), 300 * (9000 / 300) ** x, q=2.0)) * x ** 2.2
    tone = np.sin(2 * np.pi * np.cumsum(180 * 2 ** (3 * x)) / SR) * x ** 3 * 0.22
    return s * 0.8 + tone


def impact():
    t = T(2.6)
    boom = np.sin(2 * np.pi * np.cumsum(32 + 70 * np.exp(-t / 0.07)) / SR) * np.exp(-t / 0.55)
    thud = norm(fft_filter(noise(len(t)), lp(900))) * np.exp(-t / 0.09)
    body = np.tanh(1.5 * (boom + 0.5 * thud)) * 0.9
    cl = norm(fft_filter(noise(len(t)), hp(4500, 2))) * np.exp(-t / 1.1) * 0.22
    cr = norm(fft_filter(noise(len(t)), hp(4500, 2))) * np.exp(-t / 1.1) * 0.22
    return body + cl, body + cr


def whoosh(d=0.5, big=False):
    t = T(d)
    x = t / d
    fc = np.where(x < 0.7, 250 * (6000 / 250) ** (x / 0.7), 6000 * (700 / 6000) ** ((x - 0.7) / 0.3))
    env = np.where(x < 0.7, (x / 0.7) ** 2.2, np.exp(-(x - 0.7) / 0.3 * 3.5))
    L = svf(noise(len(t)), fc, 0.9) * env
    R = svf(noise(len(t)), fc * 1.06, 0.9) * env
    pan = np.linspace(-0.8, 0.8, len(t))
    L, R = L * np.cos((pan + 1) * np.pi / 4), R * np.sin((pan + 1) * np.pi / 4)
    if big:
        rum = norm(fft_filter(noise(len(t)), lp(160, 2))) * env * 0.6
        L, R = norm(L) + rum, norm(R) + rum
    m = max(np.max(np.abs(L)), np.max(np.abs(R)))
    return L / m, R / m


def swish():
    t = T(0.22)
    x = t / 0.22
    s = svf(noise(len(t)), 1500 * (8000 / 1500) ** x, 1.2) * np.sin(np.pi * x) ** 2
    return norm(s)


def pop(f):
    t = T(0.16)
    fr = f * (1 + 0.9 * np.exp(-t / 0.01))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    s = np.sin(ph) * np.exp(-t / 0.05) + 0.3 * np.sin(2 * ph) * np.exp(-t / 0.02)
    return s * np.minimum(1, t / 0.0008)


def key(low=False):
    t = T(0.05)
    band = rng.uniform(1200, 2000) if low else rng.uniform(2800, 4200)
    n = norm(fft_filter(noise(len(t)), bp(band, 1.4)))
    thump = np.sin(2 * np.pi * rng.uniform(120, 180) * t) * np.exp(-t / (0.016 if low else 0.008))
    return (n * np.exp(-t / 0.0045) + (0.9 if low else 0.5) * thump) * rng.uniform(0.75, 1.0)


def mouse_click():
    out = np.zeros(int(0.12 * SR))
    for t0, band, g in ((0.0, 2600, 1.0), (0.07, 1900, 0.55)):
        t = T(0.03)
        n = norm(fft_filter(noise(len(t)), bp(band, 1.6))) * np.exp(-t / 0.003) * g
        i = int(t0 * SR)
        out[i:i + len(n)] += n
    return out


def error():
    out = np.zeros(int(0.45 * SR))
    for f, t0 in ((330.0, 0.0), (247.0, 0.15)):
        t = T(0.2)
        s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t)
        s *= np.minimum(1, t / 0.004) * np.exp(-t / 0.08)
        i = int(t0 * SR)
        out[i:i + len(s)] += s
    return fft_filter(out, lp(2500))


def charge(d):
    t = T(d)
    x = t / d
    f = 260 * 2 ** (1.6 * x)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 16 * t))
    return s * np.minimum(1, x / 0.2) * np.clip((1 - x) / 0.15, 0, 1) * (0.5 + 0.5 * x)


def zip_(f):
    t = T(0.2)
    x = t / 0.2
    s = np.sin(2 * np.pi * np.cumsum(f * 2 ** x) / SR) * np.sin(np.pi * x)
    n = norm(svf(noise(len(t)), 2000 * 2 ** (1.5 * x), 2.0)) * np.sin(np.pi * x) * 0.25
    return s + n


def arp_bells(notes, gap, tau=0.5, idx=1.4):
    out = np.zeros(int((gap * len(notes) + 1.6) * SR))
    for k, n in enumerate(notes):
        b = bell(hz(n), 1.5, idx, 3.5, tau)
        i = int(k * gap * SR)
        out[i:i + len(b)] += b
    return out


def drop():
    t = T(0.27)
    x = t / 0.27
    return np.sin(2 * np.pi * np.cumsum(1400 * (600 / 1400) ** x) / SR) * np.sin(np.pi * x) ** 0.5


def sparkle(count=8):
    out = np.zeros(int(1.6 * SR))
    for k in range(count):
        b = bell(hz(['C7', 'D7', 'E7', 'G7', 'A7'][rng.integers(5)]), 0.8, 0.9, 3.5, 0.18) * rng.uniform(0.4, 1)
        i = int(k * 0.028 * SR)
        out[i:i + len(b)] += b
    return out



# ---------------------------------------------------------------- bruitages supplémentaires
def car_pass():
    t = T(1.2)
    x = t / 1.2
    f = 70 * (1.25 - 0.4 * x)                       # effet Doppler
    ph = 2 * np.pi * np.cumsum(f) / SR
    eng = np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.35 * np.sin(3 * ph) + 0.2 * np.sin(5 * ph)
    rumble = norm(fft_filter(noise(len(t)), lp(500)))
    env = np.sin(np.pi * x) ** 1.5
    s = (0.6 * eng + 0.5 * rumble) * env
    pan = np.linspace(0.7, -0.7, len(t))
    return s * np.cos((pan + 1) * np.pi / 4), s * np.sin((pan + 1) * np.pi / 4)


def cash():
    out = np.zeros(int(1.4 * SR))
    b = bell(hz('E6'), 1.2, 1.0, 2.0, 0.35) + 0.7 * bell(hz('A6'), 1.2, 1.0, 2.0, 0.3)
    out[int(0.08 * SR):int(0.08 * SR) + len(b)] += b
    for k in range(6):   # pièces
        c = bell(hz(['C7', 'E7', 'G7'][k % 3]) * rng.uniform(.98, 1.02), 0.3, 0.6, 3.1, 0.06)
        i = int((0.0 + k * 0.035) * SR)
        out[i:i + len(c)] += c * 0.4
    return out


def wind(d=2.2):
    t = T(d)
    x = t / d
    s = svf(noise(len(t)), 400 + 500 * np.sin(np.pi * x * 2) ** 2, 2.5)
    return norm(s) * np.sin(np.pi * x) ** 2


def boing():
    t = T(0.6)
    f = 180 + 260 * np.exp(-t / 0.12) + 40 * np.sin(2 * np.pi * 14 * t) * np.exp(-t / 0.3)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.25)


def slam():
    t = T(0.8)
    boom = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.25)
    hit = norm(fft_filter(noise(len(t)), bp(1800, 0.7))) * np.exp(-t / 0.03)
    return np.tanh(1.6 * (boom + 0.5 * hit))


def sputter():
    out = np.zeros(int(1.3 * SR))
    for k, t0 in enumerate((0.0, 0.16, 0.28, 0.5, 0.62, 0.95)):
        t = T(0.12)
        s = norm(fft_filter(noise(len(t)), bp(220, 0.8))) * np.exp(-t / 0.035) + 0.5 * np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.05)
        i = int(t0 * SR)
        out[i:i + len(s)] += s * (1 - k * 0.1)
    return out


def scroll_ticks():
    out = np.zeros(int(1.0 * SR))
    for k in range(14):
        c = key() * 0.6
        i = int((k * 0.06) * SR)
        out[i:i + len(c)] += c
    return out


def sad_trombone():
    out = np.zeros(int(2.2 * SR))
    notes = [(hz('D4'), 0.0, 0.32), (hz('C#4'), 0.34, 0.32), (hz('C4'), 0.68, 0.32), (hz('B3'), 1.02, 1.0)]
    for f0, t0, d in notes:
        t = T(d)
        vib = 1 + 0.012 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.2)
        ph = 2 * np.pi * np.cumsum(f0 * vib) / SR
        s = sum(np.sin(k * ph) / k ** 0.9 for k in range(1, 10))
        env = np.minimum(1, t / 0.04) * np.clip((d - t) / 0.08, 0, 1)
        i = int(t0 * SR)
        out[i:i + len(s)] += s * env
    return fft_filter(out, lp(2200))


def stamp():
    t = T(0.4)
    return np.tanh(2 * (np.sin(2 * np.pi * np.cumsum(90 + 120 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.09)
                        + 0.6 * norm(fft_filter(noise(len(t)), lp(1500))) * np.exp(-t / 0.03)))


def ring():
    out = np.zeros(int(1.0 * SR))
    for k in range(10):
        t = T(0.05)
        f = 1300 if k % 2 else 1650
        s = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t)) * np.minimum(1, t / 0.003)
        i = int(k * 0.05 * SR)
        out[i:i + len(s)] += s
    return out


def coin():
    return bell(hz('B6'), 0.5, 0.8, 3.0, 0.12) + 0.6 * bell(hz('E7'), 0.5, 0.8, 3.0, 0.1)



# ---------------------------------------------------------------- musique
CHORDS = {  # accord du pad, basse, arpège
    'Am': (['A3', 'C4', 'E4', 'A4'], 'A1', ['A4', 'C5', 'E5', 'A5']),
    'C': (['G3', 'C4', 'E4', 'G4'], 'C2', ['G4', 'C5', 'E5', 'G5']),
    'G': (['G3', 'B3', 'D4', 'G4'], 'G1', ['G4', 'B4', 'D5', 'G5']),
    'F': (['A3', 'C4', 'F4', 'A4'], 'F1', ['A4', 'C5', 'F5', 'A5']),
}
ARP = [0, 1, 2, 3, 1, 2, 3, 2]
END = MARKS['end']                 # arrivée de la carte de fin
n_bars = int(np.ceil(END / BAR))
kick_b, snare_b, hat_b, bass_b, pad_b, pluck_b, fx_b = (Bus() for _ in range(7))
groove_kicks = []
for bar in range(n_bars):
    t0 = bar * BAR
    name = ['C', 'G', 'Am', 'F'][bar % 4]
    voicing, root, arp = CHORDS[name]
    pad_b.add(pad(voicing, BAR, bright=2400), t0)
    for k in range(8):
        tk = t0 + k * BEAT / 2
        if tk < END - 0.05:
            pluck_b.add(pluck(hz(arp[ARP[k]])), tk, 1.0, pan=-0.35 if k % 2 else 0.35)
            bass_b.add(bass(hz(root) * (2 if k % 2 else 1), BEAT / 2 - 0.02), tk)
    if bar == 0:
        continue                   # 1re mesure plus légère, la batterie arrive à 2 s
    for k in range(4):
        tk = t0 + k * BEAT
        if tk >= END - 0.05:
            break
        kick_b.add(kick(), tk)
        groove_kicks.append(tk)
        if k in (1, 3):
            snare_b.add(clap(), tk)
    for k in range(16):
        tk = t0 + k * BEAT / 4
        if tk < END - 0.05:
            hat_b.add(hat(), tk, 1.0 if k % 4 == 2 else 0.35, pan=0.3 if k % 2 else -0.15)
# accord final sous la carte de fin
voicing, root, _ = CHORDS['C']
pad_b.add(pad(voicing + ['C5'], DUR - END, bright=3000, release=1.2), END)
bass_b.add(bass(hz(root), 1.6), END)
for k, n in enumerate(['C5', 'E5', 'G5', 'C6']):
    pluck_b.add(pluck(hz(n), 1.4), END + k * 0.012, 0.7, pan=(k - 1.5) * 0.3)
kick_b.add(kick(), END)
fx_b.add(riser(1.0), MARKS['seo'] - 1.0, 0.5)
fx_b.add(riser(1.0), MARKS['reveal'] - 1.0, 0.4)

duck = np.ones(N)
for tk in groove_kicks:
    i = int(tk * SR)
    n = min(int(0.45 * SR), N - i)
    tt = np.arange(n) / SR
    duck[i:i + n] *= 1 - 0.5 * np.exp(-tt / 0.13) * np.minimum(1, tt / 0.004)
for b in (bass_b, pad_b, pluck_b):
    b.scale(duck)

kick_b.level(-21)
snare_b.level(-28)
hat_b.level(-31)
bass_b.level(-24)
pad_b.level(-27)
pluck_b.level(-28)
fx_b.level(-24)
music = Bus()
for b in (kick_b, snare_b, hat_b, bass_b, pad_b, pluck_b, fx_b):
    music.mix(b)
send = Bus()
send.mix(pad_b, 0.3)
send.mix(pluck_b, 0.4)

# silence juste avant « SEO » pour que les 3 lettres claquent
tt = np.arange(N) / SR
gate = np.ones(N)
m = MARKS['seo']
gate[(tt > m - 0.32) & (tt < m - 0.005)] = 0.0
ramp = (tt >= m - 0.36) & (tt <= m - 0.32)
gate[ramp] = 1 - (tt[ramp] - (m - 0.36)) / 0.04

# ---------------------------------------------------------------- bruitages
sfx = Bus()
for c in CUES:
    t, ty, g, n = c['t'], c['type'], c.get('g', 1.0), c.get('n')
    if ty == 'pop':
        sfx.add(pop(hz(n)), t, 0.5 * g, pan=rng.uniform(-0.3, 0.3))
    elif ty == 'key':
        sfx.add(key(), t, 0.4 * g, pan=0.1)
    elif ty == 'whoosh':
        sfx.add(whoosh(c.get('d', 0.5), bool(c.get('big'))), t, 0.36 * g)
    elif ty == 'swish':
        sfx.add(swish(), t, 0.25 * g)
    elif ty == 'check':
        sfx.add(pop(hz(n)), t, 0.4 * g)
        sfx.add(bell(hz(n) * 2, 0.6, 0.8, 3.5, 0.15), t, 0.12 * g)
    elif ty == 'car':
        sfx.add(car_pass(), t, 0.3 * g)
    elif ty == 'cash':
        sfx.add(cash(), t, 0.3 * g)
    elif ty == 'tumble':
        sfx.add(wind(2.2), t, 0.25 * g)
    elif ty == 'boing':
        sfx.add(boing(), t, 0.35 * g)
    elif ty == 'slam':
        sfx.add(slam(), t, 0.5 * g)
    elif ty == 'sputter':
        sfx.add(sputter(), t, 0.4 * g)
    elif ty == 'scroll':
        sfx.add(scroll_ticks(), t, 0.3 * g)
    elif ty == 'sad':
        sfx.add(sad_trombone(), t, 0.22 * g)
    elif ty == 'stamp':
        sfx.add(stamp(), t, 0.5 * g)
    elif ty == 'ding':
        sfx.add(bell(hz(n), 1.5, 1.2, 3.5, 0.45), t, 0.3 * g)
    elif ty == 'levelup':
        sfx.add(arp_bells(['C6', 'E6', 'G6', 'C7'], 0.06), t, 0.3 * g)
    elif ty == 'scan':
        sfx.add(charge(c.get('d', 1.0)), t, 0.14 * g)
    elif ty == 'charge':
        sfx.add(charge(c.get('d', 1.0)), t, 0.16 * g)
    elif ty == 'ring':
        sfx.add(ring(), t, 0.18 * g)
    elif ty == 'click':
        sfx.add(mouse_click(), t, 1.0)
    elif ty == 'coin':
        sfx.add(coin(), t, 0.25 * g)
    elif ty == 'success':
        sfx.add(arp_bells(['G5', 'C6', 'E6'], 0.09, 0.5), t, 0.3 * g)
    elif ty == 'impact':
        sfx.add(impact(), t, 0.55 * g)
    elif ty == 'sparkle':
        sfx.add(sparkle(10), t, 0.18 * g)
sfx_send = Bus()
sfx_send.mix(sfx, 0.25)


# ---------------------------------------------------------------- réverbe
def reverb(bus, seconds=2.2):
    t = T(seconds)
    out = Bus()
    for ch, src in ((0, bus.L), (1, bus.R)):
        ir = fft_filter(noise(len(t)), lp(6000, 1)) * np.exp(-t / (seconds / 6.9))
        ir[: int(0.015 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        nf = 1 << (N + len(ir) - 1).bit_length()
        (out.L if ch == 0 else out.R)[:] = np.fft.irfft(np.fft.rfft(src, nf) * np.fft.rfft(ir, nf), nf)[:N]
    return out


wet = reverb(send)
wet.scale(0.5)
music.mix(wet)
music.scale(gate)
wet_sfx = reverb(sfx_send)
wet_sfx.scale(0.5)
sfx.mix(wet_sfx)

# ---------------------------------------------------------------- voix + ducking
v, vsr = sf.read(voice_file, always_2d=True)
v = v.mean(axis=1)
if vsr != SR:
    v = np.interp(np.linspace(0, len(v) - 1, int(len(v) * SR / vsr)), np.arange(len(v)), v)
voice = np.zeros(N)
voice[:min(len(v), N)] = v[:N]
act = voice[np.abs(voice) > 0.02]
voice *= 10 ** (-17 / 20) / np.sqrt(np.mean(act ** 2))       # voix au premier plan
win = int(0.08 * SR)
env = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode='same'))
env = np.convolve(env, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode='same')   # relâchement doux
duck_v = 1 - 0.6 * np.clip(env / (np.max(env) * 0.25), 0, 1)                   # jusqu'à -8 dB sous la voix
music.scale(duck_v)

master = Bus()
if not NO_MUSIC:
    master.mix(music)
master.mix(sfx)
master.L += voice
master.R += voice
for ch in ('L', 'R'):
    setattr(master, ch, fft_filter(getattr(master, ch), hp(32, 2)))

# fondu final
fade = np.clip((DUR - tt) / 0.8, 0, 1) ** 1.5
master.scale(fade)

# sonie -14 LUFS (mesure ITU-R BS.1770), limiteur doux sous -1 dBTP
K_SHELF = ((1.53512485958697, -2.69169618940638, 1.19839281085285), (1, -1.69065929318241, 0.73248077421585))
K_HP = ((1.0, -2.0, 1.0), (1, -1.99004745483398, 0.99007225036621))


def k_weight(f):
    z = np.exp(-2j * np.pi * f / SR)
    h = 1
    for b, a in (K_SHELF, K_HP):
        h = h * (b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z)
    return np.abs(h)


def loudness(x):
    """Sonie intégrée en LUFS : blocs de 400 ms, porte absolue -70 LUFS puis relative -10 LU."""
    p = sum(fft_filter(c, k_weight) ** 2 for c in x)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    cs = np.r_[0, np.cumsum(p)]
    ms = (cs[blk::hop] - cs[:-blk:hop][:len(cs[blk::hop])]) / blk
    lufs = lambda m: -0.691 + 10 * np.log10(m + 1e-12)
    ms = ms[lufs(ms) > -70]
    return lufs(np.mean(ms[lufs(ms) > lufs(np.mean(ms)) - 10]))


def limit(x, th=0.62, ceil=0.79):
    ax = np.abs(x)
    over = ax > th
    y = x.copy()
    y[over] = np.sign(x[over]) * (th + (ceil - th) * np.tanh((ax[over] - th) / (ceil - th)))
    return y


TARGET = -14.0
x = np.stack([master.L, master.R])[:, : int(DUR * SR)]
g = 10 ** ((TARGET - loudness(x)) / 20)
for _ in range(2):               # le limiteur retire un peu de sonie : on corrige le gain
    g *= 10 ** ((TARGET - loudness(limit(x * g))) / 20)
x = limit(x * g)
pcm = (np.clip(x.T, -1, 1) * 32767).astype('<i2')
with wave.open(out_file, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f'wrote {out_file}: {DUR:.1f}s, {loudness(x):.1f} LUFS, peak {np.max(np.abs(x)):.3f}')
