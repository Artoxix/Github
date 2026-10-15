#!/usr/bin/env python3
"""Voix off de la narratrice : synthèse neuronale phrase par phrase + minutage de chaque mot.

Moteur : Kokoro (modèle neuronal libre, voix française « ff_siwis »), piloté en phonétique.
Le texte français est converti en phonèmes, puis les mots étrangers ou de marque sont
remplacés par une transcription phonétique écrite à la main, pour une prononciation
naturelle à la française : {SEO} « esse-eu-o », {GOOGLE} « gougueul », {SMT} « séo-masteur-tèk ».

Chaque phrase a deux textes : `say` (lu par la voix, avec ces marqueurs) et `show`
(le sous-titre affiché). Sorties : build/voice.wav et build/timeline.json.

    python3 voice.py
"""
import json
import os
import re
import subprocess
import urllib.request

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')
MODELS = os.path.join(BUILD, 'models')
MODEL_URL = 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/'
VOICE = 'ff_siwis'
SPEED = 1.08

# transcriptions phonétiques (API) des mots que la conversion automatique prononce mal
IPA = {
    'SEO': 'ˌɛsəˈo',
    'GOOGLE': 'ɡˈuɡəl',
    'SMT': 'seomastœʁtˈɛk',
    'SMTFR': 'seomastœʁtˈɛk pwˌɛ̃ ˈɛf ˈɛʁ',
}

# retouches de la conversion automatique : « pub » à la française, liaisons trop formelles
FIXES = [('pˈœb', 'pˈyb'), ('pʁefˈɛʁz ˈɛtʁ', 'pʁefˈɛʁ ˈɛtʁ'), ('fˈɛt apˈɛl', 'fˈɛ apˈɛl'), ('lˈə ˌɛsəˈo', 'lə ˌɛsəˈo')]

# (id, texte lu, sous-titre, silence après en secondes)
SCRIPT = [
    ('hook', "Ces deux garages sont dans la même rue.", "Ces deux garages sont dans la même rue.", 0.15),
    ('hook2', "Pourtant, l'un a trois fois plus de clients que l'autre.", "Pourtant, l'un a 3 fois plus de clients que l'autre.", 0.3),
    ('same', "Même travail. Même qualité. Mêmes prix.", "Même travail. Même qualité. Mêmes prix.", 0.2),
    ('why', "Alors… c'est quoi, la différence ?", "Alors… c'est quoi la différence ?", 0.35),
    ('seo', "La réponse tient en trois lettres : {SEO}.", "La réponse tient en 3 lettres : SEO.", 0.45),
    ('panne', "Ta voiture tombe en panne. Tu sors ton téléphone, et tu tapes : garage près de moi.",
     "Ta voiture tombe en panne. Tu sors ton téléphone et tu tapes : « garage près de moi ».", 0.25),
    ('list', "Sur {GOOGLE}, le garage Léon ? Premier résultat.", "Sur Google, le garage Léon ? Premier résultat.", 0.2),
    ('marcel', "Le garage Marcel ? Page trois. Autant dire… invisible.", "Le garage Marcel ? Page 3. Autant dire… invisible.", 0.45),
    ('def', "Le {SEO}, ou référencement naturel, c'est l'art de convaincre {GOOGLE} que ton site est la meilleure réponse.",
     "Le SEO, ou référencement naturel, c'est l'art de convaincre Google que ton site est la meilleure réponse.", 0.25),
    ('three', "Pour ça, {GOOGLE} regarde trois choses.", "Pour ça, Google regarde 3 choses.", 0.25),
    ('c1', "Un : ce que dit ton site. Tes services, ta ville, les bons mots-clés.", "1 : ce que dit ton site. Tes services, ta ville, les bons mots-clés.", 0.2),
    ('c2', "Deux : la technique. Un site rapide, et parfait sur mobile.", "2 : la technique. Un site rapide et parfait sur mobile.", 0.2),
    ('c3', "Trois : la confiance. Tes avis clients, et ta fiche {GOOGLE}.", "3 : la confiance. Tes avis clients et ta fiche Google.", 0.35),
    ('result', "Résultat : plus de visibilité, plus d'appels, plus de rendez-vous.", "Résultat : plus de visibilité, plus d'appels, plus de rendez-vous.", 0.25),
    ('free', "Et contrairement à la pub, tu ne paies pas chaque clic.", "Et contrairement à la pub, tu ne paies pas chaque clic.", 0.4),
    ('reveal', "Le garage Léon, lui, a fait appel à {SMT}.", "Le garage Léon, lui, a fait appel à Seomastertech.", 0.2),
    ('services', "Site, référencement, {SEO} local : on s'occupe de tout.", "Site, référencement, SEO local : on s'occupe de tout.", 0.35),
    ('cta', "Et toi, tu préfères être le garage Léon… ou le garage Marcel ?", "Et toi, tu préfères être le garage Léon… ou le garage Marcel ?", 0.3),
    ('cta2', "Dis-le en commentaire. Et rendez-vous sur {SMTFR}.", "Dis-le en commentaire. Et rendez-vous sur seomastertech.fr", 0.0),
]
LEAD_IN = 0.25   # la voix démarre presque tout de suite : l'accroche doit tomber dans la 1re seconde
TAIL = 1.6       # fin musicale après la dernière phrase


def ensure_model():
    os.makedirs(MODELS, exist_ok=True)
    paths = []
    for name in ('kokoro-v1.0.onnx', 'voices-v1.0.bin'):
        path = os.path.join(MODELS, name)
        if not os.path.exists(path):
            urllib.request.urlretrieve(MODEL_URL + name, path)
        paths.append(path)
    return Kokoro(*paths)


def to_phonemes(kokoro, text):
    """Texte français -> phonèmes, avec les marqueurs {XXX} remplacés par leur transcription."""
    out = []
    for piece in re.split(r'(\{[A-Z]+\})', text):
        m = re.fullmatch(r'\{([A-Z]+)\}', piece)
        if m:
            out.append(IPA[m.group(1)])
        elif piece.strip() and not piece.strip(' .,?!:;…'):
            out.append(piece.strip())                     # ponctuation seule : gardée telle quelle
        elif piece.strip():
            out.append(kokoro.tokenizer.phonemize(piece, 'fr-fr'))
    s = re.sub(r'\s+([,.?!:;…])', r'\1', ' '.join(out))
    s = re.sub(r'([,.?!:;…])\1+', r'\1', s)
    for a, b in FIXES:
        s = s.replace(a, b)
    return s


def trim(x, sr, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a, b = max(idx[0] - int(0.02 * sr), 0), min(idx[-1] + int(0.08 * sr), len(x))
    return x[a:b]


def word_times(show, t0, t1):
    """Répartit la durée de la phrase sur les mots affichés, au prorata de leur longueur
    (+ une petite pause après la ponctuation)."""
    words = show.split()
    w = []
    for s in words:
        core = sum(ch.isalnum() for ch in s)
        w.append(max(core, 1) + 1.5 + (4 if s[-1] in '.?!…:' else 2 if s[-1] in ',;' else 0))
    total = sum(w)
    out, t = [], t0
    for s, k in zip(words, w):
        d = (t1 - t0) * k / total
        out.append({'w': s, 'a': round(t, 3), 'b': round(t + d, 3)})
        t += d
    return out


def main():
    os.makedirs(BUILD, exist_ok=True)
    kokoro = ensure_model()
    sr = None
    chunks, timeline, t = [], [], LEAD_IN
    for sid, say, show, gap in SCRIPT:
        ph = to_phonemes(kokoro, say)
        x, sr = kokoro.create(ph, voice=VOICE, speed=SPEED, is_phonemes=True)
        x = trim(np.asarray(x, dtype=np.float64), sr)
        d = len(x) / sr
        timeline.append({'id': sid, 'a': round(t, 3), 'b': round(t + d, 3), 'show': show, 'phonemes': ph,
                         'words': word_times(show, t, t + d)})
        chunks += [x, np.zeros(int(gap * sr))]
        t += d + gap
    chunks = [np.zeros(int(LEAD_IN * sr))] + chunks + [np.zeros(int(TAIL * sr))]
    raw_path = os.path.join(BUILD, 'voice_raw.wav')
    sf.write(raw_path, np.concatenate(chunks).astype(np.float32), sr)
    # traitement « studio » sec : nettoyage du bas, présence, un peu d'air, compression douce
    fx = ('highpass=f=75,equalizer=f=260:t=q:w=1:g=-1.5,equalizer=f=3400:t=q:w=1.2:g=2,'
          'equalizer=f=9500:t=q:w=1:g=1.5,acompressor=threshold=-20dB:ratio=2.5:attack=5:release=110:makeup=2')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', raw_path, '-af', fx,
                    '-ar', '48000', os.path.join(BUILD, 'voice.wav')], check=True)
    duration = round(t + TAIL, 3)
    json.dump({'duration': duration, 'segments': timeline}, open(os.path.join(BUILD, 'timeline.json'), 'w'),
              ensure_ascii=False, indent=1)
    print(f'voix : {duration:.2f} s, {len(timeline)} phrases')
    for s in timeline:
        print(f"  {s['id']:9s} {s['a']:6.2f} -> {s['b']:6.2f}   {s['phonemes']}")


if __name__ == '__main__':
    main()
