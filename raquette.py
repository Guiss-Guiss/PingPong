import pygame
import logging
from regles_tennis_table import creer_regles

logger = logging.getLogger('tennis_table')

def creer_raquette(x, y, vitesse, image=None):
    """Créer une nouvelle raquette avec son état initial"""
    logger.debug(f"Création raquette à ({x}, {y}) avec vitesse {vitesse}")
    regles = creer_regles()
    rect = pygame.Rect(x, y, regles['LARGEUR_RAQUETTE'], regles['HAUTEUR_RAQUETTE'])
    
    HAUTEUR_TETE = regles['HAUTEUR_RAQUETTE'] * 0.55
    y_tete = y + regles['HAUTEUR_RAQUETTE']
    zone_collision = pygame.Rect(x, y_tete, regles['LARGEUR_RAQUETTE'], HAUTEUR_TETE)
    
    est_raquette_gauche = x < regles['LARGEUR_FENETRE'] // 2
    
    if image:
        image = pygame.transform.scale(image, 
                                    (regles['LARGEUR_RAQUETTE'], 
                                     regles['HAUTEUR_RAQUETTE']))
        if not est_raquette_gauche:
            image = pygame.transform.flip(image, True, False)
    
    moitie_ecran = regles['LARGEUR_FENETRE'] // 2
    x_min = 0 if est_raquette_gauche else moitie_ecran
    x_max = moitie_ecran if est_raquette_gauche else regles['LARGEUR_FENETRE']
    
    raquette = {
        'regles': regles,
        'rect': rect,
        'zone_collision': zone_collision,
        'vitesse': vitesse,
        'image': image,
        'est_raquette_gauche': est_raquette_gauche,
        'dx': 0,
        'dy': 0,
        'temps_dernier_impact': 0,
        'delai_entre_impacts': regles['DELAI_ENTRE_IMPACTS'],
        'x_min': x_min,
        'x_max': x_max,
        'x_initial': x,
        'y_initial': y
    }
    logger.debug(f"Raquette créée: {raquette}")
    return raquette

def deplacer(raquette):
    nouveau_x = raquette['rect'].x + raquette['dx']
    nouveau_y = raquette['rect'].y + raquette['dy']
    logger.debug(f"Déplacement raquette vers ({nouveau_x}, {nouveau_y})")
    
    nouvelle_raquette = {**raquette}
    nouveau_rect = nouvelle_raquette['rect'].copy()
    nouvelle_zone_collision = nouvelle_raquette['zone_collision'].copy()
    
    if raquette['x_min'] <= nouveau_x <= raquette['x_max'] - raquette['rect'].width:
        nouveau_rect.x = nouveau_x
        nouvelle_zone_collision.x = nouveau_x
    else:
        logger.debug("Limite horizontale atteinte")
            
    nouveau_rect.y = min(max(0, nouveau_y), 
                        raquette['regles']['HAUTEUR_FENETRE'] - raquette['rect'].height)
    if nouveau_rect.y != nouveau_y:
        logger.debug("Limite verticale atteinte")
    
    nouvelle_zone_collision.y = nouveau_rect.y + raquette['regles']['HAUTEUR_RAQUETTE'] * 0.05
    
    nouvelle_raquette['rect'] = nouveau_rect
    nouvelle_raquette['zone_collision'] = nouvelle_zone_collision
    return nouvelle_raquette

def definir_velocite(raquette, dx, dy):
    """Définir la vélocité de la raquette pour les deux axes"""
    logger.debug(f"Nouvelle vélocité: dx={dx}, dy={dy}")
    return {
        **raquette,
        'dx': dx * raquette['vitesse'],
        'dy': dy * raquette['vitesse']
    }

def verifier_collision_balle(raquette, balle, temps_actuel):
    if temps_actuel - raquette['temps_dernier_impact'] < raquette['delai_entre_impacts']:
        return False, None
        
    balle_rect = pygame.Rect(
        balle['x'] - balle['rayon'],
        balle['y'] - balle['rayon'],
        balle['rayon'] * 2,
        balle['rayon'] * 2
    )
    
    collision = raquette['zone_collision'].colliderect(balle_rect)
    if collision:
        position_impact = (balle['y'] - raquette['zone_collision'].top) / raquette['zone_collision'].height
        logger.debug(f"Collision détectée à la position relative {position_impact}")
        return True, position_impact
    
    return False, None

def reinitialiser_position(raquette):
    """Réinitialiser la raquette à sa position initiale"""
    logger.debug("Réinitialisation position raquette")
    nouvelle_raquette = arreter(raquette)
    nouveau_rect = nouvelle_raquette['rect'].copy()
    nouveau_rect.x = nouvelle_raquette['x_initial']
    nouveau_rect.y = nouvelle_raquette['y_initial']
    
    nouvelle_zone_collision = nouvelle_raquette['zone_collision'].copy()
    nouvelle_zone_collision.x = nouveau_rect.x
    nouvelle_zone_collision.y = nouveau_rect.y + raquette['regles']['HAUTEUR_RAQUETTE'] * 0.05
    
    nouvelle_raquette['rect'] = nouveau_rect
    nouvelle_raquette['zone_collision'] = nouvelle_zone_collision
    return nouvelle_raquette

def arreter(raquette):
    logger.debug("Arrêt de la raquette")
    return {
        **raquette,
        'dx': 0,
        'dy': 0
    }

def dessiner(raquette, ecran):
    if raquette['image']:
        ecran.blit(raquette['image'], raquette['rect'])
    else:
        pygame.draw.rect(ecran, raquette['regles']['BLANC'], raquette['rect'])
