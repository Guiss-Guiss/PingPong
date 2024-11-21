import pygame
import logging
from regles_tennis_table import creer_regles

logger = logging.getLogger('tennis_table')

def creer_statut_jeu(largeur_ecran):
    try:
        logger.debug("Création du gestionnaire de statut")
        regles = creer_regles()
        
        statut = {
            'regles': regles,
            'largeur_ecran': largeur_ecran,
            'statut_jeu': "Préparez-vous !",
            'statut_match': "",
            'message_alerte': "",
            'minuteur_alerte': 0,
            'polices': {
                'principale': pygame.font.Font(None, regles['TAILLE_POLICE_STANDARD']),
                'alerte': pygame.font.Font(None, regles['TAILLE_POLICE_ALERTE'])
            }
        }
        logger.debug(f"Statut créé: {statut}")
        return statut
    except Exception as e:
        logger.error(f"Erreur lors de la création du statut: {e}", exc_info=True)
        raise

def mettre_a_jour(statut, etat_jeu):
    try:
        logger.debug("Mise à jour du statut")
        nouveau_statut = {**statut}
        
        if etat_jeu.get('service', False):
            nouveau_statut['statut_jeu'] = f"Joueur {etat_jeu['serveur']} au service"
        elif etat_jeu.get('point_marque'):
            nouveau_statut = afficher_alerte(
                nouveau_statut,
                f"Point pour le Joueur {etat_jeu['gagnant_point']} !"
            )
        elif etat_jeu.get('jeu_termine'):
            nouveau_statut['statut_jeu'] = f"Joueur {etat_jeu['gagnant']} gagne le jeu !"
        elif etat_jeu.get('let_service'):
            nouveau_statut = afficher_alerte(nouveau_statut, "Let Service !")
        else:
            nouveau_statut['statut_jeu'] = statut['regles']['ETATS_JEU']['ECHANGE']
        
        return nouveau_statut
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du statut: {e}", exc_info=True)
        return statut

def mettre_a_jour_match(statut, etat_match):
    try:
        if etat_match.get('match_termine'):
            return {
                **statut,
                'statut_match': f"Joueur {etat_match['gagnant']} gagne le match !"
            }
        else:
            jeux = etat_match.get('jeux', (0, 0))
            return {
                **statut,
                'statut_match': f"Jeux : {jeux[0]} - {jeux[1]}"
            }
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du match: {e}", exc_info=True)
        return statut

def afficher_alerte(statut, message):
    try:
        logger.debug(f"Affichage alerte: {message}")
        return {
            **statut,
            'message_alerte': message,
            'minuteur_alerte': pygame.time.get_ticks()
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage de l'alerte: {e}", exc_info=True)
        return statut

def dessiner(statut, ecran):
    try:
        elements_a_dessiner = []
        
        if statut['statut_jeu']:
            texte = statut['polices']['principale'].render(
                statut['statut_jeu'],
                True,
                statut['regles']['BLANC']
            )
            elements_a_dessiner.append((texte, (statut['largeur_ecran'] // 2, 30)))
        
        if statut['statut_match']:
            texte = statut['polices']['principale'].render(
                statut['statut_match'],
                True,
                statut['regles']['BLANC']
            )
            elements_a_dessiner.append((texte, (statut['largeur_ecran'] // 2, 60)))
        
        temps_actuel = pygame.time.get_ticks()
        if (statut['message_alerte'] and 
            temps_actuel - statut['minuteur_alerte'] < statut['regles']['DUREE_ALERTE']):
            texte = statut['polices']['alerte'].render(
                statut['message_alerte'],
                True,
                statut['regles']['JAUNE']
            )
            elements_a_dessiner.append((texte, (statut['largeur_ecran'] // 2, 100)))
        
        for texte, position in elements_a_dessiner:
            rect = texte.get_rect(center=position)
            ecran.blit(texte, rect)
    except Exception as e:
        logger.error(f"Erreur lors du dessin du statut: {e}", exc_info=True)

def afficher_controles(statut, ecran):
    try:
        controles = [
            "Contrôles :",
            f"Joueur 1 : {pygame.key.name(statut['regles']['CONTROLES']['JOUEUR1']['HAUT'])}/"
            f"{pygame.key.name(statut['regles']['CONTROLES']['JOUEUR1']['BAS'])} pour bouger",
            f"Joueur 2 : {pygame.key.name(statut['regles']['CONTROLES']['JOUEUR2']['HAUT'])}/"
            f"{pygame.key.name(statut['regles']['CONTROLES']['JOUEUR2']['BAS'])} pour bouger",
            f"Appuyez sur {pygame.key.name(statut['regles']['CONTROLES']['SERVICE'])} pour servir",
            f"Appuyez sur {pygame.key.name(statut['regles']['CONTROLES']['REINITIALISER'])} pour redémarrer le jeu"
        ]
        
        position_y = 150
        for ligne in controles:
            texte = statut['polices']['principale'].render(ligne, True, statut['regles']['BLANC'])
            rect_texte = texte.get_rect(center=(statut['largeur_ecran'] // 2, position_y))
            ecran.blit(texte, rect_texte)
            position_y += 30
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage des contrôles: {e}", exc_info=True)

def afficher_menu_pause(statut, ecran):
    try:
        overlay = pygame.Surface((statut['largeur_ecran'], ecran.get_height()))
        overlay.fill(statut['regles']['NOIR'])
        overlay.set_alpha(128)
        ecran.blit(overlay, (0, 0))
        
        messages = [
            ("JEU EN PAUSE", statut['polices']['alerte'], statut['regles']['JAUNE']),
            ("Appuyez sur P pour reprendre", statut['polices']['principale'], statut['regles']['BLANC']),
            (f"Appuyez sur {pygame.key.name(statut['regles']['CONTROLES']['REINITIALISER'])} pour redémarrer",
             statut['polices']['principale'], statut['regles']['BLANC']),
            ("Appuyez sur ESC pour quitter", statut['polices']['principale'], statut['regles']['BLANC'])
        ]
        
        position_y = ecran.get_height() // 3
        for message, police, couleur in messages:
            texte = police.render(message, True, couleur)
            rect_texte = texte.get_rect(center=(statut['largeur_ecran'] // 2, position_y))
            ecran.blit(texte, rect_texte)
            position_y += 50
    except Exception as e:
        logger.error(f"Erreur lors de l'affichage du menu pause: {e}", exc_info=True)