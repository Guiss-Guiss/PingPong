import pygame
import logging
from regles_tennis_table import creer_regles

logger = logging.getLogger('tennis_table')

def creer_tableau_score(largeur_ecran):
    try:
        logger.debug("Création du tableau de score")
        regles = creer_regles()
        
        tableau = {
            'regles': regles,
            'largeur_ecran': largeur_ecran,
            'polices': {
                'principale': pygame.font.Font(None, regles['TAILLE_POLICE_PRINCIPALE']),
                'secondaire': pygame.font.Font(None, regles['TAILLE_POLICE_SECONDAIRE'])
            }
        }
        logger.debug(f"Tableau de score créé: {tableau}")
        return tableau
    except Exception as e:
        logger.error(f"Erreur lors de la création du tableau de score: {e}", exc_info=True)
        raise

def dessiner(tableau, ecran, donnees_jeu):
    try:
        elements_a_dessiner = []
        centre_x = tableau['largeur_ecran'] // 2
        
        try:
            texte_score = f"{donnees_jeu['score_joueur1']} - {donnees_jeu['score_joueur2']}"
            surface_score = tableau['polices']['principale'].render(
                texte_score,
                True,
                tableau['regles']['BLANC']
            )
            elements_a_dessiner.append((surface_score, (centre_x, tableau['regles']['TABLE_Y'] - 80)))

            texte_jeux = f"Jeux : {donnees_jeu['jeux_joueur1']} - {donnees_jeu['jeux_joueur2']}"
            surface_jeux = tableau['polices']['secondaire'].render(
                texte_jeux,
                True,
                tableau['regles']['GRIS']
            )
            elements_a_dessiner.append((surface_jeux, (centre_x, tableau['regles']['TABLE_Y'] - 120)))

            if donnees_jeu.get('message_statut') == tableau['regles']['ETATS_JEU']['MATCH_TERMINE']:
                gagnant = "1" if donnees_jeu['jeux_joueur1'] > donnees_jeu['jeux_joueur2'] else "2"
                texte_fin = f"Gagnant Joueur {gagnant} (appuyez sur r pour recommencer, q pour quitter)"
                surface_fin = tableau['polices']['secondaire'].render(
                    texte_fin,
                    True,
                    tableau['regles']['JAUNE']
                )
                elements_a_dessiner.append((surface_fin, (centre_x, tableau['regles']['TABLE_Y'] - 40)))
            elif donnees_jeu.get('serveur_actuel'):
                texte_serveur = f"Joueur {donnees_jeu['serveur_actuel']} au service"
                if donnees_jeu.get('en_service'):
                    touches = pygame.key.name(tableau['regles']['CONTROLES']['SERVICE'])
                    texte_serveur += f" (Appuyez sur {touches})"
                
                surface_serveur = tableau['polices']['secondaire'].render(
                    texte_serveur,
                    True,
                    tableau['regles']['JAUNE']
                )
                elements_a_dessiner.append((surface_serveur, (centre_x, tableau['regles']['TABLE_Y'] - 40)))

            for surface, position in elements_a_dessiner:
                rect = surface.get_rect(center=position)
                ecran.blit(surface, rect)
                
        except Exception as e:
            logger.error(f"Erreur lors du rendu des éléments: {e}")
            
    except Exception as e:
        logger.error(f"Erreur lors du dessin du tableau de score: {e}", exc_info=True)
        
def construire_texte_score(donnees_jeu):
    try:
        if donnees_jeu.get('est_avantage'):
            if donnees_jeu.get('avantage_joueur'):
                return f"Avantage Joueur {donnees_jeu['avantage_joueur']}"
            return "Égalité"
        return f"{donnees_jeu['score_joueur1']} - {donnees_jeu['score_joueur2']}"
    except Exception as e:
        logger.error(f"Erreur lors de la construction du texte score: {e}", exc_info=True)
        return "0 - 0"

def construire_texte_service(donnees_jeu, regles):
    try:
        texte = f"Joueur {donnees_jeu['serveur_actuel']} au service"
        if donnees_jeu.get('en_service'):
            touches = pygame.key.name(regles['CONTROLES']['SERVICE'])
            texte += f" (Appuyez sur {touches})"
        if donnees_jeu.get('services_restants'):
            texte += f" - {donnees_jeu['services_restants']} service(s) restant(s)"
        return texte
    except Exception as e:
        logger.error(f"Erreur lors de la construction du texte service: {e}", exc_info=True)
        return "Service"

def formater_message_statut(message):
    try:
        return message.replace('_', ' ').title()
    except Exception as e:
        logger.error(f"Erreur lors du formatage du message: {e}", exc_info=True)
        return message

def obtenir_couleur_statut(statut, regles):
    try:
        couleurs_statut = {
            'POINT_TERMINE': regles['JAUNE'],
            'JEU_TERMINE': regles['VERT'],
            'MATCH_TERMINE': regles['ROUGE'],
            'PRET_A_SERVIR': regles['BLANC']
        }
        return couleurs_statut.get(statut, regles['BLANC'])
    except Exception as e:
        logger.error(f"Erreur lors de l'obtention de la couleur du statut: {e}", exc_info=True)
        return regles['BLANC']

def dessiner_animation_point(tableau, ecran, donnees_jeu):
    try:
        temps_actuel = pygame.time.get_ticks()
        if temps_actuel - donnees_jeu.get('temps_point_marque', 0) < 1000:
            alpha = int(255 * (1 - (temps_actuel - donnees_jeu['temps_point_marque']) / 1000))
            surface_point = tableau['polices']['principale'].render(
                "Point !",
                True,
                tableau['regles']['JAUNE']
            )
            surface_point.set_alpha(alpha)
            rect_point = surface_point.get_rect(center=(tableau['largeur_ecran'] // 2, 200))
            ecran.blit(surface_point, rect_point)
    except Exception as e:
        logger.error(f"Erreur lors du dessin de l'animation de point: {e}", exc_info=True)
        
def dessiner_fin_jeu(tableau, ecran, gagnant, match_termine=False):
    try:
        elements_a_dessiner = []
        
        message = f"Le joueur {gagnant} gagne le {'match' if match_termine else 'jeu'} !"
        
        surface_texte = tableau['polices']['principale'].render(
            message,
            True,
            tableau['regles']['JAUNE']
        )
        elements_a_dessiner.append(
            (surface_texte, (tableau['largeur_ecran'] // 2, tableau['largeur_ecran'] // 4))
        )
        
        texte_redemarrer = f"Appuyez sur {pygame.key.name(tableau['regles']['CONTROLES']['REINITIALISER'])} pour redémarrer"
        surface_redemarrer = tableau['polices']['secondaire'].render(
            texte_redemarrer,
            True,
            tableau['regles']['BLANC']
        )
        elements_a_dessiner.append(
            (surface_redemarrer, (tableau['largeur_ecran'] // 2, tableau['largeur_ecran'] // 4 + 40))
        )
        
        for surface, position in elements_a_dessiner:
            rect = surface.get_rect(center=position)
            ecran.blit(surface, rect)
            
    except Exception as e:
        logger.error(f"Erreur lors du dessin de fin de jeu: {e}", exc_info=True)