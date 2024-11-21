from dataclasses import dataclass
from typing import Tuple, Optional
import pygame
from regles_tennis_table import ReglesTennisTable

Position = Tuple[float, float]
Velocite = Tuple[float, float]
Dimensions = Tuple[int, int]
CollisionInfo = Tuple[bool, Optional[float]]

@dataclass(frozen=True)
class Raquette:
    """État immuable d'une raquette"""
    position: Position
    velocite: Velocite
    dimensions: Dimensions
    est_gauche: bool
    image: Optional[pygame.Surface]
    temps_dernier_impact: int
    x_min: float
    x_max: float
    position_initiale: Position

def creer_raquette(x: float, y: float, vitesse: float, image: Optional[pygame.Surface] = None) -> Raquette:
    """Crée une nouvelle instance de raquette avec ses paramètres initiaux"""
    regles = ReglesTennisTable()
    
    est_gauche = x < regles.LARGEUR_FENETRE // 2
    moitie_ecran = regles.LARGEUR_FENETRE // 2
    
    # Redimensionner et retourner l'image si fournie
    image_traitee = None
    if image:
        image_traitee = pygame.transform.scale(image, 
                                             (regles.LARGEUR_RAQUETTE, 
                                              regles.HAUTEUR_RAQUETTE))
        if not est_gauche:
            image_traitee = pygame.transform.flip(image_traitee, True, False)
    
    return Raquette(
        position=(x, y),
        velocite=(0, 0),
        dimensions=(regles.LARGEUR_RAQUETTE, regles.HAUTEUR_RAQUETTE),
        est_gauche=est_gauche,
        image=image_traitee,
        temps_dernier_impact=0,
        x_min=0 if est_gauche else moitie_ecran,
        x_max=moitie_ecran if est_gauche else regles.LARGEUR_FENETRE,
        position_initiale=(x, y)
    )

def calculer_nouvelle_position(raquette: Raquette, delta_temps: float) -> Position:
    """Calcule la nouvelle position de la raquette en respectant les limites"""
    regles = ReglesTennisTable()
    
    # Calculer la nouvelle position
    nouveau_x = raquette.position[0] + raquette.velocite[0] * delta_temps
    nouveau_y = raquette.position[1] + raquette.velocite[1] * delta_temps
    
    # Appliquer les limites horizontales
    nouveau_x = max(
        raquette.x_min + raquette.dimensions[0] // 2,
        min(nouveau_x, raquette.x_max - raquette.dimensions[0] // 2)
    )
    
    # Appliquer les limites verticales
    nouveau_y = max(
        raquette.dimensions[1] // 2,
        min(nouveau_y, regles.HAUTEUR_FENETRE - raquette.dimensions[1] // 2)
    )
    
    return (nouveau_x, nouveau_y)

def deplacer_raquette(raquette: Raquette, delta_temps: float) -> Raquette:
    """Retourne une nouvelle raquette avec sa position mise à jour"""
    nouvelle_position = calculer_nouvelle_position(raquette, delta_temps)
    
    return Raquette(
        position=nouvelle_position,
        velocite=raquette.velocite,
        dimensions=raquette.dimensions,
        est_gauche=raquette.est_gauche,
        image=raquette.image,
        temps_dernier_impact=raquette.temps_dernier_impact,
        x_min=raquette.x_min,
        x_max=raquette.x_max,
        position_initiale=raquette.position_initiale
    )

def definir_velocite(raquette: Raquette, dx: float, dy: float) -> Raquette:
    """Retourne une nouvelle raquette avec la vélocité mise à jour"""
    regles = ReglesTennisTable()
    return Raquette(
        position=raquette.position,
        velocite=(dx * regles.VITESSE_RAQUETTE, dy * regles.VITESSE_RAQUETTE),
        dimensions=raquette.dimensions,
        est_gauche=raquette.est_gauche,
        image=raquette.image,
        temps_dernier_impact=raquette.temps_dernier_impact,
        x_min=raquette.x_min,
        x_max=raquette.x_max,
        position_initiale=raquette.position_initiale
    )

def verifier_collision_balle(raquette: Raquette, balle: 'Balle', 
                           temps_actuel: int) -> Tuple[Raquette, CollisionInfo]:
    """Vérifie la collision avec la balle et retourne la raquette mise à jour et l'info de collision"""
    regles = ReglesTennisTable()
    
    # Vérifier le délai entre les impacts
    if temps_actuel - raquette.temps_dernier_impact < regles.DELAI_ENTRE_IMPACTS:
        return raquette, (False, None)
    
    # Créer le rectangle de collision
    rect = pygame.Rect(
        raquette.position[0] - raquette.dimensions[0] // 2,
        raquette.position[1] - raquette.dimensions[1] // 2,
        raquette.dimensions[0],
        raquette.dimensions[1]
    )
    
    if rect.collidepoint(balle.position[0], balle.position[1]):
        # Calculer la position relative de l'impact
        position_impact = ((balle.position[1] - rect.top) / rect.height)
        
        # Mettre à jour le temps d'impact
        nouvelle_raquette = Raquette(
            position=raquette.position,
            velocite=raquette.velocite,
            dimensions=raquette.dimensions,
            est_gauche=raquette.est_gauche,
            image=raquette.image,
            temps_dernier_impact=temps_actuel,
            x_min=raquette.x_min,
            x_max=raquette.x_max,
            position_initiale=raquette.position_initiale
        )
        
        return nouvelle_raquette, (True, position_impact)
    
    return raquette, (False, None)

def reinitialiser_position(raquette: Raquette) -> Raquette:
    """Retourne une nouvelle raquette réinitialisée à sa position initiale"""
    return Raquette(
        position=raquette.position_initiale,
        velocite=(0, 0),
        dimensions=raquette.dimensions,
        est_gauche=raquette.est_gauche,
        image=raquette.image,
        temps_dernier_impact=raquette.temps_dernier_impact,
        x_min=raquette.x_min,
        x_max=raquette.x_max,
        position_initiale=raquette.position_initiale
    )

def obtenir_rectangle_collision(raquette: Raquette) -> pygame.Rect:
    """Retourne le rectangle de collision de la raquette"""
    return pygame.Rect(
        raquette.position[0] - raquette.dimensions[0] // 2,
        raquette.position[1] - raquette.dimensions[1] // 2,
        raquette.dimensions[0],
        raquette.dimensions[1]
    )

def dessiner_raquette(raquette: Raquette, ecran: pygame.Surface) -> None:
    """Dessine la raquette sur l'écran"""
    rect = obtenir_rectangle_collision(raquette)
    
    if raquette.image:
        ecran.blit(raquette.image, rect)
    else:
        regles = ReglesTennisTable()
        pygame.draw.rect(ecran, regles.BLANC, rect)