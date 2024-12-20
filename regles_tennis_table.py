import pygame
import logging

logger = logging.getLogger('tennis_table')

def creer_regles():
    try:
        logger.debug("Création des règles du jeu")
        CONTROLES = {
            'JOUEUR1': {
                'HAUT': pygame.K_w,
                'BAS': pygame.K_s,
                'GAUCHE': pygame.K_a,
                'DROITE': pygame.K_d
            },
            'JOUEUR2': {
                'HAUT': pygame.K_UP,
                'BAS': pygame.K_DOWN,
                'GAUCHE': pygame.K_LEFT,
                'DROITE': pygame.K_RIGHT
            },
            'SERVICE': pygame.K_SPACE,
            'REINITIALISER': pygame.K_r
        }

        ETATS_JEU = {
            'PRET_A_SERVIR': 'pret_a_servir',
            'SERVICE_COMMENCE': 'service_commence',
            'ECHANGE': 'echange',
            'POINT_TERMINE': 'point_termine',
            'JEU_TERMINE': 'jeu_termine',
            'MATCH_TERMINE': 'match_termine'
        }

        MODES_JEU = {
            'SIMPLE': 'simple'
        }

        COULEURS_NIVEAU = [
            (0, 0, 255),      # Débutant
            (0, 255, 0),      # Intermédiaire
            (255, 165, 0),    # Expert
            (255, 0, 0)       # Maître
        ]

        regles = {
            'LARGEUR_FENETRE': 800,
            'HAUTEUR_FENETRE': 600,
            'TITRE_FENETRE': "Tennis de Table",
            'IPS': 60,
            'POINTS_POUR_GAGNER': 11,
            'DIFFERENCE_POINTS_MIN': 2,
            'JEUX_POUR_GAGNER_MATCH': 4,
            'TOTAL_JEUX_POSSIBLES': 7,
            'SERVICES_PAR_TOUR': 2,
            'CHANGEMENT_SERVICE_POINTS': 2,
            'DELAI_ENTRE_IMPACTS': 100,
            'LARGEUR_TABLE': 60,
            'POSITION_FILET': 50,
            'LARGEUR_TABLE_PIXELS': 480,
            'HAUTEUR_TABLE': 300,
            'TABLE_X': 160,
            'TABLE_Y': 150,
            'LARGEUR_RAQUETTE': 60,
            'HAUTEUR_RAQUETTE': 100,
            'VITESSE_RAQUETTE': 10,
            'RAYON_BALLE': 7,
            'VITESSE_BALLE_MIN': 7.0,
            'VITESSE_BALLE_MAX': 18.0,
            'TAILLE_POLICE_PRINCIPALE': 48,
            'TAILLE_POLICE_SECONDAIRE': 32,
            'TAILLE_POLICE_STANDARD': 36,
            'TAILLE_POLICE_ALERTE': 48,
            'DUREE_ALERTE': 2000,
            'DIFFICULTE_MIN': 1,
            'DIFFICULTE_MAX': 10,
            'LARGEUR_CURSEUR_DIFFICULTE': 400,
            'HAUTEUR_CURSEUR_DIFFICULTE': 8,
            'RAYON_POIGNEE_DIFFICULTE': 12,
            'BLANC': (255, 255, 255),
            'NOIR': (0, 0, 0),
            'GRIS': (64, 64, 66),
            'VERT': (0, 164, 0),
            'JAUNE': (255, 255, 0),
            'ROUGE': (255, 0, 0),
            'CURSEUR_ARRIERE_PLAN': (100, 100, 100),
            'CURSEUR_REMPLISSAGE': (150, 150, 150),
            'CONTROLES': CONTROLES,
            'ETATS_JEU': ETATS_JEU,
            'MODES_JEU': MODES_JEU,
            'COULEURS_NIVEAU': COULEURS_NIVEAU
        }
        
        logger.debug("Règles créées avec succès")
        return regles
    except Exception as e:
        logger.error(f"Erreur lors de la création des règles: {e}", exc_info=True)
        raise

def est_avantage(regles, score1, score2):
    try:
        return score1 >= 10 and score2 >= 10
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'avantage: {e}", exc_info=True)
        return False

def est_gagnant_jeu(regles, score1, score2):
    try:
        if max(score1, score2) >= regles['POINTS_POUR_GAGNER']:
            if abs(score1 - score2) >= regles['DIFFERENCE_POINTS_MIN']:
                return 1 if score1 > score2 else 2
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du gagnant du jeu: {e}", exc_info=True)
        return None

def est_gagnant_match(regles, jeux1, jeux2):
    try:
        if jeux1 >= regles['JEUX_POUR_GAGNER_MATCH']:
            return 1
        elif jeux2 >= regles['JEUX_POUR_GAGNER_MATCH']:
            return 2
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du gagnant du match: {e}", exc_info=True)
        return None

def obtenir_vitesse_balle_pour_niveau(regles, niveau):
    try:
        ratio = (niveau - regles['DIFFICULTE_MIN']) / (regles['DIFFICULTE_MAX'] - regles['DIFFICULTE_MIN'])
        return regles['VITESSE_BALLE_MIN'] + (regles['VITESSE_BALLE_MAX'] - regles['VITESSE_BALLE_MIN']) * ratio
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la vitesse de balle: {e}", exc_info=True)
        return regles['VITESSE_BALLE_MIN']

def obtenir_nom_niveau(regles, niveau):
    try:
        if niveau <= 3:
            return "Débutant"
        elif niveau <= 6:
            return "Intermédiaire"
        elif niveau <= 9:
            return "Expert"
        else:
            return "Maître"
    except Exception as e:
        logger.error(f"Erreur lors de l'obtention du nom du niveau: {e}", exc_info=True)
        return "Débutant"
