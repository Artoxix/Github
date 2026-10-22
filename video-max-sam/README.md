# Max & Sam — « Une agence qui te garantit la 1ère place Google ? Fuis. » (stop motion)

Vidéo de test du personnage **Max** (planche personnage, **style 1 « Rond & doux »**) en situation réelle : le **script 1.1** du document « Scripts vidéos + calendrier éditorial », animé en **stop motion** avec HyperFrames.

Format vertical 9:16 (1080 × 1920, 30 i/s), 36 s, pour TikTok, Reels et LinkedIn. C'est la vidéo prévue le lundi de la semaine 1 du calendrier.

## Livrables (`output/`)

| Fichier | Contenu |
|---|---|
| `Seomastertech_Max_Sam_stop_motion.mp4` | La vidéo finale : voix, musique, bruitages, sous-titres (−14 LUFS) |
| `Seomastertech_Max_Sam_leger.mp4` | La même en version légère, pour l'envoyer par WhatsApp, Messenger ou e-mail |
| `planche.png` | Les moments clés sur une planche |

## Le film

| Temps | Plan | Ce qui se passe |
|---|---|---|
| 0–3 s | large | **Accroche déjà à l'écran** : « On vous garantit la 1ère place Google ». Sam brandit le contrat de l'agence, tout excitée. |
| 3–5,5 s | gros plan Max | « Alors fuis. » Main levée, mot « Fuis. » |
| 5,5–10 s | large | Un coffre-fort « ALGORITHME » cadenassé tombe du ciel au bout d'un fil. « Personne n'a l'algo de Google. » Max secoue la tête. |
| 10–12,5 s | gros plan Sam | « Alors… je paie pour quoi ? » Haussement d'épaules, points d'interrogation. |
| 12,5–19,8 s | Max | « Une méthode, pas une promesse » : 3 cartes posées une à une (site technique propre, contenu qui répond, confiance avec avis et fiche Google). |
| 19,8–21,6 s | gros plan Sam | « Et ça me donne quoi, concrètement ? » |
| 21,6–25,8 s | plan moyen | « + de trafic qualifié », « + d'appels » (le téléphone sonne), puis Sam froisse le contrat et le jette. |
| 25,8–29 s | large | Un drapeau rouge se plante entre eux : « Promesse trop belle = agence à éviter ». |
| 29–33 s | gros plan Max | « Audit gratuit de ton site », tampon « sans promesse bidon », clin d'œil, « Lien en bio ». |
| 33–36 s | carte de fin | Logo Seomastertech, « Création de sites web & SEO », seomastertech.fr |

Le texte dit est celui du script 1.1, à deux retouches près : le « Fuis. » du début du dialogue n'est pas répété (il est déjà dans l'accroche), et « n°1 » est dit « numéro un ».

## Le personnage

- **Max** reprend la planche style 1 à l'identique (mêmes formes et couleurs : peau #F47A54, cheveux #8E5B34, costume navy, cravate bleue, aplats sans contour, dégradés, grain). Il est découpé en pièces articulées comme une marionnette : épaules, coudes, tête.
- **Sam**, la gérante, est dessinée avec la même construction (grosse tête, grandes mains) : chignon, marinière, tablier moutarde. Le document de scripts prévoit un duo récurrent, il fallait donc un second personnage.
- Comme en vraie stop motion, les **visages sont des pièces de remplacement** : 5 formes d'yeux, des sourcils qui bougent, 9 bouches. Les expressions (joie, surprise, perplexité, tristesse, sérieux, clin d'œil…) viennent de la planche « Émotions » du style 1.
- La **bouche suit la voix** : son ouverture est calculée sur le volume de chaque réplique, à 12 images par seconde.

## Le style stop motion

- Tout ce qui bouge avance **par paliers de 1/12 s** (on « anime en deux », comme en pâte à modeler ou en papier découpé), alors que la vidéo reste à 30 i/s.
- Chaque pièce **tremble très légèrement d'une image à l'autre** (±1,2 px, ±0,25°), comme si elle avait été reposée à la main, et la lumière papillote de 1,5 à 3,5 %.
- Le décor est en papier : un mur lavande avec les lumières de la marque (bleu, violet, cyan), un sol en carton. Les cartes de texte sont des feuilles blanches posées en 3 images.
- La caméra passe d'un plan à l'autre en coupe franche (large, gros plan, plan moyen), jamais en fondu.

## La DA reprise de la vidéo de la marque

Poppins en gras, encre marine #0E1A4F, dégradé de marque #4F7FE8 → #6F6FE8 → #A05BDC sur le mot clé, cartes blanches arrondies avec ombre douce. Les sous-titres reprennent ceux de la vidéo « le SEO expliqué » : 2 à 4 mots, mot prononcé surligné. On a ajouté le nom de celui qui parle : **Max en violet de marque, Sam en orangé**. La carte de fin reprend celle de la marque.

## Voix, musique, bruitages

- **Voix** (ElevenLabs, modèle Eleven v4) : Max = « Thomas San » (homme ~35 ans, un peu grave, sympa, posé), Sam = « Agathe » (femme, naturelle et expressive). Les deux prises sont dans le projet ElevenLabs « Seomastertech – Max & Sam (script 1.1) ».
- **Musique** : 120 BPM, pizzicato et marimba, légère et sautillante. Elle est synthétisée dans `audio.py`, donc libre de droits, et baisse automatiquement sous les voix.
- **Bruitages** : papier posé, coffre qui tombe, molette, cadenas, frappe au clavier, téléphone, papier froissé, drapeau planté, tampon. Ils viennent du pack de la skill media-use ou sont synthétisés.
- **Sonie** : mixage final à −14 LUFS, le niveau attendu par les réseaux sociaux. Le son a été mesuré, pas écouté.

## Points à valider

- **Le site seomastertech.fr** n'était pas joignable depuis l'environnement de travail. Le contenu s'appuie sur le document de scripts, la vidéo de référence et les vidéos déjà faites dans ce dépôt.
- **L'audit gratuit** est l'appel à l'action écrit dans le script. Vérifiez qu'il est bien proposé.
- **Le compte ElevenLabs** a signalé une « activité inhabituelle » et coupé l'accès du plan gratuit pour une des prises. Avec le plan gratuit, l'usage commercial n'est pas permis et ElevenLabs doit être crédité. Pour publier, il faut une prise faite avec un abonnement payant.
- **Sam** est une proposition : coiffure, tenue et voix se changent facilement (voir plus bas).

## Modifier et régénérer

```bash
python3 voice/prepare.py   # découpe les prises, place les répliques, minutage des mots et des bouches
python3 audio.py           # musique + bruitages (baissés sous les voix)
npx hyperframes check      # vérifications
npx hyperframes render -q delivery -o build/render_raw.mp4
```

Puis normaliser le son à −14 LUFS :

```bash
ffmpeg -i build/render_raw.mp4 -c:v copy -af loudnorm=I=-14:TP=-1:LRA=11 -c:a aac -b:a 192k output/Seomastertech_Max_Sam_stop_motion.mp4
```

- **Changer une réplique** : régénérer la prise dans ElevenLabs, remplacer `voice/max_raw.mp3` ou `voice/sam_raw.mp3`, ajuster les débuts et fins de morceaux dans `LINES` (`voice/prepare.py`), relancer les commandes ci-dessus. Les gestes, les cartes et les sous-titres sont calés sur les mots (`W('m3', 'site')`) et suivent d'eux-mêmes. Les coupes de plan et les `data-start` des cartes dans `compositions/stage.html` sont en secondes : à reprendre si le texte change beaucoup.
- **Changer les couleurs d'un personnage** : `PALETTES` dans `assets/rig.js` (les ombres, joues et lèvres se recalculent comme dans la planche).
- **Changer le jeu d'un personnage** : les pistes `SAM` et `MAX` dans `compositions/stage.html`. Chaque clé est `[instant, valeur, durée]` : bras `{ L: [épaule, coude], R: [...] }` en degrés vers l'extérieur, humeur (`joy`, `surprised`, `perplexed`, `serious`, `wink`…), tête, regard.

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | Composition racine : la scène, la carte de fin, les sous-titres, les voix, la musique et les bruitages |
| `compositions/stage.html` | Le décor, Max et Sam, les accessoires, les cartes du script, la caméra, le rendu stop motion à 12 i/s |
| `compositions/captions.html` | Les sous-titres, colorés selon le personnage |
| `compositions/endcard.html` | La carte de fin de la marque |
| `assets/rig.js` | Le rig des personnages (pièces, humeurs, bouches) |
| `assets/timing.js` | Le minutage des répliques, des mots et des bouches (généré) |
| `voice/` | Les prises ElevenLabs brutes et `prepare.py` |
| `SPEC.md`, `REVIEW.md` | La note de réalisation et la revue |
