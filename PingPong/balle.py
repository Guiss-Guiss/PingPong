from dataclasses import dataclass
from typing import Tuple, NamedTuple, Optional, Dict
import pygame
import math
import random
import time
from regles_tennis_table import ReglesTennisTable

# Types personnalisés
Position = Tuple[float, float]
Velocite = Tuple[float, float]

class Sons(NamedTuple):
    """Structure immuable pour les sons"""
    coup_gauche: Optional[pygame.mixer.Sound]
    coup_droit: Optional[pygame.mixer.Sound]
    service: Optional[pygame.mixer.Sound]

class BalleData(NamedTuple):
    """Structure immuable représentant l'état d'une balle"""
    position: Position
    velocite: Velocite
    rayon: int
    vitesse: float
    active: bool
    au_service: bool
    etat: str
    sons: Sons

def valider_vitesse(vitesse: float, regles: 'ReglesTennisTable') -> None:
    """Valide la vitesse selon les règles"""
    if not isinstance(vitesse, (int, float)):
        raise ValueError("La vitesse doit être un nombre")
    if vitesse < regles.VITESSE_BALLE_MIN or vitesse > regles.VITESSE_BALLE_MAX:
        raise ValueError(
            f"La vitesse doit être entre {regles.VITESSE_BALLE_MIN} "
            f"et {regles.VITESSE_BALLE_MAX}"
        )

def creer_balle(regles: 'ReglesTennisTable', vitesse: Optional[float] = None) -> BalleData:
    """Crée un nouvel état de balle avec ses paramètres initiaux"""
    if vitesse is not None:
        valider_vitesse(vitesse, regles)
    
    vitesse_initiale = vitesse if vitesse is not None else regles.VITESSE_BALLE_MIN
    
    return BalleData(
        position=(regles.LARGEUR_FENETRE // 2, regles.HAUTEUR_FENETRE // 2),
        velocite=(0, 0),
        rayon=regles.RAYON_BALLE,
        vitesse=vitesse_initiale,
        active=True,
        au_service=True,
        etat=regles.ETATS_JEU['PRET_A_SERVIR'],
        sons=Sons(None, None, None)
    )

def definir_sons(
    balle: BalleData,
    son_gauche: pygame.mixer.Sound,
    son_droit: pygame.mixer.Sound,
    son_service: pygame.mixer.Sound
) -> BalleData:
    """Retourne un nouvel état de balle avec les sons configurés"""
    return balle._replace(
        sons=Sons(son_gauche, son_droit, son_service)
    )

def definir_cible_aleatoire(
    regles: 'ReglesTennisTable',
    est_joueur_gauche: bool
) -> Position:
    """Calcule des coordonnées cibles aléatoires du côté adverse de manière pure"""
    random.seed(time.time())  # Pour l'aspect aléatoire tout en restant déterministe

    if est_joueur_gauche:
        # Cibler la moitié droite
        cible_x = (
            regles.TABLE_X +
            (regles.LARGEUR_TABLE_PIXELS / 2) +
            random.uniform(0, regles.LARGEUR_TABLE_PIXELS / 2)
        )
    else:
        # Cibler la moitié gauche
        cible_x = (
            regles.TABLE_X +
            random.uniform(0, regles.LARGEUR_TABLE_PIXELS / 2)
        )
    
    cible_y = random.uniform(
        regles.TABLE_Y,
        regles.TABLE_Y + regles.HAUTEUR_TABLE
    )
    
    return (cible_x, cible_y)

def servir(balle: BalleData, regles: 'ReglesTennisTable', serveur: int) -> BalleData:
    """Retourne un nouvel état de balle préparée pour le service"""
    if serveur not in (1, 2):
        raise ValueError("Le serveur doit être 1 ou 2")
    
    position_x = (
        regles.TABLE_X + 30 if serveur == 1
        else regles.TABLE_X + regles.LARGEUR_TABLE_PIXELS - 30
    )
    position_y = regles.HAUTEUR_FENETRE // 2

    return balle._replace(
        position=(position_x, position_y),
        velocite=(0, 0),
        active=True,
        au_service=True,
        etat=regles.ETATS_JEU['SERVICE_COMMENCE']
    )

def calculer_nouvelle_position(
    position: Position,
    velocite: Velocite
) -> Position:
    """Calcule la nouvelle position de manière pure"""
    return (
        position[0] + velocite[0],
        position[1] + velocite[1]
    )

def deplacer_balle(
    balle: BalleData,
    regles: 'ReglesTennisTable'
) -> Tuple[BalleData, bool]:
    """Retourne un nouvel état de balle déplacée et si un point a été marqué"""
    if not balle.active:
        return balle, False

    nouvelle_position = calculer_nouvelle_position(balle.position, balle.velocite)
    
    # Vérifier si un point a été marqué
    if nouvelle_position[0] < 0 or nouvelle_position[0] > regles.LARGEUR_FENETRE:
        return balle._replace(
            position=nouvelle_position,
            active=False,
            etat=regles.ETATS_JEU['POINT_TERMINE']
        ), True

    # Gérer les rebonds verticaux
    nouvelle_velocite = balle.velocite
    if nouvelle_position[1] < 0:
        nouvelle_position = (nouvelle_position[0], 0)
        nouvelle_velocite = (balle.velocite[0], abs(balle.velocite[1]))
    elif nouvelle_position[1] > regles.HAUTEUR_FENETRE:
        nouvelle_position = (nouvelle_position[0], regles.HAUTEUR_FENETRE)
        nouvelle_velocite = (balle.velocite[0], -abs(balle.velocite[1]))

    return balle._replace(
        position=nouvelle_position,
        velocite=nouvelle_velocite,
        etat=regles.ETATS_JEU['ECHANGE']
    ), False

def calculer_velocite_collision(
    balle: BalleData,
    raquette: 'Raquette',
    position_impact: float,
    regles: 'ReglesTennisTable'
) -> Velocite:
    """Calcule la nouvelle vélocité après une collision de manière pure"""
    multiplicateur_vitesse = 1 + abs(position_impact - 0.5)
    vitesse_finale = balle.vitesse * multiplicateur_vitesse
    
    cible_x, cible_y = definir_cible_aleatoire(regles, raquette.est_gauche)
    angle = math.atan2(cible_y - balle.position[1], cible_x - balle.position[0])
    
    return (math.cos(angle) * vitesse_finale, math.sin(angle) * vitesse_finale)

def gerer_collision_raquette(
    balle: BalleData,
    raquette: 'Raquette',
    position_impact: float,
    regles: 'ReglesTennisTable'
) -> BalleData:
    """Retourne un nouvel état de balle après collision avec une raquette"""
    nouvelle_position = (
        (raquette.rect.right + balle.rayon, balle.position[1])
        if raquette.est_gauche else
        (raquette.rect.left - balle.rayon, balle.position[1])
    )

    nouvelle_velocite = calculer_velocite_collision(
        balle, raquette, position_impact, regles
    )
    
    # Jouer le son approprié
    if raquette.est_gauche and balle.sons.coup_gauche:
        balle.sons.coup_gauche.play()
    elif not raquette.est_gauche and balle.sons.coup_droit:
        balle.sons.coup_droit.play()

    return balle._replace(
        position=nouvelle_position,
        velocite=nouvelle_velocite,
        au_service=False,
        etat=regles.ETATS_JEU['ECHANGE']
    )

def verifier_balle_en_jeu(balle: BalleData, regles: 'ReglesTennisTable') -> bool:
    """Vérifie si la balle est dans les limites du jeu de manière pure"""
    return not (
        balle.position[0] < -balle.rayon or
        balle.position[0] > regles.LARGEUR_FENETRE + balle.rayon or
        balle.position[1] < -balle.rayon or
        balle.position[1] > regles.HAUTEUR_FENETRE + balle.rayon
    )

def calculer_vitesse_rebond(
    vitesse: float,
    angle_impact: float,
    regles: 'ReglesTennisTable'
) -> Velocite:
    """Calcule la nouvelle vélocité après un rebond de manière pure"""
    nouvelle_vitesse_x = vitesse * math.cos(angle_impact)
    nouvelle_vitesse_y = vitesse * math.sin(angle_impact)
    
    return (nouvelle_vitesse_x, nouvelle_vitesse_y)

def appliquer_effet(
    balle: BalleData,
    effet: float,
    regles: 'ReglesTennisTable'
) -> BalleData:
    """Retourne un nouvel état de balle avec l'effet appliqué"""
    if abs(effet) > 1:
        raise ValueError("L'effet doit être entre -1 et 1")

    angle_actuel = math.atan2(balle.velocite[1], balle.velocite[0])
    angle_modifie = angle_actuel + (effet * math.pi / 6)
    
    nouvelle_velocite = calculer_vitesse_rebond(
        balle.vitesse,
        angle_modifie,
        regles
    )

    return balle._replace(velocite=nouvelle_velocite)

def jouer_son_impact(balle: BalleData, type_impact: str) -> None:
    """Joue le son approprié lors d'un impact de manière pure"""
    if type_impact not in ['gauche', 'droit', 'service']:
        raise ValueError("Type d'impact invalide")

    son = getattr(balle.sons, f"coup_{type_impact}" if type_impact != 'service' else 'service')
    if son:
        son.play()

def dessiner_balle(balle: BalleData, ecran: pygame.Surface) -> None:
    """Dessine la balle sur l'écran de manière pure"""
    pygame.draw.circle(
        ecran,
        (255, 255, 255),
        (int(balle.position[0]), int(balle.position[1])),
        balle.rayon
    )