#!/usr/bin/env python3
"""Découpe les deux prises ElevenLabs (Max, Sam) en répliques, les place dans le film
et calcule le minutage de chaque mot (sous-titres) et l'ouverture de la bouche (lip-sync).

    python3 voice/prepare.py

Entrées : voice/max_raw.mp3, voice/sam_raw.mp3 (une prise par personnage, répliques
séparées par des pauses). Sorties :
  assets/voice/<id>.wav   une réplique par fichier, placée telle quelle dans index.html
  assets/timing.js        window.TIMING : répliques, mots, bouches (12 i/s), repères
  build/voice.wav         toutes les voix à leur place (pour le ducking de la musique)

Le minutage des mots est réparti par syllabes à l'intérieur de chaque morceau de phrase
délimité par une vraie pause de la prise (détectée avec ffmpeg silencedetect).
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
FPS = 12          # cadence « stop motion » de la bouche

# (id, perso, morceaux : (texte dit, début, fin) en secondes dans la prise brute)
# `show` remplace un mot dit par son écriture à l'écran (1 pour 1).
LINES = [
    ('s1', 'sam', [("L'agence m'a promis la première place sur Google !", 0.00, 2.794)]),
    ('m1', 'max', [("Alors fuis.", 0.00, 0.907), ("Je t'explique pourquoi.", 1.192, 2.164)]),
    ('m2', 'max', [("Personne ne possède l'algorithme de Google.", 3.177, 5.259),
                   ("Personne ne peut garantir une position.", 5.716, 7.534)]),
    ('s2', 'sam', [("Alors…", 3.419, 4.019), ("je paie pour quoi ?", 4.251, 5.344)]),
    ('m3', 'max', [("Pour une méthode :", 8.269, 8.952),
                   ("un site techniquement propre,", 9.160, 10.678),
                   ("du contenu qui répond à ce que les gens tapent,", 10.785, 12.748),
                   ("et de la confiance :", 12.914, 13.730),
                   ("tes avis,", 13.984, 14.533),
                   ("ta fiche Google.", 14.678, 15.354)]),
    ('s3', 'sam', [("Et ça me donne quoi,", 6.002, 6.958), ("concrètement ?", 7.069, 7.552)]),
    ('m4', 'max', [("Plus de trafic qualifié,", 15.868, 17.138),
                   ("plus d'appels.", 17.308, 17.929),
                   ("Pas une promesse magique de numéro un.", 18.282, 19.825),
                   ("Une promesse trop belle, c'est le premier signe d'une agence à éviter.", 20.131, 23.080)]),
    ('m5', 'max', [("On fait un audit gratuit de ton site, sans promesse bidon.", 23.477, 26.010),
                   ("Lien en bio !", 26.146, 26.740)]),
]
SHOW = {'première': '1ère', 'un.': '1.'}
FIRST = 0.30      # la 1re réplique démarre ici (la 1re image montre déjà l'accroche)
GAP = {'s1': 0.22, 'm1': 0.30, 'm2': 0.32, 's2': 0.26, 'm3': 0.32, 's3': 0.26, 'm4': 0.36}
END_HOLD = 0.45   # après la dernière réplique, avant la carte de fin
END_CARD = 3.2    # durée de la carte de fin (la dernière ligne reste 2 s et plus)
PAD_IN, PAD_OUT = 0.04, 0.10
VOICE_DB = -17    # niveau RMS de la parole (dBFS) ; le mixage final vise -14 LUFS


def load(name):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(ROOT / 'voice' / name), '-ac', '1',
                          '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, '<f4').astype(np.float64)


def onset(x, t0, t1, th_db=-38):
    """Premier instant après t0 où le niveau dépasse le seuil (affine les débuts de fichier)."""
    a, b = int(t0 * SR), int(t1 * SR)
    win = int(0.01 * SR)
    seg = x[a:b]
    rms = np.sqrt(np.convolve(seg ** 2, np.ones(win) / win, mode='same'))
    idx = np.nonzero(20 * np.log10(rms + 1e-9) > th_db)[0]
    return t0 + (idx[0] / SR if len(idx) else 0.0)


def syllables(word):
    w = re.sub(r"[^a-zàâäéèêëîïôöùûüÿœæç]", '', word.lower())
    n = len(re.findall(r"[aeiouyàâäéèêëîïôöùûüÿœæ]+", w))
    if w.endswith('es') or (w.endswith('e') and n > 1):
        n -= 0.6           # e muet final
    return max(n, 0.6)


raw = {'max': load('max_raw.mp3'), 'sam': load('sam_raw.mp3')}
out_dir = ROOT / 'assets' / 'voice'
out_dir.mkdir(parents=True, exist_ok=True)
(ROOT / 'build').mkdir(exist_ok=True)

t = FIRST
lines = []
for lid, who, chunks in LINES:
    x = raw[who]
    c0 = onset(x, chunks[0][1], chunks[0][2]) if chunks[0][1] == 0 else chunks[0][1]
    c1 = chunks[-1][2]
    shift = t - c0                       # temps du film = temps de la prise + shift
    words = []
    for k, (text, a, b) in enumerate(chunks):
        a = c0 if k == 0 else a
        toks = []
        for w in text.split():           # « Google ! » : la ponctuation reste collée au mot
            if toks and not re.search(r'\w', w):
                toks[-1] += ' ' + w
            else:
                toks.append(w)
        wts = np.array([syllables(w) for w in toks])
        edges = a + (b - a) * np.r_[0, np.cumsum(wts)] / wts.sum()
        for w, s, e in zip(toks, edges[:-1], edges[1:]):
            words.append({'text': SHOW.get(w, w), 'start': round(s + shift, 3), 'end': round(e + shift, 3)})
    clip_a, clip_b = c0 - PAD_IN, c1 + PAD_OUT
    seg = x[int(clip_a * SR):int(clip_b * SR)].copy()
    act = seg[np.abs(seg) > 0.02 * np.max(np.abs(seg))]   # même niveau de parole pour chaque réplique
    seg *= min(10 ** (VOICE_DB / 20) / np.sqrt(np.mean(act ** 2)), 0.89 / np.max(np.abs(seg)))
    f = int(0.008 * SR)
    seg[:f] *= np.linspace(0, 1, f)
    seg[-f:] *= np.linspace(1, 0, f)
    sf.write(out_dir / f'{lid}.wav', seg.astype(np.float32), SR, subtype='PCM_16')
    lines.append({'id': lid, 'speaker': who, 'start': round(t, 3), 'end': round(c1 + shift, 3),
                  'clip': f'assets/voice/{lid}.wav', 'clipStart': round(clip_a + shift, 3),
                  'clipDur': round(len(seg) / SR, 3), 'words': words})
    t = c1 + shift + GAP.get(lid, 0)

end_card = round(lines[-1]['end'] + END_HOLD, 3)
duration = round(end_card + END_CARD, 2)

# toutes les voix à leur place + enveloppe de bouche par personnage
N = int(duration * SR) + SR
mix = np.zeros(N)
per = {'max': np.zeros(N), 'sam': np.zeros(N)}
for ln in lines:
    seg, _ = sf.read(ROOT / ln['clip'])
    i0 = int(round(ln['clipStart'] * SR))
    mix[i0:i0 + len(seg)] += seg
    per[ln['speaker']][i0:i0 + len(seg)] += seg
sf.write(ROOT / 'build' / 'voice.wav', mix[:int(duration * SR)].astype(np.float32), SR, subtype='PCM_16')

mouth = {}
nfr = int(np.ceil(duration * FPS))
for who, sig in per.items():
    hop = SR // FPS
    rms = np.array([np.sqrt(np.mean(sig[i * hop:(i + 1) * hop] ** 2)) for i in range(nfr)])
    ref = np.percentile(rms[rms > 0.01], 85) if np.any(rms > 0.01) else 1
    lv = rms / ref
    states = np.where(lv < 0.10, 0, np.where(lv < 0.38, 1, np.where(lv < 0.75, 2, 3)))
    mouth[who] = ''.join(map(str, states))

timing = {'fps': FPS, 'duration': duration, 'endCard': end_card, 'lines': lines, 'mouth': mouth}
(ROOT / 'assets' / 'timing.js').write_text(
    '// Généré par voice/prepare.py : ne pas modifier à la main.\n'
    'window.TIMING = ' + json.dumps(timing, ensure_ascii=False) + ';\n', encoding='utf-8')
json.dump(timing, open(ROOT / 'build' / 'timing.json', 'w'), ensure_ascii=False, indent=1)
for ln in lines:
    print(f"{ln['id']} {ln['speaker']:3} {ln['start']:6.2f} → {ln['end']:6.2f}  " +
          ' '.join(w['text'] for w in ln['words']))
print('carte de fin', end_card, '· durée', duration)
