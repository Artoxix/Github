# SPEC — « Une agence qui te garantit la 1ère place Google ? Fuis. » (script 1.1)

```text
GOAL:    tester le personnage (Max, style 1 « Rond & doux ») en situation : la personne doit
         reconnaître un expert calme et sympa, comprendre « pas de garantie de 1ère place »,
         et retenir l'audit gratuit.
OUTPUT:  HyperFrames, 1080 x 1920 (TikTok / Reels), 30 i/s ; animation des personnages et
         des accessoires à 12 i/s (stop motion « en deux »).
TIME:    35,4 s x 30 = 1062 images ; dialogue Max / Sam = l'horloge ; musique 120 BPM
         (15 images par temps).
LOOK:    décor en papier : mur lavande #EEF1FB avec fibres (bruit 5 %), lumières de marque
         en taches douces (#4F7FE8 22 %, #A05BDC 18 %, #6EE7FF 20 %) ; sol en carton #E3E8F8
         à y = 1200 ; personnages de la planche style 1 (aplats sans contour, dégradés,
         grain 22 %) ; cartes = papier blanc, rayon 34 px, ombre portée 0 10 0 rgba(14,26,79,.10)
         + 0 22 40 rgba(14,26,79,.12) ; encre #0E1A4F ; accent = dégradé de marque
         #4F7FE8 → #6F6FE8 → #A05BDC, un mot par carte ; alerte #E5484D (drapeau rouge).
         Poppins 800, titres 60-72 px, tracking -1,5 px ; sous-titres 64 px.
         Stop motion : chaque pièce bouge par sauts de 1/12 s, tremble de ±1,2 px / ±0,25°
         d'une image à l'autre, lumière qui papillote de 1,5 à 3,5 %.
OBJECTS: le contrat de l'agence (feuille A4 avec tampon rouge « 1er GARANTI ») ;
         le coffre-fort « ALGORITHME » suspendu à un fil, cadenas jaune ;
         3 cartes « méthode » (jauge 98/100, barre de recherche, 4,9 étoiles + épingle) ;
         carte trafic (courbe qui monte), carte appels (téléphone qui sonne) ;
         la boule de papier froissée ; le drapeau rouge planté dans le sol.
MOTION:  personnages : clés avec anticipation et dépassement (back 1,9), bouches
         de remplacement synchronisées sur la voix (4 formes), clignements ;
         cartes : posées à la main en 3 images (back.out 2), retirées en 2 images ;
         caméra : coupes franches entre plans (large, gros plan Max, gros plan Sam,
         plan moyen), jamais de fondu.
SHOTS:   0-3,15 large · Sam brandit le contrat, carte d'accroche déjà à l'écran (image 0)
         3,15-5,5 gros plan Max · main « stop », mot « Fuis. »
         5,5-10,15 large · le coffre « ALGORITHME » tombe du ciel ; carte « Personne n'a l'algo de Google »
         10,15-12,4 gros plan Sam · haussement d'épaules, « ? »
         12,4-19,8 Max à droite · « Une méthode, pas une promesse » + 3 cartes posées une à une
         19,8-21,6 gros plan Sam · curieuse
         21,6-25,85 plan moyen · trafic + appels, puis le contrat est froissé et jeté
         25,85-29,1 large · le drapeau rouge se plante ; « Promesse trop belle = agence à éviter »
         29,1-33 gros plan Max · carte audit gratuit, clin d'œil, « Lien en bio »
         33-35,4 carte de fin de la marque (logo, seomastertech.fr)
BANNED:  fond sombre, néon, lueurs ; tout qui glisse et apparaît en fondu ; titres qui
         bougent pendant la lecture ; logo collé dans un coin ; 3 cartes côte à côte ;
         mouvement fluide « motion design » sur les personnages (tout est en paliers 12 i/s).
QA:      image 0 (accroche lisible), 3,8 (Fuis), 7 (coffre), 11 (Sam ?), 18 (3 cartes),
         23,5 (trafic + appels), 25,5 (boule jetée), 27 (drapeau), 31,5 (clin d'œil), 34 (fin).
```
