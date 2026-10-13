# Seomastertech – publicité motion design

Vidéo publicitaire explicative de 28 s au format vertical 9:16 (1080×1920, 30 i/s), pensée pour TikTok, Instagram Reels, YouTube Shorts et les stories.

## Livrables (`output/`)

| Fichier | Contenu |
|---|---|
| `seomastertech_pub_9x16.mp4` | La pub finale avec musique et bruitages (−14 LUFS, le niveau attendu par les réseaux sociaux) |
| `seomastertech_pub_9x16_sans_musique.mp4` | Même vidéo avec les bruitages seuls, pour poser un son tendance TikTok ou Instagram par-dessus |
| `seomastertech_cover.png` | Image de couverture (écran final) |
| `storyboard.png` | Planche des 14 moments clés |

## Le message

La vidéo suit le schéma classique d'une pub explicative : **problème → solution → comment ça marche → pour qui → appel à l'action**.

| Temps | À l'écran | Rôle |
|---|---|---|
| 0–4 s | « Vos clients vous cherchent sur Google… » : une recherche « plombier près de chez moi » s'écrit, les concurrents s'affichent… « …mais votre site reste invisible » (votre site est en page 5) | L'accroche, le problème |
| 4–6 s | Flash aux couleurs de la marque, le logo Seomastertech se forme : « Création de sites web & SEO » | La solution |
| 6–10 s | **Étape 01 · Création** : un site sur-mesure se construit sous nos yeux (WordPress, WooCommerce, responsive, jauge de performance) | Comment ça marche (1) |
| 10–14 s | **Étape 02 · Référencement** : la même recherche, « votre entreprise » grimpe de #27 à #1, puis SEO local (épingle sur la carte) et courbe de visites | Comment ça marche (2) |
| 14–18 s | **Étape 03 · Autonomie** : interface No-Code, on modifie le titre, on change la couleur, on publie | Comment ça marche (3) |
| 18–21 s | « Pour qui ? » : artisans, commerçants, restaurants, indépendants, TPE & PME, e-commerce | La cible |
| 21–24 s | « Tout-en-un » : site sur-mesure, référencement SEO, SEO local, maintenance, identité visuelle | L'offre complète |
| 24–28 s | « Votre site. Votre SEO. Vos clients. » + seomastertech.fr + bouton « Contactez-nous » | L'appel à l'action |

La vidéo se comprend sans le son : 85 % des vidéos sur les réseaux sont regardées en muet. Les textes restent hors des zones couvertes par l'interface de TikTok et de Reels (haut, bas, colonne de droite).

## Bande-son

La musique (pop électro à 120 BPM) et tous les bruitages sont **synthétisés de zéro** (`audio.py`), donc **libres de droits**. Chaque changement de scène tombe sur une mesure. Le logo arrive sur le « drop » à 4 s, après un riser et une demi-seconde de silence. Les bruitages (frappe au clavier, clics, apparitions, transitions, le « ding » quand le site passe #1) sont calés à l'image près sur l'animation.

### Voix off (optionnelle)

Si vous voulez enregistrer une voix off, voici un texte calé sur le montage :

> **0–4 s** – Vos clients vous cherchent sur Google… mais votre site reste invisible ?
> **4–6 s** – Découvrez Seomastertech, votre agence web et SEO.
> **6–10 s** – On crée votre site sur-mesure : un design qui vous ressemble, un site ultra-rapide.
> **10–14 s** – On booste votre référencement, même en local, pour vous faire grimper sur Google.
> **14–18 s** – Et vous gardez la main : modifiez votre site sans toucher au code.
> **18–24 s** – Artisans, commerçants, TPE ou e-commerce : un seul partenaire, tout-en-un.
> **24–28 s** – Seomastertech. Votre site, votre SEO, vos clients. Rendez-vous sur seomastertech.fr !

## Points à valider avant diffusion

- **Sources** : seomastertech.fr n'était pas joignable depuis mon environnement de travail. Le contenu s'appuie sur les captures du site (services du menu, plateformes WordPress / WooCommerce / Google, « Interface No-Code », « Performance Web ») et sur la fiche annuaire de l'agence (création de sites et SEO pour TPE et entrepreneurs).
- **Logo** : il est redessiné en vectoriel d'après la capture. Si vous avez le fichier officiel, remplacez la fonction `LOGO()` dans `index.html`.
- **Chiffres** : le score de performance (98) et le passage de #27 à #1 sont des illustrations, pas des promesses de résultat.
- **Cibles** : la liste « Pour qui ? » est une proposition, ajustable en une ligne.

## Modifier et régénérer la vidéo

L'animation est une page HTML (`index.html`) rendue image par image avec Chromium. Tous les textes y sont lisibles et modifiables directement. Les instants de chaque animation sont des constantes du script (fonctions `s1()` à `s8()`).

```bash
./build.sh                                   # régénère tout dans output/ (≈ 3 min)
node render.js --stills=4.5,12,26.6          # aperçus PNG de quelques instants dans build/
```

Prérequis : Node.js avec Playwright (Chromium), Python 3 avec numpy, ffmpeg.

Police : Poppins (licence SIL Open Font License, voir `fonts/OFL.txt`).
