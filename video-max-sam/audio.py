#!/usr/bin/env python3
"""Musique et bruitages de la vidéo Max & Sam (stop motion).

    python3 audio.py

Lit build/timing.json et build/voice.wav (voice/prepare.py) et écrit :
  assets/audio/music.wav   musique 120 BPM (synthétisée, libre de droits), baissée sous les voix
  assets/audio/sfx.wav     bruitages calés sur les actions de la scène
  build/mix.wav            voix + musique + bruitages, pour mesurer la sonie

Les bruitages viennent du pack inclus avec la skill media-use (pop, whoosh, frappe clavier,
impact) ou sont synthétisés ici quand le pack n'a rien (papier froissé, tampon, sonnerie).
"""
import json
import subprocess
import unicodedata
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent
SFX_DIR = ROOT.parent / '.claude' / 'skills' / 'media-use' / 'audio' / 'assets' / 'sfx'
SR = 48000
rng = np.random.default_rng(7)

TM = json.load(open(ROOT / 'build' / 'timing.json'))
DUR = TM['duration']
END = TM['endCard']
N = int(DUR * SR)
LINE = {l['id']: l for l in TM['lines']}


def norm_word(s):
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s.lower() if c.isalnum() and unicodedata.category(c) != 'Mn')


def W(lid, word, n=0):
    return [w['start'] for w in LINE[lid]['words'] if norm_word(w['text']) == word][n]


def q(t):                      # même grille 12 i/s que l'animation
    return round(t * 12) / 12


# ---------------------------------------------------------------- outils
def T(d):
    return np.arange(int(d * SR)) / SR


def noise(n):
    return rng.standard_normal(n)


def fft_filter(x, gain):
    n = len(x)
    nf = 1 << (n - 1).bit_length()
    f = np.fft.rfftfreq(nf, 1 / SR)
    return np.fft.irfft(np.fft.rfft(x, nf) * gain(f), nf)[:n]


def lp(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order))


def hp(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-6)) ** (2 * order))


def bp(fc, q_=1.0):
    return lambda f: 1 / np.sqrt(1 + (q_ * (f / fc - fc / np.maximum(f, 1e-6))) ** 2)


def norm(x, peak=1.0):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def saw(f, t, nh=30, roll=1.0):
    out = np.zeros_like(t)
    for k in range(1, int(min(nh, (SR / 2 - 1000) / f)) + 1):
        out += np.sin(2 * np.pi * k * f * t + 0.7 * k) / k ** roll
    return out


NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def hz(name):
    semi, i = NAMES[name[0]], 1
    if name[1:2] == '#':
        semi, i = semi + 1, 2
    elif name[1:2] == 'b':
        semi, i = semi - 1, 2
    return 440.0 * 2 ** ((12 * (int(name[i:]) + 1) + semi - 69) / 12)


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
        if n > 0:
            self.L[i0:i0 + n] += l[:n] * gain * gl
            self.R[i0:i0 + n] += r[:n] * gain * gr

    def mix(self, other, gain=1.0):
        self.L += other.L * gain
        self.R += other.R * gain

    def scale(self, env):
        self.L *= env
        self.R *= env

    def level(self, db):
        x = np.concatenate([self.L, self.R])
        x = x[np.abs(x) > 1e-4]
        if len(x):
            self.scale(10 ** (db / 20) / np.sqrt(np.mean(x ** 2)))


def load(name):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(SFX_DIR / name), '-ac', '2', '-ar', str(SR),
                          '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, '<f4').astype(np.float64).reshape(-1, 2)
    return norm(x[:, 0]), norm(x[:, 1])


def pitch(sig, ratio):        # rééchantillonnage simple (varie les prises d'un même son)
    l, r = sig
    idx = np.arange(0, len(l) - 1, ratio)
    return np.interp(idx, np.arange(len(l)), l), np.interp(idx, np.arange(len(r)), r)


# ---------------------------------------------------------------- instruments (musique)
def kick():
    t = T(0.45)
    f = 52 + 120 * np.exp(-t / 0.03)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)
    return np.tanh(1.8 * s) / np.tanh(1.8)


def clap():
    t = T(0.3)
    n = norm(fft_filter(noise(len(t)), bp(1700, 0.8)))
    env = sum((t >= d) * np.exp(-np.maximum(t - d, 0) / 0.006) for d in (0.0, 0.011, 0.022))
    return n * (env + (t >= 0.03) * np.exp(-np.maximum(t - 0.03, 0) / 0.08) * 0.6)


def shaker():
    t = T(0.07)
    return norm(fft_filter(noise(len(t)), hp(6000, 3))) * np.exp(-t / 0.018)


def bass(f, dur):
    t = T(dur + 0.03)
    s = 0.7 * np.sin(2 * np.pi * f * t) + 0.4 * saw(f, t, nh=12, roll=1.2)
    env = np.minimum(1, t / 0.005) * np.exp(-t / 0.35) * np.clip((dur + 0.03 - t) / 0.03, 0, 1)
    return fft_filter(s * env, lambda fr: lp(1100, 2)(fr) * hp(40, 2)(fr))


def pluck(f, dur=0.6):        # « pizzicato » de boîte à musique, léger et sautillant
    t = T(dur)
    s = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.05)
         + 0.2 * np.sin(6 * np.pi * f * t) * np.exp(-t / 0.03))
    return s * np.minimum(1, t / 0.002) * np.exp(-t / 0.16)


def marimba(f, dur=0.5):
    t = T(dur)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.22) + 0.35 * np.sin(2 * np.pi * 3.9 * f * t) * np.exp(-t / 0.04)
    return s * np.minimum(1, t / 0.001)


# ---------------------------------------------------------------- bruitages synthétisés
def crumple(d=0.55):          # papier froissé : craquements de bruit filtré
    out = np.zeros(int(d * SR))
    for _ in range(46):
        t0 = rng.uniform(0, d - 0.03)
        t = T(rng.uniform(0.004, 0.02))
        c = fft_filter(noise(len(t)), bp(rng.uniform(1800, 6500), 1.2)) * np.exp(-t / 0.004)
        i = int(t0 * SR)
        out[i:i + len(c)] += c * rng.uniform(0.3, 1.0)
    return norm(out)


def stamp():
    t = T(0.4)
    return norm(np.tanh(2 * (np.sin(2 * np.pi * np.cumsum(90 + 120 * np.exp(-t / 0.02)) / SR) * np.exp(-t / 0.09)
                             + 0.6 * norm(fft_filter(noise(len(t)), lp(1500))) * np.exp(-t / 0.03))))


def thud(f0=70):
    t = T(0.35)
    s = np.sin(2 * np.pi * np.cumsum(f0 + 90 * np.exp(-t / 0.015)) / SR) * np.exp(-t / 0.08)
    return norm(s + 0.3 * norm(fft_filter(noise(len(t)), lp(900))) * np.exp(-t / 0.02))


def ring():
    out = np.zeros(int(0.9 * SR))
    for k in range(16):
        t = T(0.025)
        f = 1350 if k % 2 else 1700
        s = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.minimum(1, t / 0.002)
        i = int(k * 0.025 * SR) + (int(0.45 * SR) if k >= 8 else 0)
        out[i:i + len(s)] += s
    return fft_filter(out, lp(4000)) * 0.8


def rattle():                 # cadenas qui tremble
    out = np.zeros(int(0.6 * SR))
    for k in range(6):
        t = T(0.04)
        c = fft_filter(noise(len(t)), bp(rng.uniform(2500, 4200), 2.5)) * np.exp(-t / 0.006)
        i = int(k * 0.09 * SR)
        out[i:i + len(c)] += c
    return norm(out)


# ---------------------------------------------------------------- musique : 120 BPM, Do Sol Lam Fa
BEAT, BAR = 0.5, 2.0
CHORDS = {'C': ('C2', ['E4', 'G4', 'C5', 'E5']), 'G': ('G1', ['D4', 'G4', 'B4', 'D5']),
          'Am': ('A1', ['E4', 'A4', 'C5', 'E5']), 'F': ('F1', ['F4', 'A4', 'C5', 'F5'])}
PATTERN = [0, 2, 1, 3, 2, 1, 3, 2]
kick_b, clap_b, shk_b, bass_b, plk_b, mar_b = (Bus() for _ in range(6))
n_bars = int(np.ceil(END / BAR))
for bar in range(n_bars):
    t0 = bar * BAR
    root, notes = CHORDS[['C', 'G', 'Am', 'F'][bar % 4]]
    for k in range(8):
        tk = t0 + k * BEAT / 2
        if tk >= END - 0.05:
            break
        plk_b.add(pluck(hz(notes[PATTERN[k]])), tk, 1.0 if k % 2 == 0 else 0.6, pan=-0.3 if k % 2 else 0.3)
        if k % 2 == 0:
            bass_b.add(bass(hz(root) * (1 if k % 4 == 0 else 2), BEAT - 0.04), tk)
        shk_b.add(shaker(), tk, 1.0 if k % 2 else 0.45, pan=0.25)
    if bar % 2 == 1:          # petite réponse de marimba une mesure sur deux
        for k, nn in enumerate(notes[::-1][:3]):
            mar_b.add(marimba(hz(nn) * 2), t0 + 1.5 + k * 0.125, 0.7, pan=-0.4)
    for k in range(4):
        tk = t0 + k * BEAT
        if tk >= END - 0.05:
            break
        if k in (0, 2):
            kick_b.add(kick(), tk)
        else:
            clap_b.add(clap(), tk)
# accord final sous la carte de fin
for k, nn in enumerate(['C5', 'E5', 'G5', 'C6']):
    plk_b.add(pluck(hz(nn), 1.4), END + k * 0.06, 0.9, pan=(k - 1.5) * 0.3)
bass_b.add(bass(hz('C2'), 1.6), END)
kick_b.add(kick(), END)

kick_b.level(-25)
clap_b.level(-33)
shk_b.level(-36)
bass_b.level(-27)
plk_b.level(-28)
mar_b.level(-32)
music = Bus()
for b in (kick_b, clap_b, shk_b, bass_b, plk_b, mar_b):
    music.mix(b)

# baisse sous les voix (jusqu'à -8 dB), relâchement doux
v, vsr = sf.read(ROOT / 'build' / 'voice.wav')
voice = np.zeros(N)
voice[:min(len(v), N)] = v[:N]
win = int(0.08 * SR)
env = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode='same'))
env = np.convolve(env, np.ones(int(0.3 * SR)) / int(0.3 * SR), mode='same')
music.scale(1 - 0.6 * np.clip(env / (np.max(env) * 0.25), 0, 1))
tt = np.arange(N) / SR
music.scale(np.clip((DUR - tt) / 0.8, 0, 1) ** 1.5 * np.minimum(1, tt / 0.05))

# ---------------------------------------------------------------- bruitages
POP, WH, WHS, KEY, IMP = (load(f) for f in ('pop.mp3', 'whoosh.mp3', 'whoosh-short.mp3', 'key-press.mp3', 'impact-bass-1.mp3'))
fx = Bus()
pops = [pitch(POP, r) for r in (1.0, 1.12, 0.9, 1.25)]
wshort = [WHS, pitch(WHS, 1.1), pitch(WHS, 0.92)]
npop = [0]


def p(t, g=0.5, pan=0.0):
    fx.add(pops[npop[0] % len(pops)], t + 1 / 30, g, pan)
    npop[0] += 1


nwh = [0]


def cut(t, g=0.32):
    fx.add(wshort[nwh[0] % len(wshort)], t - 0.12, g)
    nwh[0] += 1


p(0.17, 0.45)                                      # l'accroche est tamponnée
cut(3.1667)
fx.add(stamp(), 3.75 + 1 / 30, 0.45)               # « Fuis. »
cut(5.5)
fx.add(WH, 5.6667 - 0.25, 0.28)                    # le coffre tombe…
fx.add(thud(60), 5.9167 + 1 / 30, 0.7)             # …et rebondit au bout du fil
fx.add(thud(80), 6.25 + 1 / 30, 0.35)
p(5.5833, 0.4)                                     # carte « Personne n'a l'algo »
for k in range(8):                                 # la molette tourne
    fx.add(KEY, q(W('m2', 'lalgorithme')) + k * 0.175, 0.16, pan=0.1)
fx.add(rattle(), q(W('m2', 'garantir')), 0.35)     # le cadenas tremble
cut(10.1667)
p(10.5, 0.4, -0.2)
p(11.6667, 0.35, -0.3)
cut(12.4167)
p(q(W('m3', 'methode') - 0.08), 0.4)
p(q(W('m3', 'un') - 0.05), 0.45)
p(q(W('m3', 'du') - 0.05), 0.45)
t_type = q(W('m3', 'contenu'))
for k in range(12):                                # la recherche se tape
    fx.add(KEY, t_type + k * 0.1 + rng.uniform(-0.01, 0.01), 0.14 * rng.uniform(0.7, 1), pan=-0.2)
p(q(W('m3', 'et') - 0.05), 0.45)
cut(19.75)
p(q(W('s3', 'quoi')), 0.35, 0.3)
cut(21.5833)
p(q(W('m4', 'trafic') - 0.1), 0.45)
p(q(W('m4', 'plus', 1) - 0.05), 0.45)
fx.add(ring(), q(W('m4', 'dappels')), 0.12, pan=-0.2)   # le téléphone sonne
fx.add(pitch(WHS, 1.3), 24.0 - 0.05, 0.2)          # les cartes sont retirées
fx.add(crumple(), q(W('m4', 'magique') + 0.12) - 0.05, 0.3, pan=-0.3)
fx.add(WH, 25.4167 - 0.15, 0.28)                   # la boule est jetée
fx.add(pitch(WHS, 0.8), q(W('m4', 'promesse', 1) - 0.08) - 0.12, 0.3)
fx.add(thud(55), q(W('m4', 'promesse', 1)) + 0.09 + 1 / 30, 0.75)  # le drapeau se plante
p(26.3333, 0.4)
cut(29.1667)
p(q(W('m5', 'audit') - 0.1), 0.45)
fx.add(stamp(), q(W('m5', 'sans')) + 1 / 30, 0.4)
p(q(W('m5', 'lien') - 0.05), 0.4)
fx.add(WH, END - 0.2, 0.3)                         # la feuille de fin est posée
fx.add(IMP, END + 0.33 + 1 / 30, 0.22)             # le logo arrive
p(END + 0.75, 0.35)

# ---------------------------------------------------------------- export + sonie
K_SHELF = ((1.53512485958697, -2.69169618940638, 1.19839281085285), (1, -1.69065929318241, 0.73248077421585))
K_HP = ((1.0, -2.0, 1.0), (1, -1.99004745483398, 0.99007225036621))


def k_weight(f):
    z = np.exp(-2j * np.pi * f / SR)
    h = 1
    for b, a in (K_SHELF, K_HP):
        h = h * (b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z)
    return np.abs(h)


def loudness(x):
    pw = sum(fft_filter(c, k_weight) ** 2 for c in x)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    cs = np.r_[0, np.cumsum(pw)]
    ms = (cs[blk::hop] - cs[:-blk:hop][:len(cs[blk::hop])]) / blk
    lufs = lambda m: -0.691 + 10 * np.log10(m + 1e-12)
    ms = ms[lufs(ms) > -70]
    return lufs(np.mean(ms[lufs(ms) > lufs(np.mean(ms)) - 10]))


out = ROOT / 'assets' / 'audio'
out.mkdir(parents=True, exist_ok=True)
for name, bus in (('music', music), ('sfx', fx)):
    x = np.stack([bus.L, bus.R])
    pk = np.max(np.abs(x))
    if pk > 0.89:
        x *= 0.89 / pk
    sf.write(out / f'{name}.wav', x.T.astype(np.float32), SR, subtype='PCM_16')
mix = np.stack([music.L + fx.L + voice, music.R + fx.R + voice])
sf.write(ROOT / 'build' / 'mix.wav', np.clip(mix.T, -1, 1).astype(np.float32), SR, subtype='PCM_16')
print(f'mix : {loudness(mix):.1f} LUFS, crête {20 * np.log10(np.max(np.abs(mix))):.1f} dBFS ; '
      f'voix seules {loudness(np.stack([voice, voice])):.1f} LUFS ; musique seule {loudness(np.stack([music.L, music.R])):.1f} LUFS')
