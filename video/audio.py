#!/usr/bin/env python3
"""Synthesises the soundtrack of the Seomastertech ad: music + sound design.

Everything is generated from scratch with numpy (no samples, no licence issue).
The music runs at 120 BPM, so one bar = 2 s and every scene change of the
animation lands on a bar line. Sound effects are placed on the cues exported by
render.js (build/cues.json), which come from the same timeline as the visuals.

    python3 audio.py build/cues.json build/audio.wav
"""
import json
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(11)

cues_file = sys.argv[1] if len(sys.argv) > 1 else 'build/cues.json'
out_file = sys.argv[2] if len(sys.argv) > 2 else 'build/audio.wav'
data = json.load(open(cues_file))
DUR = float(data['duration'])
CUES = data['cues']
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


# ---------------------------------------------------------------- music
CHORDS = {  # pad voicing, bass root, arpeggio notes
    'Am': (['A3', 'C4', 'E4', 'A4'], 'A1', ['A4', 'C5', 'E5', 'A5']),
    'C': (['G3', 'C4', 'E4', 'G4'], 'C2', ['G4', 'C5', 'E5', 'G5']),
    'G': (['G3', 'B3', 'D4', 'G4'], 'G1', ['G4', 'B4', 'D5', 'G5']),
    'F': (['A3', 'C4', 'F4', 'A4'], 'F1', ['A4', 'C5', 'F5', 'A5']),
}
PROG = ['Am', 'F', 'C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F', 'C', 'G', 'F', 'C']   # 14 bars = 28 s
ARP = [0, 1, 2, 3, 1, 2, 3, 2]

kick_b, snare_b, hat_b, bass_b, pad_b, pluck_b, fx_b = (Bus() for _ in range(7))
groove_kicks = []

for bar, name in enumerate(PROG):
    t0 = bar * BAR
    voicing, root, arp = CHORDS[name]
    intro, final = bar < 2, bar == len(PROG) - 1

    if final:   # resolution: one big chord that rings out
        pad_b.add(pad(voicing + ['C5'], 1.2, bright=3200, release=1.6), t0, 1.0)
        bass_b.add(bass(hz(root), 1.6), t0, 1.0)
        for k, n in enumerate(['C5', 'E5', 'G5', 'C6']):
            pluck_b.add(pluck(hz(n), 1.4), t0 + k * 0.012, 0.7, pan=(k - 1.5) * 0.3)
        kick_b.add(kick(), t0, 1.0)
        continue

    pad_b.add(pad(voicing, BAR - (0.125 if bar == 1 else 0.0), bright=1500 if intro else 2800), t0, 1.0)

    if intro:
        for k in range(4):   # slow, slightly melancholic arpeggio
            pluck_b.add(pluck(hz(arp[[0, 1, 2, 1][k]]), 0.9, 0.6), t0 + k * BEAT, 1.0, pan=[-0.3, 0.3, -0.2, 0.2][k])
        for k in (0, 2):     # heartbeat
            kick_b.add(kick(soft=True), t0 + k * BEAT, 0.55)
        for k in range(8):   # ticking clock
            hat_b.add(hat(), t0 + k * BEAT / 2, 0.25 if k % 2 else 0.12, pan=0.25)
        if bar == 1:
            bass_b.add(bass(hz(root), 1.8), t0, 0.6)
        continue

    for k in range(4):
        tk = t0 + k * BEAT
        kick_b.add(kick(), tk, 1.0)
        groove_kicks.append(tk)
        if k in (1, 3):
            snare_b.add(clap(), tk, 1.0)
    for k in range(16):  # 16th hats, accent on the off-beat 8ths
        acc = 1.0 if k % 4 == 2 else 0.35
        hat_b.add(hat(), t0 + k * BEAT / 4, acc, pan=0.3 if k % 2 else -0.15)
    if bar % 2 == 1:
        hat_b.add(hat(open_=True), t0 + 3.5 * BEAT, 0.6, pan=0.3)
    for k in range(8):   # octave-pumping bass
        f = hz(root) * (2 if k % 2 else 1)
        bass_b.add(bass(f, BEAT / 2 - 0.02), t0 + k * BEAT / 2, 1.0)
    for k in range(8):
        pluck_b.add(pluck(hz(arp[ARP[k]])), t0 + k * BEAT / 2, 1.0, pan=-0.35 if k % 2 else 0.35)
    if bar in (4, 6, 8):   # small clap fill into the next scene
        for k in range(4):
            snare_b.add(clap(), t0 + 3 * BEAT + k * BEAT / 4, 0.35 + 0.15 * k)

# drop into the brand reveal (4.0 s) and into the call to action (24.0 s)
fx_b.add(riser(1.15), 2.75, 0.55)
for k, tr in enumerate((3.0, 3.25, 3.5, 3.625, 3.75, 3.8125)):
    snare_b.add(clap(), tr, 0.2 + 0.1 * k)
fx_b.add(riser(1.0), 23.0, 0.45)
for k in range(8):
    snare_b.add(clap(), 23.0 + k * BEAT / 4, 0.15 + 0.08 * k)
for k in range(4):
    snare_b.add(clap(), 23.5 + k * BEAT / 8, 0.6)
for tt in (4.0, 24.0):
    fx_b.add(impact(), tt, 1.0)
fx_b.add(impact(), 26.0, 0.7)

# sidechain pumping of the tonal parts from the groove kick
duck = np.ones(N)
for tk in groove_kicks:
    i = int(tk * SR)
    n = min(int(0.45 * SR), N - i)
    tt = np.arange(n) / SR
    duck[i:i + n] *= 1 - 0.6 * np.exp(-tt / 0.13) * np.minimum(1, tt / 0.004)
for b in (bass_b, pad_b, pluck_b):
    b.scale(duck)

# ping-pong delay on the plucks (dotted eighth)
dl = int(0.375 * SR)
pl_L, pl_R = pluck_b.L.copy(), pluck_b.R.copy()
for k in range(1, 6):
    shift = np.zeros(N)
    shift[k * dl:] = (pl_L + pl_R)[:N - k * dl] * 0.5 * 0.38 ** k
    (pluck_b.L if k % 2 else pluck_b.R)[:] += shift

kick_b.level(-20)
snare_b.level(-26)
hat_b.level(-29)
bass_b.level(-23)
pad_b.level(-25)
pluck_b.level(-26)
fx_b.level(-21)

music = Bus()
for b in (kick_b, snare_b, hat_b, bass_b, pad_b, pluck_b, fx_b):
    music.mix(b)

send = Bus()
send.mix(pad_b, 0.35)
send.mix(pluck_b, 0.45)
send.mix(snare_b, 0.2)

# ---------------------------------------------------------------- sound design
sfx = Bus()
for c in CUES:
    t, ty, g = c['t'], c['type'], c.get('g', 1.0)
    n = c.get('n')
    if ty == 'pop':
        sfx.add(pop(hz(n)), t, 0.55 * g, pan=rng.uniform(-0.3, 0.3))
    elif ty == 'key':
        sfx.add(key(), t, 0.45 * g, pan=0.1)
    elif ty == 'enter':
        sfx.add(key(low=True), t, 0.7)
    elif ty == 'whoosh':
        sfx.add(whoosh(c.get('d', 0.5), bool(c.get('big'))), t, 0.42 * g)
    elif ty == 'swish':
        sfx.add(swish(), t, 0.25 * g, pan=rng.uniform(-0.4, 0.4))
    elif ty == 'error':
        sfx.add(error(), t, 0.3)
    elif ty == 'shimmer':
        sfx.add(sparkle(10), t, 0.18 * g)
    elif ty == 'charge':
        sfx.add(charge(c.get('d', 1.0)), t, 0.16 * g)
    elif ty == 'ding':
        sfx.add(bell(hz(n), 1.5, 1.2, 3.5, 0.45), t, 0.3 * g)
    elif ty == 'zip':
        sfx.add(zip_(hz(n)), t, 0.42 * g)
    elif ty == 'levelup':
        sfx.add(arp_bells(['C6', 'E6', 'G6', 'C7'], 0.06), t, 0.3 * g)
        sfx.add(sparkle(8), t + 0.2, 0.12 * g)
    elif ty == 'drop':
        sfx.add(drop(), t, 0.12 * g)
    elif ty == 'click':
        sfx.add(mouse_click(), t, 1.2)
    elif ty == 'magic':
        sfx.add(arp_bells(['G5', 'C6', 'E6', 'G6', 'C7'], 0.035, 0.35), t, 0.2 * g)
        sfx.add(swish(), t, 0.2 * g)
    elif ty == 'success':
        sfx.add(arp_bells(['G5', 'C6', 'E6'], 0.09, 0.5), t, 0.3 * g)
    elif ty == 'check':
        sfx.add(pop(hz(n)), t, 0.5 * g)
        sfx.add(bell(hz(n) * 2, 0.6, 0.8, 3.5, 0.15), t, 0.12 * g)
    elif ty == 'sparkle':
        sfx.add(sparkle(12), t, 0.2 * g)
sfx_send = Bus()
sfx_send.mix(sfx, 0.25)

# ---------------------------------------------------------------- reverb
def reverb(bus, seconds=2.4):
    t = T(seconds)
    out = Bus()
    for ch, src in ((0, bus.L), (1, bus.R)):
        ir = fft_filter(noise(len(t)), lp(6000, 1)) * np.exp(-t / (seconds / 6.9))
        ir[: int(0.015 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        nf = 1 << (N + len(ir) - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(src, nf) * np.fft.rfft(ir, nf), nf)[:N]
        (out.L if ch == 0 else out.R)[:] = y
    return out


wet = reverb(send)
wet.scale(0.5)
wet_sfx = reverb(sfx_send)
wet_sfx.scale(0.5)
sfx.mix(wet_sfx)

# gap of silence just before the drop on the brand reveal
gate = np.ones(N)
tt = np.arange(N) / SR
for t_drop in (4.0, 24.0):   # a short breath of silence before each drop
    gate[(tt > t_drop - 0.14) & (tt < t_drop - 0.005)] = 0.0
    ramp = (tt >= t_drop - 0.16) & (tt <= t_drop - 0.14)
    gate[ramp] = 1 - (tt[ramp] - (t_drop - 0.16)) / 0.02
music.mix(wet)
music.scale(gate)

master = Bus()
master.mix(music, 1.0)
master.mix(sfx, 1.0)
for ch in ('L', 'R'):   # clean up the sub rumble nobody hears on a phone
    setattr(master, ch, fft_filter(getattr(master, ch), hp(32, 2)))
SFX_ONLY = '--sfx-only' in sys.argv   # variant without music, to lay a platform sound under it

if '--stats' in sys.argv:
    def db(b, a, z):
        i, j = int(a * SR), int(z * SR)
        x = np.concatenate([b.L[i:j], b.R[i:j]])
        return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
    for a, z, what in ((1.0, 1.9, 'typing'), (2.0, 2.4, 'result pops'), (4.0, 4.4, 'logo'), (10.9, 11.9, 'rank zips'),
                       (14.8, 15.0, 'click'), (18.3, 18.9, 'chip pops'), (21.6, 22.3, 'checks'), (25.95, 26.3, 'cta click')):
        print(f'{what:12s} music {db(music, a, z):6.1f} dB   sfx {db(sfx, a, z):6.1f} dB')

# fade-out at the very end
fade = np.clip((DUR - tt) / 0.9, 0, 1) ** 1.5
master.scale(fade)
sfx.scale(fade)

# loudness: about -14 LUFS for social platforms, then soft-limit below -1 dBTP
# (the sound-effects-only variant keeps exactly the same gain as the full mix)
x = np.stack([master.L, master.R])
gain = 10 ** (-16.4 / 20) / np.sqrt(np.mean(x[:, : int(DUR * SR)] ** 2))
if SFX_ONLY:
    x = np.stack([sfx.L, sfx.R])
x *= gain
th, ceil = 0.62, 0.79
ax = np.abs(x)
over = ax > th
x[over] = np.sign(x[over]) * (th + (ceil - th) * np.tanh((ax[over] - th) / (ceil - th)))
x = x[:, : int(DUR * SR)]

pcm = (np.clip(x.T, -1, 1) * 32767).astype('<i2')
with wave.open(out_file, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f'wrote {out_file}: {DUR:.1f}s, peak {np.max(np.abs(x)):.3f}, rms {20 * np.log10(np.sqrt(np.mean(x ** 2))):.1f} dBFS')
