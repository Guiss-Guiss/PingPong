# Jeu de Tennis de Table 🏓

Un jeu de tennis de table en Python utilisant Pygame, permettant à deux joueurs de s'affronter sur le même ordinateur.

## 📋 Prérequis

- Python 3.x
- Pygame

## 💻 Installation

1. Clonez le dépôt ou téléchargez les fichiers source
```bash
git clone https://github.com/Guiss-Guiss/PingPong
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## 🎮 Comment jouer

### Démarrer le jeu
```bash
python main.py
```

### Contrôles

#### Joueur 1 (Gauche)
- `W` : Monter
- `S` : Descendre
- `A` : Gauche
- `D` : Droite

#### Joueur 2 (Droite)
- `↑` : Monter
- `↓` : Descendre
- `←` : Gauche
- `→` : Droite

#### Autres commandes
- `ESPACE` : Servir
- `R` : Réinitialiser le jeu
- `ESC`/`Q` : Quitter le jeu

## 🎯 Règles du jeu

- Le jeu se joue en plusieurs manches (jeux)
- Chaque jeu se joue en 11 points avec 2 points d'écart
- En cas d'égalité à 10-10, il faut 2 points d'écart pour gagner
- Le service change tous les 2 points
- Le premier joueur à gagner 4 jeux remporte le match

## 🔧 Fonctionnalités

- Sélection du niveau de difficulté (vitesse de la balle)
- Système de score complet
- Gestion des services
- Effets sonores
- Affichage du score et des statistiques
- Interface utilisateur intuitive

## 📊 Logs

Le jeu génère des logs dans le dossier `logs/` pour faciliter le débogage.

## 🌟 Niveaux de difficulté

- **Débutant** (1-3) : Vitesse de balle lente
- **Intermédiaire** (4-6) : Vitesse de balle moyenne
- **Expert** (7-9) : Vitesse de balle rapide
- **Maître** (10) : Vitesse de balle maximale

## 🏆 Système de points

- Un point est marqué quand l'adversaire ne renvoie pas la balle
- Le service change tous les 2 points
- En cas d'égalité (10-10), le service alterne à chaque point


