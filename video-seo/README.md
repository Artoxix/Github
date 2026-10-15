# Seomastertech – le SEO expliqué (vidéo narrée, 1 min)

Vidéo verticale 9:16 (1080×1920, 30 i/s, 64 s) pour Instagram Reels et TikTok. Un narrateur raconte l'histoire de deux garages de la même rue : même travail, même qualité, mêmes prix. Pourtant, le garage Léon a 3 fois plus de clients que le garage Marcel, parce qu'il a fait appel à Seomastertech pour son référencement.

## Livrables (`output/`)

| Fichier | Contenu |
|---|---|
| `Seomastertech_SEO_explique.mp4` | La vidéo finale : voix off, musique, bruitages, sous-titres (−14 LUFS) |
| `Seomastertech_SEO_explique_sans_musique.mp4` | Voix off et bruitages sans musique, pour poser un son tendance de la plateforme |
| `storyboard.png` | Planche des moments clés |

## Codes « viraux » appliqués

- **Accroche en moins d'une seconde**, avec mouvement dès la 1re image et un chiffre concret (« 3 fois plus de clients »).
- **Question ouverte** (« c'est quoi la différence ? ») qui pousse à rester jusqu'à la réponse.
- **Mots-clés prononcés tôt** (garage, SEO, Google, référencement) : TikTok transcrit l'audio pour sa recherche.
- **Sous-titres dynamiques** 2-3 mots à la fois, mot prononcé surligné, pour le visionnage sans son.
- **Rythme** : un changement visuel toutes les 2 à 4 s, des bruitages comiques (virevoltant, trombone triste sur « invisible », tampon).
- **Appel aux commentaires** (« Garage Léon ou garage Marcel ? »), puis carte de fin avec seomastertech.fr.
- **Zones de sécurité** : rien d'important sous l'interface TikTok et Instagram.

## Script de la voix off

> Ces deux garages sont dans la même rue. Pourtant, l'un a 3 fois plus de clients que l'autre. Même travail. Même qualité. Mêmes prix. Alors… c'est quoi la différence ? La réponse tient en 3 lettres : SEO.
> Ta voiture tombe en panne. Tu sors ton téléphone et tu tapes : « garage près de moi ». Sur Google, le garage Léon ? Premier résultat. Le garage Marcel ? Page 3. Autant dire… invisible.
> Le SEO, ou référencement naturel, c'est l'art de convaincre Google que ton site est la meilleure réponse. Pour ça, Google regarde 3 choses. 1 : ce que dit ton site. Tes services, ta ville, les bons mots-clés. 2 : la technique. Un site rapide et parfait sur mobile. 3 : la confiance. Tes avis clients et ta fiche Google.
> Résultat : plus de visibilité, plus d'appels, plus de rendez-vous. Et contrairement à la pub, tu ne paies pas chaque clic.
> Le garage Léon, lui, a fait appel à Seomastertech. Site, référencement, SEO local : ils s'occupent de tout. Et toi, tu préfères être le garage Léon… ou le garage Marcel ? Dis-le en commentaire. Et rendez-vous sur seomastertech.fr

Les garages Léon et Marcel sont fictifs ; les chiffres (3 fois plus de clients, 4,9 étoiles, 98/100) illustrent l'histoire et ne sont pas des promesses de résultat.

## Comment c'est fabriqué

1. `iso.js` : la rue, les deux garages et les voitures en 3D isométrique (diorama low-poly).
1. `voice.py` : voix off de synthèse française (Piper « Tom », via sherpa-onnx), phrase par phrase, avec le minutage de chaque mot (`build/timeline.json`). La colonne `say` contient l'orthographe phonétique lue par la voix (« Gougle », « S.E.O. », « Séo Master Tek ») ; la colonne `show` contient le sous-titre affiché.
2. `index.html` + `render.js` : l'animation se cale automatiquement sur le minutage de la voix, puis Chromium la rend image par image.
3. `audio.py` : musique 120 BPM et bruitages synthétisés (libres de droits), musique atténuée sous la voix, mixage à −14 LUFS.

Pour modifier le texte, changer `SCRIPT` dans `voice.py` puis relancer `./build.sh` (≈ 8 min) : les scènes et sous-titres suivent.
