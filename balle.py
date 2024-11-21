import pygame
import math
import random
import time
import logging
from regles_tennis_table import creer_regles

logger = logging.getLogger('tennis_table')

def creer_balle(vitesse=None):
    try:
        regles = creer_regles()
        vitesse = vitesse if vitesse is not None else regles['VITESSE_BALLE_MIN']
        logger.debug(f"Création d'une nouvelle balle avec vitesse={vitesse}")
        
        balle = {
            'regles': regles,
            'rayon': regles['RAYON_BALLE'],
            'couleur': regles['BLANC'],
            'vitesse': vitesse,
            'x': regles['LARGEUR_FENETRE'] // 2,
            'y': regles['HAUTEUR_FENETRE'] // 2,
            'au_service': True,
            'active': True,
            'etat': regles['ETATS_JEU']['PRET_A_SERVIR'],
            'dx': 0,
            'dy': 0,
            'son_coup_gauche': None,
            'son_coup_droit': None,
            'son_service': None,
            'cible_x': None,
            'cible_y': None
        }
        
        logger.debug(f"Balle créée: {balle}")
        return balle
    except Exception as e:
        logger.error(f"Erreur lors de la création de la balle: {e}", exc_info=True)
        raise RuntimeError("Impossible de créer la balle") from e

def definir_sons(balle, son_gauche, son_droit, son_service):
    try:
        if not isinstance(balle, dict):
            raise ValueError("La balle doit être un dictionnaire")
            
        nouvelle_balle = {
            **balle,
            'son_coup_gauche': son_gauche,
            'son_coup_droit': son_droit,
            'son_service': son_service
        }
        logger.debug("Sons de la balle définis")
        return nouvelle_balle
    except Exception as e:
        logger.error(f"Erreur lors de la définition des sons: {e}", exc_info=True)
        return balle 
    
def reinitialiser(balle):
    try:
        logger.debug("Réinitialisation de la balle")
        if not isinstance(balle, dict) or 'regles' not in balle:
            raise ValueError("Balle invalide")

        regles = balle['regles']
        nouvelle_balle = {
            **balle,
            'x': regles['LARGEUR_FENETRE'] // 2,
            'y': regles['HAUTEUR_FENETRE'] // 2,
            'dx': 0,
            'dy': 0,
            'au_service': True,
            'active': True,
            'etat': regles['ETATS_JEU']['PRET_A_SERVIR'],
            'cible_x': None,
            'cible_y': None
        }
        logger.debug(f"Balle réinitialisée: {nouvelle_balle}")
        return nouvelle_balle
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation de la balle: {e}", exc_info=True)
        return balle

def servir(balle, serveur):
    try:
        logger.debug(f"Service par joueur {serveur}")
        if not isinstance(balle, dict) or not isinstance(serveur, int):
            raise ValueError("Paramètres invalides pour le service")
        if serveur not in [1, 2]:
            raise ValueError("Numéro de serveur invalide")

        regles = balle['regles']
        nouvelle_balle = {
            **balle,
            'au_service': True,
            'active': True,
            'etat': regles['ETATS_JEU']['SERVICE_COMMENCE'],
            'dy': 0,
            'dx': 0,
            'y': regles['HAUTEUR_FENETRE'] // 2
        }

        if serveur == 1:
            nouvelle_balle['x'] = regles['TABLE_X'] + 30
            est_gauche = True
            logger.debug("Service depuis la gauche")
        else:
            nouvelle_balle['x'] = regles['TABLE_X'] + regles['LARGEUR_TABLE_PIXELS'] - 30
            est_gauche = False
            logger.debug("Service depuis la droite")

        try:
            cible_x, cible_y = definir_cible_aleatoire(nouvelle_balle, est_gauche)
            nouvelle_balle.update({
                'cible_x': cible_x,
                'cible_y': cible_y,
                'service_depuis_gauche': est_gauche
            })
        except Exception as e:
            logger.error(f"Erreur lors de la définition de la cible: {e}")
            nouvelle_balle.update({
                'cible_x': regles['LARGEUR_FENETRE'] // 2,
                'cible_y': regles['HAUTEUR_FENETRE'] // 2,
                'service_depuis_gauche': est_gauche
            })

        logger.debug(f"Nouvelle balle après service: {nouvelle_balle}")
        return nouvelle_balle

    except Exception as e:
        logger.error(f"Erreur lors du service: {e}", exc_info=True)
        return balle

def definir_cible_aleatoire(balle, est_joueur_gauche):
    try:
        logger.debug(f"Calcul cible aléatoire (depuis gauche: {est_joueur_gauche})")
        temps_actuel = time.time()
        random.seed(temps_actuel)
        regles = balle['regles']

        if est_joueur_gauche:
            cible_x = regles['TABLE_X'] + (regles['LARGEUR_TABLE_PIXELS'] * 3/4)
        else:
            cible_x = regles['TABLE_X'] + (regles['LARGEUR_TABLE_PIXELS'] * 1/4)
                
        cible_y = random.uniform(regles['TABLE_Y'], 
                               regles['TABLE_Y'] + regles['HAUTEUR_TABLE'])
                               
        logger.debug(f"Cible calculée: ({cible_x}, {cible_y})")
        return cible_x, cible_y
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la cible: {e}", exc_info=True)
        raise

def deplacer(balle):
    if not balle['active']:
        return balle, False

    try:
        nouvelle_balle = {
            **balle,
            'x': balle['x'] + balle['dx'],
            'y': balle['y'] + balle['dy']
        }

        if nouvelle_balle['x'] < 0 or nouvelle_balle['x'] > nouvelle_balle['regles']['LARGEUR_FENETRE']:
            nouvelle_balle['active'] = False
            nouvelle_balle['etat'] = nouvelle_balle['regles']['ETATS_JEU']['POINT_TERMINE']
            logger.debug("Point terminé: balle hors limites")
            return nouvelle_balle, True

        if nouvelle_balle['y'] < 0:
            nouvelle_balle['y'] = 0
            nouvelle_balle['dy'] = abs(nouvelle_balle['dy'])
            logger.debug("Collision avec le haut")
        elif nouvelle_balle['y'] > nouvelle_balle['regles']['HAUTEUR_FENETRE']:
            nouvelle_balle['y'] = nouvelle_balle['regles']['HAUTEUR_FENETRE']
            nouvelle_balle['dy'] = -abs(nouvelle_balle['dy'])
            logger.debug("Collision avec le bas")

        nouvelle_balle['etat'] = nouvelle_balle['regles']['ETATS_JEU']['ECHANGE']
        return nouvelle_balle, False

    except Exception as e:
        logger.error(f"Erreur lors du déplacement de la balle: {e}", exc_info=True)
        return balle, False
    
def gerer_collision_raquette(balle, raquette, position_impact):
    try:
        logger.debug(f"Collision avec raquette à la position relative {position_impact}")
        
        try:
            cible_x, cible_y = definir_cible_aleatoire(balle, raquette['est_raquette_gauche'])
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la nouvelle cible: {e}")
            cible_x = raquette['est_raquette_gauche'] and balle['regles']['LARGEUR_FENETRE'] - 50 or 50
            cible_y = balle['regles']['HAUTEUR_FENETRE'] // 2
        
        try:
            if balle['x'] is not None and balle['y'] is not None and cible_x is not None and cible_y is not None:
                angle = math.atan2(cible_y - balle['y'], cible_x - balle['x'])
                logger.debug(f"Angle calculé: {angle}")
            else:
                angle = 0 if raquette['est_raquette_gauche'] else math.pi
                logger.debug(f"Angle par défaut utilisé: {angle}")
        except Exception as e:
            logger.error(f"Erreur lors du calcul de l'angle: {e}")
            angle = 0 if raquette['est_raquette_gauche'] else math.pi

        position_relative = (balle['y'] - raquette['rect'].top) / raquette['rect'].height
        multiplicateur_vitesse_impact = 1 + abs(position_relative - 0.5)
        vitesse_finale = balle['vitesse'] * multiplicateur_vitesse_impact

        nouvelle_balle = {
            **balle,
            'au_service': False,
            'etat': balle['regles']['ETATS_JEU']['ECHANGE'],
            'dx': math.cos(angle) * vitesse_finale,
            'dy': math.sin(angle) * vitesse_finale,
            'cible_x': cible_x,
            'cible_y': cible_y
        }

        if raquette['est_raquette_gauche']:
            nouvelle_balle['x'] = raquette['rect'].right + nouvelle_balle['rayon']
            if nouvelle_balle['son_coup_gauche']:
                try:
                    nouvelle_balle['son_coup_gauche'].play()
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture du son gauche: {e}")
        else:
            nouvelle_balle['x'] = raquette['rect'].left - nouvelle_balle['rayon']
            if nouvelle_balle['son_coup_droit']:
                try:
                    nouvelle_balle['son_coup_droit'].play()
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture du son droit: {e}")

        logger.debug(f"Nouvelle balle après collision: {nouvelle_balle}")
        return nouvelle_balle

    except Exception as e:
        logger.error(f"Erreur lors de la gestion de la collision: {e}", exc_info=True)
        return balle

def dessiner(balle, ecran):
    try:
        pygame.draw.circle(
            ecran, 
            balle['couleur'], 
            (int(balle['x']), int(balle['y'])), 
            balle['rayon']
        )
    except Exception as e:
        logger.error(f"Erreur lors du dessin de la balle: {e}", exc_info=True)
