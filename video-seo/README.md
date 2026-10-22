# Seomastertech – le SEO expliqué (vidéo narrée, 1 min)

Vidéo verticale 9:16 (1080×1920, 30 i/s, 1 min 05) pour Instagram Reels et TikTok. Un narrateur raconte l'histoire de deux garages de la même rue : même travail, même qualité, mêmes prix. Pourtant, le garage Léon a 3 fois plus de clients que le garage Marcel, parce qu'il a fait appel à Seomastertech pour son référencement.

## Livrables (`output/`)

| Fichier | Contenu |
|---|---|
| `Seomastertech_SEO_explique.mp4` | La vidéo finale : voix off, musique, bruitages, sous-titres (−14 LUFS) |
| `Seomastertech_SEO.mp4` | La même vidéo en version légère (8 Mo, qualité identique à l'œil), à envoyer par WhatsApp, Messenger, e-mail ou Discord |
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
> Le garage Léon, lui, a fait appel à Seomastertech. Site, référencement, SEO local : on s'occupe de tout. Et toi, tu préfères être le garage Léon… ou le garage Marcel ? Dis-le en commentaire. Et rendez-vous sur seomastertech.fr

Les garages Léon et Marcel sont fictifs ; les chiffres (3 fois plus de clients, 4,9 étoiles, 98/100) illustrent l'histoire et ne sont pas des promesses de résultat.

## Comment c'est fabriqué

1. `iso.js` : le quartier en 3D isométrique (diorama low-poly) : garages, immeubles, maison, boulangerie, café, mobilier urbain, voitures et piétons animés.
1. `voice.py` : voix off. La prise ElevenLabs (`voice/voix_off.mp3`) est accélérée de 10 % (hauteur conservée), découpée phrase par phrase sur ses vraies pauses, les silences sont recalés, et chaque mot affiché reçoit son minutage (`build/timeline.json`) d'après la transcription ElevenLabs Scribe (`voice/mots.json`). La colonne `say` du `SCRIPT` contient le texte envoyé à ElevenLabs, la colonne `show` le sous-titre affiché.
2. `index.html` + `render.js` : l'animation se cale automatiquement sur le minutage de la voix, puis Chromium la rend image par image.
3. `audio.py` : musique 120 BPM et bruitages synthétisés (libres de droits), musique atténuée sous la voix, mixage à −14 LUFS.

Pour régénérer la vidéo : `./build.sh` (≈ 8 min). Pour modifier le texte : changer `SCRIPT` dans `voice.py`, coller la sortie de `python3 voice.py --texte` dans ElevenLabs (voix « Diano V », modèle Eleven v4, langue français), remplacer `voice/voix_off.mp3` par la nouvelle prise et `voice/mots.json` par sa transcription Scribe (liste des mots avec `start`/`end`), puis relancer `./build.sh` : les scènes et sous-titres suivent.

## Voix off

- **Voix** : « Diano V » de la bibliothèque ElevenLabs (homme, français standard, ton assuré et dynamique, pensée pour les réseaux sociaux et le storytelling), modèle Eleven v4. Le texte est généré d'un seul tenant pour garder un phrasé naturel ; la prise et sa transcription sont dans le projet ElevenLabs « Seomastertech – SEO expliqué (voix off) ».
- **Prononciation** : « SEO » est écrit en alphabet phonétique (`/ɛsiˈo/`) pour être dit à l'anglaise, « èss-i-o », d'un seul trait ; « Google » est dit naturellement ; la marque est lue « Séo Master Tech ».
- **Droits** : la licence ElevenLabs autorise l'usage commercial (publicité) à partir d'un abonnement payant ; avec le plan gratuit, l'usage commercial n'est pas permis et ElevenLabs doit être crédité.
