#!/usr/bin/env python3
"""Voix off du narrateur : prise ElevenLabs découpée phrase par phrase + minutage de chaque mot.

La voix a été générée sur ElevenLabs (voix « Diano V », modèle Eleven v4, langue fr), d'un seul
tenant pour garder un phrasé naturel, à partir du texte que donne `python3 voice.py --texte`.
La prise (voice/voix_off.mp3) et le minutage de ses mots transcrits par ElevenLabs Scribe
(voice/mots.json) sont versionnés : ce script n'a besoin ni de réseau ni de compte ElevenLabs.

Chaque phrase a deux textes : `say` (le texte envoyé à ElevenLabs, avec ses balises de ton entre
crochets ; « SEO » y est écrit en alphabet phonétique, /ɛsiˈo/, pour être dit à l'anglaise) et
`show` (le sous-titre affiché). Le script recale les mots transcrits sur le texte, coupe la prise
entre les phrases, règle les silences (dernière colonne du SCRIPT) et minute chaque mot affiché.
Sorties : build/voice.wav et build/timeline.json, utilisés ensuite par l'animation et le mixage.

    python3 voice.py            # build/voice.wav + build/timeline.json
    python3 voice.py --texte    # texte à coller dans ElevenLabs pour régénérer la prise
"""
import difflib
import json
import os
import re
import subprocess
import sys
import unicodedata

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')
TAKE = os.path.join(HERE, 'voice', 'voix_off.mp3')
WORDS = os.path.join(HERE, 'voice', 'mots.json')
SR = 48000
TEMPO = 1.1      # la prise est accélérée de 10 % (hauteur conservée) pour tenir la minute, rythme des réseaux
LAG = 0.08       # le minutage de Scribe arrive en moyenne 80 ms après le début réel des mots

SEO = '/ɛsiˈo/'
# (id, texte lu, sous-titre, silence après en secondes)
SCRIPT = [
    ('hook', "[confident] Ces deux garages sont dans la même rue.", "Ces deux garages sont dans la même rue.", 0.15),
    ('hook2', "Pourtant, l'un a trois fois plus de clients que l'autre.", "Pourtant, l'un a 3 fois plus de clients que l'autre.", 0.3),
    ('same', "Même travail. Même qualité. Mêmes prix.", "Même travail. Même qualité. Mêmes prix.", 0.2),
    ('why', "[curious] Alors… c'est quoi, la différence ?", "Alors… c'est quoi la différence ?", 0.35),
    ('seo', f"[confident] La réponse tient en trois lettres : {SEO}.", "La réponse tient en 3 lettres : SEO.", 0.45),
    ('panne', "Ta voiture tombe en panne. Tu sors ton téléphone, et tu tapes : « garage près de moi ».",
     "Ta voiture tombe en panne. Tu sors ton téléphone et tu tapes : « garage près de moi ».", 0.25),
    ('list', "Sur Google, le garage Léon ? Premier résultat.", "Sur Google, le garage Léon ? Premier résultat.", 0.2),
    ('marcel', "Le garage Marcel ? Page trois. Autant dire… invisible.", "Le garage Marcel ? Page 3. Autant dire… invisible.", 0.45),
    ('def', f"Le {SEO}, ou référencement naturel, c'est l'art de convaincre Google que ton site est la meilleure réponse.",
     "Le SEO, ou référencement naturel, c'est l'art de convaincre Google que ton site est la meilleure réponse.", 0.25),
    ('three', "Pour ça, Google regarde trois choses.", "Pour ça, Google regarde 3 choses.", 0.25),
    ('c1', "Un : ce que dit ton site. Tes services, ta ville, les bons mots-clés.", "1 : ce que dit ton site. Tes services, ta ville, les bons mots-clés.", 0.2),
    ('c2', "Deux : la technique. Un site rapide, et parfait sur mobile.", "2 : la technique. Un site rapide et parfait sur mobile.", 0.2),
    ('c3', "Trois : la confiance. Tes avis clients, et ta fiche Google.", "3 : la confiance. Tes avis clients et ta fiche Google.", 0.35),
    ('result', "Résultat : plus de visibilité, plus d'appels, plus de rendez-vous.", "Résultat : plus de visibilité, plus d'appels, plus de rendez-vous.", 0.25),
    ('free', "Et contrairement à la pub, tu ne paies pas chaque clic.", "Et contrairement à la pub, tu ne paies pas chaque clic.", 0.4),
    ('reveal', "[excited] Le garage Léon, lui, a fait appel à Séo Master Tech.", "Le garage Léon, lui, a fait appel à Seomastertech.", 0.2),
    ('services', f"Site, référencement, {SEO} local : on s'occupe de tout.", "Site, référencement, SEO local : on s'occupe de tout.", 0.35),
    ('cta', "Et toi, tu préfères être le garage Léon… ou le garage Marcel ?", "Et toi, tu préfères être le garage Léon… ou le garage Marcel ?", 0.3),
    ('cta2', "Dis-le en commentaire. Et rendez-vous sur Séo Master Tech point F R.", "Dis-le en commentaire. Et rendez-vous sur seomastertech.fr", 0.0),
]
LEAD_IN = 0.25   # la voix démarre presque tout de suite : l'accroche doit tomber dans la 1re seconde
TAIL = 1.6       # fin musicale après la dernière phrase


def prompt_text():
    return '\n\n'.join(say for _, say, _, _ in SCRIPT)


def units(word):
    """Morceaux comparables d'un mot : minuscules, sans accents ni ponctuation,
    coupés aux apostrophes, traits d'union et points (« l'autre » -> l, autre)."""
    s = unicodedata.normalize('NFD', word.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return [p for p in re.split(r"[^0-9a-zɛ]+", s) if p]


def spoken_words(say):
    return re.sub(r'\[[^\]]*\]', ' ', say).split()


def flatten(words):
    """Mots -> morceaux comparables + indice du mot d'origine de chaque morceau."""
    out, owner = [], []
    for i, w in enumerate(words):
        for u in units(w):
            out.append(u)
            owner.append(i)
    return out, owner


def align(src, dst):
    """Associe chaque élément de src à une plage [i, j) de dst : égalités d'abord,
    puis les trous entre deux égalités se répartissent dans l'ordre."""
    m = difflib.SequenceMatcher(None, src, dst, autojunk=False)
    span = [None] * len(src)
    for op, a0, a1, b0, b1 in m.get_opcodes():
        if op == 'equal':
            for k in range(a1 - a0):
                span[a0 + k] = (b0 + k, b0 + k + 1)
        elif op in ('replace', 'delete'):
            n = a1 - a0
            for k in range(n):
                lo = b0 + (b1 - b0) * k // n
                hi = b0 + (b1 - b0) * (k + 1) // n
                span[a0 + k] = (lo, max(hi, lo)) if b1 > b0 else (b0, b0)
    return span


def load_take():
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', TAKE, '-af', f'atempo={TEMPO}', '-ac', '1', '-ar', str(SR),
                          '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def word_clock():
    """Début/fin (dans la prise) de chaque mot lu du SCRIPT, d'après la transcription."""
    heard = [dict(w, start=max(w['start'] - LAG, 0) / TEMPO, end=max(w['end'] - LAG, 0) / TEMPO)
             for w in json.load(open(WORDS)) if w.get('type', 'word') == 'word']
    hu, howner = flatten([w['text'] for w in heard])
    # un mot transcrit coupé en plusieurs morceaux se partage sa durée au prorata des lettres
    ht = []
    for i, w in enumerate(heard):
        parts = [u for u, o in zip(hu, howner) if o == i]
        tot = sum(len(p) for p in parts) or 1
        t = w['start']
        for p in parts:
            d = (w['end'] - w['start']) * len(p) / tot
            ht.append((t, t + d))
            t += d
    said = [spoken_words(say) for _, say, _, _ in SCRIPT]
    flat = [w for ws in said for w in ws]
    su, sowner = flatten(flat)
    span = align(su, hu)
    t_unit = []
    for k, (i, j) in enumerate(span):
        t_unit.append((ht[i][0], ht[j - 1][1]) if j > i else None)
    # morceaux sans équivalent entendu : bornés par leurs voisins
    for k, v in enumerate(t_unit):
        if v is None:
            prev = next((t_unit[q][1] for q in range(k - 1, -1, -1) if t_unit[q]), 0.0)
            nxt = next((t_unit[q][0] for q in range(k + 1, len(t_unit)) if t_unit[q]), prev)
            t_unit[k] = (prev, max(prev, nxt))
    clock = [[None, None] for _ in flat]
    for (a, b), o in zip(t_unit, sowner):
        clock[o][0] = a if clock[o][0] is None else min(clock[o][0], a)
        clock[o][1] = b if clock[o][1] is None else max(clock[o][1], b)
    for k, c in enumerate(clock):    # ponctuation isolée (« ? », « : ») : collée au mot d'avant
        if c[0] is None:
            c[0] = c[1] = clock[k - 1][1] if k else next(d[0] for d in clock if d[0] is not None)
    out, k = [], 0
    for ws in said:
        out.append(clock[k:k + len(ws)])
        k += len(ws)
    return said, out


def show_times(show, said, clock):
    """Minutage des mots affichés à partir des mots lus de la même phrase."""
    sw = show.split()
    su, sowner = flatten(sw)
    lu, lowner = flatten(said)
    span = align(su, lu)
    res = [[None, None] for _ in sw]
    for (i, j), o in zip(span, sowner):
        if j <= i:
            continue
        a = min(clock[lowner[q]][0] for q in range(i, j))
        b = max(clock[lowner[q]][1] for q in range(i, j))
        res[o][0] = a if res[o][0] is None else min(res[o][0], a)
        res[o][1] = b if res[o][1] is None else max(res[o][1], b)
    for k, v in enumerate(res):      # mot affiché sans équivalent lu : entre ses voisins
        if v[0] is None:
            prev = next((res[q][1] for q in range(k - 1, -1, -1) if res[q][1] is not None), clock[0][0])
            v[0] = v[1] = prev
    return sw, res


def envelope(x, win=0.01):
    n = int(win * SR)
    e = np.sqrt(np.convolve(x * x, np.ones(n) / n, mode='same'))
    return 20 * np.log10(e + 1e-9)


def silences(env, thr, min_len):
    """Plages (début, fin) en secondes où la prise est silencieuse."""
    quiet = np.r_[0, (env < thr).astype(int), 0]
    edges = np.flatnonzero(np.diff(quiet))
    return [(a / SR, b / SR) for a, b in zip(edges[::2], edges[1::2]) if (b - a) / SR >= min_len]


def snap_to_pauses(clock, pauses):
    """Après une vraie pause, un mot commence là où la voix repart (et le mot d'avant
    finit là où elle s'arrête) : l'alignement automatique y est souvent en retard."""
    flat = [c for seg in clock for c in seg]
    for i, c in enumerate(flat):
        ends = [(p0, p1) for p0, p1 in pauses if c[0] - 0.35 <= p1 <= c[0] + 0.06]
        if not ends:
            continue
        p0, p1 = max(ends, key=lambda p: p[1])
        if i and flat[i - 1][0] >= p0:
            continue
        c[0] = p1
        c[1] = max(c[1], p1)
        if i and flat[i - 1][1] > p0:
            flat[i - 1][1] = p0


def main():
    if '--texte' in sys.argv:
        print(prompt_text())
        return
    os.makedirs(BUILD, exist_ok=True)
    x = load_take()
    env = envelope(x)
    thr = np.percentile(env, 99) - 42
    said, clock = word_clock()
    snap_to_pauses(clock, silences(env, thr, 0.1))
    seg_ab = [(c[0][0], c[-1][1]) for c in clock]
    # coupe au milieu de la pause qui sépare deux phrases, puis resserre sur la voix
    pauses = silences(env, thr, 0.03)
    cuts = [0.0]
    for (a0, b0), (a1, b1) in zip(seg_ab, seg_ab[1:]):
        lo, hi = min(b0, a1) - 0.35, max(b0, a1) + 0.15
        cand = [(min(p1, hi) - max(p0, lo), (max(p0, lo) + min(p1, hi)) / 2) for p0, p1 in pauses if p1 > lo and p0 < hi]
        if cand:
            cuts.append(max(cand)[1])
        else:
            i0, i1 = int(min(b0, a1) * SR), int(max(b0, a1) * SR) + 1
            cuts.append((i0 + int(np.argmin(env[i0:i1]))) / SR)
    cuts.append(len(x) / SR)
    fade = int(0.008 * SR)
    chunks, timeline, t = [np.zeros(int(LEAD_IN * SR))], [], LEAD_IN
    for k, (sid, say, show, gap) in enumerate(SCRIPT):
        lo, hi = int(cuts[k] * SR), int(cuts[k + 1] * SR)
        loud = np.where(env[lo:hi] > thr)[0]
        s0 = lo + max(loud[0] - int(0.04 * SR), 0) if len(loud) else lo
        s1 = lo + min(loud[-1] + int(0.08 * SR), hi - lo) if len(loud) else hi
        seg = x[s0:s1].copy()
        seg[:fade] *= np.linspace(0, 1, fade)
        seg[-fade:] *= np.linspace(1, 0, fade)
        shift = t - s0 / SR
        d = len(seg) / SR
        sw, st = show_times(show, said[k], clock[k])
        words = []
        for i, (w, (a, b)) in enumerate(zip(sw, st)):
            a = min(max(a + shift, t), t + d)
            nxt = st[i + 1][0] + shift if i + 1 < len(sw) else b + shift
            words.append({'w': w, 'a': round(a, 3), 'b': round(min(max(nxt, a), t + d), 3)})
        timeline.append({'id': sid, 'a': words[0]['a'], 'b': round(min(seg_ab[k][1] + shift, t + d), 3),
                         'show': show, 'words': words})
        chunks += [seg, np.zeros(int(gap * SR))]
        t += d + gap
    chunks.append(np.zeros(int(TAIL * SR)))
    raw = np.concatenate(chunks)
    raw_path = os.path.join(BUILD, 'voice_raw.wav')
    sf.write(raw_path, raw.astype(np.float32), SR)
    # la prise ElevenLabs est déjà propre : on retire juste le grave inutile et on tient le niveau
    fx = 'highpass=f=70,acompressor=threshold=-22dB:ratio=2:attack=10:release=160:makeup=1.5'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', raw_path, '-af', fx, '-ar', str(SR),
                    os.path.join(BUILD, 'voice.wav')], check=True)
    duration = round(t + TAIL, 3)   # t inclut déjà le dernier silence
    json.dump({'duration': duration, 'segments': timeline}, open(os.path.join(BUILD, 'timeline.json'), 'w'),
              ensure_ascii=False, indent=1)
    print(f'voix : {duration:.2f} s, {len(timeline)} phrases')
    for s in timeline:
        print(f"  {s['id']:9s} {s['a']:6.2f} -> {s['b']:6.2f}")


if __name__ == '__main__':
    main()
