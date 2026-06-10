# Miaouno

## Présentation

Le Miaouno est un jeu de Uno en multijoueur en LAN avec une interface graphique.
Le projet est grossièrement composé de 3 parties :
- Le modèle du Uno avec toute la logique métier
- L'interface graphique, faite avec l'aide de la librairie Pygame qui permet l'affichage d'images et de rectangles. Nous avons créé une petite surcouche qui permet d'avoir des composants d'UI génériques afin de les réutiliser régulièrement.
- La partie réseau qui fait le lien entre les différents joueurs (Host et ses clients)

## Dépendances
Vous devez avoir installé sur votre ordinateur la version 3.12 de Python minimum.
Votre version de Python doit posséder les packages suivants :
- pygame (Dernière version)
- pygame-textinput (Dernière version)

Pour les installer, vous pouvez utiliser les commandes :
```
pip install pygame
```
et
```
pip install pygame-textinput
```

Il est possible d'utiliser un venv si vous le souhaitez.

## Pour récupérer le projet et le lancer
1. Cloner le projet
2. Vérifiez que vous possédez bien les dépendances nécessaires et installez-les si ce n'est pas le cas
3. **IMPORTANT** : Afin de tester le projet, étant donné qu'il est en multijoueur local, il vous faudra lancer le projet au moins deux fois en étant connecté sur un réseau local (Wifi / Forfait 4G). Windows vous demandera potentiellement l'autorisation pour que l'application communique sur des réseaux privés ou publics. Il vous faudra sélectionner "Réseau privé" lorsque cela arrivera.
4. Placez-vous à la racine du projet et lancez-le avec ```python main.py```. Afin de tester pleinement le projet, il faudra lancer deux fois le programme pour avoir deux joueurs.

## Autres
Info à propos du jeu : Lorsqu'un +2 ou +4 est joué, il n'y a pas encore d'indication visuelle qui indique qu'il faut cliquer sur la pioche. Cliquez directement sur la pioche pour récupérer vos cartes et continuer.
