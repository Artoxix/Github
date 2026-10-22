# Revue — Max & Sam, script 1.1 (stop motion)

## Choix de réalisation

- **Script retenu** : le 1.1 « Une agence qui te garantit la 1ère place Google ? Fuis. ». C'est un dialogue Max/Sam (le meilleur test pour un personnage), c'est la 1re vidéo du calendrier (semaine 1, lundi, TikTok) et c'est le message de confiance central de la marque. Écartés : 1.2 et 1.3 (dialogues aussi, mais plus « liste »), 2.1 et 2.3 (enregistrement d'écran, sans personnage), 3.x (niche métier, mieux pour une 2e vidéo avec un Sam artisan).
- **Max** = le personnage de la planche style 1 en costume (l'expert). **Sam** = une gérante dessinée dans le même style, pour le duo prévu par le document.
- **Stop motion** : animation à 12 i/s dans une vidéo à 30 i/s, tremblé image par image, bouches et yeux de remplacement, décor et cartes en papier. Les sous-titres restent fluides (30 i/s) pour être lisibles.
- **Un seul décor, plusieurs plans** : un plateau de stop motion avec des coupes franches (large, gros plans, plan moyen) plutôt que des scènes séparées. C'est pourquoi `compositions/stage.html` est long (avertissement `composition_file_too_large` gardé volontairement).
- Petites retouches du texte : le « Fuis. » n'est pas répété au début du dialogue, « n°1 » est dit « numéro un ».

## Ce qui a été mesuré

- `hyperframes check` : 0 erreur (lint, exécution, mise en page, contrastes, lisibilité) ; un seul avertissement gardé (fichier long, voir plus haut).
- Planches d'images aux moments clés (0 ; 3,9 ; 7,2 ; 11,2 ; 18,4 ; 20,6 ; 23,6 ; 25,55 ; 27,3 ; 31,9 ; 34,6 s) et une séquence image par image de la chute du coffre (5,6 à 6,3 s) pour vérifier les paliers à 12 i/s.
- Sonie : voir le résultat de `hyperframes audio` dans la note de livraison. Le son a été **mesuré, pas écouté**.

## Ce qui n'a pas été vérifié

- La synchronisation fine des sous-titres : le minutage des mots est réparti par syllabes entre les vraies pauses de chaque prise (la transcription automatique n'a pas pu télécharger son modèle). Il peut y avoir un décalage de 1 ou 2 dixièmes sur certains mots.
- Le site seomastertech.fr (injoignable depuis l'environnement de travail).

## Le plan le plus faible

Le plan moyen 21,6–25,8 s : il enchaîne les deux cartes de résultats puis le contrat froissé et jeté. La boule de papier vole en 5 images seulement ; avec plus de temps, je ferais un plan dédié sur le geste de Sam, et une poubelle en papier où la boule atterrit.

## Pistes pour la suite

- Rigger les vues de profil de la planche pour que Max et Sam puissent se tourner l'un vers l'autre et marcher.
- Un Sam par métier (plombier, restauratrice, coiffeuse) pour les scripts 3.x.
- Une version avec les voix définitives (abonnement ElevenLabs payant pour l'usage commercial).
