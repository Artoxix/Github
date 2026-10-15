#!/usr/bin/env python3
"""Voix off du narrateur : synthèse phrase par phrase + minutage de chaque mot.

Chaque phrase a deux textes : `say` (ce que lit la voix de synthèse, avec une
orthographe phonétique quand il le faut) et `show` (le sous-titre affiché).
Sorties : build/voice.wav et build/timeline.json (début/fin de chaque phrase et
de chaque mot affiché), utilisés ensuite par l'animation et le mixage.

    python3 voice.py
"""
import json
import os
import subprocess
import tarfile
import urllib.request

import numpy as np
import sherpa_onnx
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, 'build')
MODELS = os.path.join(BUILD, 'models')
VOICE = 'vits-piper-fr_FR-tom-medium'
SR = 48000
SPEED = 1.15

# (id, texte lu, sous-titre, silence après en secondes)
SCRIPT = [
    ('hook', "Ces deux garages sont dans la même rue.", "Ces deux garages sont dans la même rue.", 0.15),
    ('hook2', "Pourtant, l'un a trois fois plus de clients que l'autre.", "Pourtant, l'un a 3 fois plus de clients que l'autre.", 0.3),
    ('same', "Même travail. Même qualité. Mêmes prix.", "Même travail. Même qualité. Mêmes prix.", 0.2),
    ('why', "Alors, c'est quoi, la différence ?", "Alors… c'est quoi la différence ?", 0.35),
    ('seo', "La réponse tient en trois lettres : S.E.O.", "La réponse tient en 3 lettres : SEO.", 0.45),
    ('panne', "Ta voiture tombe en panne. Tu sors ton téléphone, et tu tapes : garage près de moi.",
     "Ta voiture tombe en panne. Tu sors ton téléphone et tu tapes : « garage près de moi ».", 0.25),
    ('list', "Sur Gougle, le garage Léon ? Premier résultat.", "Sur Google, le garage Léon ? Premier résultat.", 0.2),
    ('marcel', "Le garage Marcel ? Page trois. Autant dire, invisible.", "Le garage Marcel ? Page 3. Autant dire… invisible.", 0.45),
    ('def', "Le S.E.O., ou référencement naturel, c'est l'art de convaincre Gougle que ton site est la meilleure réponse.",
     "Le SEO, ou référencement naturel, c'est l'art de convaincre Google que ton site est la meilleure réponse.", 0.25),
    ('three', "Pour ça, Gougle regarde trois choses.", "Pour ça, Google regarde 3 choses.", 0.25),
    ('c1', "Un : ce que dit ton site. Tes services, ta ville, les bons mots-clés.", "1 : ce que dit ton site. Tes services, ta ville, les bons mots-clés.", 0.2),
    ('c2', "Deux : la technique. Un site rapide, et parfait sur mobile.", "2 : la technique. Un site rapide et parfait sur mobile.", 0.2),
    ('c3', "Trois : la confiance. Tes avis clients, et ta fiche Gougle.", "3 : la confiance. Tes avis clients et ta fiche Google.", 0.35),
    ('result', "Résultat : plus de visibilité, plus d'appels, plus de rendez-vous.", "Résultat : plus de visibilité, plus d'appels, plus de rendez-vous.", 0.25),
    ('free', "Et contrairement à la pub, tu ne paies pas chaque clic.", "Et contrairement à la pub, tu ne paies pas chaque clic.", 0.4),
    ('reveal', "Le garage Léon, lui, a fait appel à Séo Master Tek.", "Le garage Léon, lui, a fait appel à Seomastertech.", 0.2),
    ('services', "Site, référencement, S.E.O. local : ils s'occupent de tout.", "Site, référencement, SEO local : ils s'occupent de tout.", 0.35),
    ('cta', "Et toi, tu préfères être le garage Léon, ou le garage Marcel ?", "Et toi, tu préfères être le garage Léon… ou le garage Marcel ?", 0.3),
    ('cta2', "Dis-le en commentaire. Et rendez-vous sur Séo Master Tek point F R.", "Dis-le en commentaire. Et rendez-vous sur seomastertech.fr", 0.0),
]
LEAD_IN = 0.25   # la voix démarre presque tout de suite : l'accroche doit tomber dans la 1re seconde
TAIL = 1.6       # fin musicale après la dernière phrase


def ensure_model():
    d = os.path.join(MODELS, VOICE)
    if not os.path.isdir(d):
        os.makedirs(MODELS, exist_ok=True)
        url = f'https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/{VOICE}.tar.bz2'
        tmp = os.path.join(MODELS, 'voice.tar.bz2')
        urllib.request.urlretrieve(url, tmp)
        with tarfile.open(tmp) as t:
            t.extractall(MODELS)
        os.remove(tmp)
    return d


def tts_engine(d):
    name = VOICE.replace('vits-piper-', '')
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=f'{d}/{name}.onnx', tokens=f'{d}/tokens.txt',
                                                   data_dir=f'{d}/espeak-ng-data', noise_scale=0.72, noise_scale_w=0.85),
        num_threads=4))
    return sherpa_onnx.OfflineTts(cfg)


def resample(x, sr_in):
    n = int(len(x) * SR / sr_in)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a, b = max(idx[0] - int(0.02 * SR), 0), min(idx[-1] + int(0.06 * SR), len(x))
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
    tts = tts_engine(ensure_model())
    chunks, timeline, t = [np.zeros(int(LEAD_IN * SR))], [], LEAD_IN
    for sid, say, show, gap in SCRIPT:
        a = tts.generate(say, sid=0, speed=SPEED)
        x = trim(resample(np.asarray(a.samples, dtype=np.float64), a.sample_rate))
        d = len(x) / SR
        timeline.append({'id': sid, 'a': round(t, 3), 'b': round(t + d, 3), 'show': show, 'words': word_times(show, t, t + d)})
        chunks += [x, np.zeros(int(gap * SR))]
        t += d + gap
    chunks.append(np.zeros(int(TAIL * SR)))
    raw = np.concatenate(chunks)
    raw_path = os.path.join(BUILD, 'voice_raw.wav')
    sf.write(raw_path, raw.astype(np.float32), SR)
    # traitement « voix radio » : chaleur, présence, compression douce, petite acoustique de pièce
    fx = ('highpass=f=75,equalizer=f=170:t=q:w=1:g=2.5,equalizer=f=3000:t=q:w=1.2:g=2.5,'
          'equalizer=f=7200:t=q:w=1:g=-2,acompressor=threshold=-21dB:ratio=3:attack=6:release=120:makeup=2,'
          'aecho=1.0:0.9:31|53:0.08|0.05')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', raw_path, '-af', fx, '-ar', str(SR),
                    os.path.join(BUILD, 'voice.wav')], check=True)
    duration = round(t - 0.0 + TAIL, 3)   # t inclut déjà le dernier silence
    json.dump({'duration': duration, 'segments': timeline}, open(os.path.join(BUILD, 'timeline.json'), 'w'),
              ensure_ascii=False, indent=1)
    print(f'voix : {duration:.2f} s, {len(timeline)} phrases')
    for s in timeline:
        print(f"  {s['id']:9s} {s['a']:6.2f} -> {s['b']:6.2f}")


if __name__ == '__main__':
    main()
