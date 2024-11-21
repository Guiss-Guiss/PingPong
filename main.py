import pygame
import sys
import os
import math
import logging
from logging_config import configurer_logging
configurer_logging()

logger = logging.getLogger('tennis_table')

from raquette import (
    creer_raquette, 
    deplacer as deplacer_raquette,
    definir_velocite, 
    reinitialiser_position,
    verifier_collision_balle,
    dessiner as dessiner_raquette
)
from balle import (
    creer_balle,
    definir_sons,
    reinitialiser as reinitialiser_balle,
    servir,
    deplacer as deplacer_balle,
    gerer_collision_raquette,
    dessiner as dessiner_balle
)
from score import (
    creer_score,
    incrementer_joueur1,
    incrementer_joueur2,
    reinitialiser as reinitialiser_score
)
from tableau_score import (
    creer_tableau_score,
    dessiner as dessiner_tableau_score
)
from selecteur_difficulte import (
    creer_selecteur_difficulte,
    gerer_evenement,
    dessiner as dessiner_selecteur
)
from gestionnaire_match import (
    creer_gestionnaire_match,
    incrementer_jeux_joueur,
    reinitialiser as reinitialiser_match
)
from gestionnaire_service import (
    creer_gestionnaire_service,
    mettre_a_jour_compte_service
)
from regles_tennis_table import creer_regles

def initialiser_jeu():
    try:
        logger.info("Initialisation du jeu")
        pygame.init()
        pygame.mixer.init()
        
        regles = creer_regles()
        ecran = pygame.display.set_mode((regles['LARGEUR_FENETRE'], regles['HAUTEUR_FENETRE']))
        pygame.display.set_caption(regles['TITRE_FENETRE'])
        
        return {
            'regles': regles,
            'ecran': ecran,
            'horloge': pygame.time.Clock(),
            'en_cours': True,
            'ressources': charger_ressources(),
            'etat_jeu': None,
            'pause': False
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du jeu: {e}", exc_info=True)
        return None

def charger_ressources():
    try:
        logger.info("Chargement des ressources")
        ressources = {'sons': {}, 'images': {}}
        
        try:
            ressources['sons'].update({
                'coup_gauche': pygame.mixer.Sound(os.path.join('sons', 'coup_gauche.mp3')),
                'coup_droit': pygame.mixer.Sound(os.path.join('sons', 'coup_droit.mp3')),
                'service': pygame.mixer.Sound(os.path.join('sons', 'service.mp3'))
            })
        except Exception as e:
            logger.warning(f"Impossible de charger les sons: {e}")
        
        try:
            arriere_plan = pygame.image.load(os.path.join('images', 'plancher.jpg'))
            raquette_bleue = pygame.image.load(os.path.join('images', 'raquette_bleue.png'))
            raquette_rouge = pygame.image.load(os.path.join('images', 'raquette_rouge.png'))
            
            ressources['images'].update({
                'arriere_plan': pygame.transform.scale(arriere_plan, (800, 600)),
                'raquette_bleue': pygame.transform.scale(raquette_bleue, (60, 100)),
                'raquette_rouge': pygame.transform.scale(raquette_rouge, (60, 100))
            })
        except Exception as e:
            logger.warning(f"Impossible de charger les images: {e}")
        
        return ressources
    except Exception as e:
        logger.error(f"Erreur lors du chargement des ressources: {e}", exc_info=True)
        return {'sons': {}, 'images': {}}

def initialiser_objets_jeu(vitesse_balle, ressources, regles):
    try:
        logger.debug(f"Initialisation des objets avec vitesse_balle={vitesse_balle}")
        
        raquette_rouge = creer_raquette(
            x=regles['TABLE_X'] - regles['LARGEUR_RAQUETTE'] - 10,
            y=regles['HAUTEUR_FENETRE'] // 2 - regles['HAUTEUR_RAQUETTE'] // 2,
            vitesse=regles['VITESSE_RAQUETTE'],
            image=ressources['images'].get('raquette_rouge')
        )
        
        raquette_bleue = creer_raquette(
            x=regles['TABLE_X'] + regles['LARGEUR_TABLE_PIXELS'] + 10,
            y=regles['HAUTEUR_FENETRE'] // 2 - regles['HAUTEUR_RAQUETTE'] // 2,
            vitesse=regles['VITESSE_RAQUETTE'],
            image=ressources['images'].get('raquette_bleue')
        )
        
        balle = creer_balle(vitesse=vitesse_balle)
        balle = definir_sons(
            balle,
            ressources['sons'].get('coup_gauche'),
            ressources['sons'].get('coup_droit'),
            ressources['sons'].get('service')
        )

        score = creer_score()
        gestionnaire_service = creer_gestionnaire_service()
        gestionnaire_match = creer_gestionnaire_match()
        tableau_score = creer_tableau_score(regles['LARGEUR_FENETRE'])

        return {
            'raquette_rouge': raquette_rouge,
            'raquette_bleue': raquette_bleue,
            'balle': balle,
            'score': score,
            'gestionnaire_service': gestionnaire_service,
            'gestionnaire_match': gestionnaire_match,
            'tableau_score': tableau_score,
            'regles': regles
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des objets: {e}", exc_info=True)
        return None

def gerer_entree(touches, raquette_rouge, raquette_bleue, regles):
    try:
        dx1 = dy1 = 0
        if touches[regles['CONTROLES']['JOUEUR1']['HAUT']]: dy1 = -1
        if touches[regles['CONTROLES']['JOUEUR1']['BAS']]: dy1 = 1
        if touches[regles['CONTROLES']['JOUEUR1']['GAUCHE']]: dx1 = -1
        if touches[regles['CONTROLES']['JOUEUR1']['DROITE']]: dx1 = 1
        raquette_rouge = definir_velocite(raquette_rouge, dx1, dy1)

        dx2 = dy2 = 0
        if touches[regles['CONTROLES']['JOUEUR2']['HAUT']]: dy2 = -1
        if touches[regles['CONTROLES']['JOUEUR2']['BAS']]: dy2 = 1
        if touches[regles['CONTROLES']['JOUEUR2']['GAUCHE']]: dx2 = -1
        if touches[regles['CONTROLES']['JOUEUR2']['DROITE']]: dx2 = 1
        raquette_bleue = definir_velocite(raquette_bleue, dx2, dy2)

        return (raquette_rouge, raquette_bleue, touches[regles['CONTROLES']['SERVICE']])
    except Exception as e:
        logger.error(f"Erreur lors de la gestion des entrées: {e}", exc_info=True)
        return raquette_rouge, raquette_bleue, False

def gerer_balle(balle, raquette_rouge, raquette_bleue, espace_presse, temps_actuel, gestionnaire_service):
    try:
        if balle['au_service'] and espace_presse:
            if balle['son_service']:
                try:
                    balle['son_service'].play()
                except Exception as e:
                    logger.warning(f"Erreur lors de la lecture du son de service: {e}")
                
            nouvelle_balle = servir(balle, gestionnaire_service['serveur_actuel'])
            nouvelle_balle['au_service'] = False
            nouvelle_balle['etat'] = balle['regles']['ETATS_JEU']['SERVICE_COMMENCE']
            
            angle = math.atan2(nouvelle_balle['cible_y'] - nouvelle_balle['y'], 
                            nouvelle_balle['cible_x'] - nouvelle_balle['x'])
            nouvelle_balle['dx'] = math.cos(angle) * nouvelle_balle['vitesse']
            nouvelle_balle['dy'] = math.sin(angle) * nouvelle_balle['vitesse']
            return nouvelle_balle, False

        elif not balle['au_service']:
            nouvelle_balle, point_marque = deplacer_balle(balle)
            if point_marque:
                return nouvelle_balle, True

            for raquette in [raquette_rouge, raquette_bleue]:
                collision, position_impact = verifier_collision_balle(raquette, nouvelle_balle, temps_actuel)
                if collision:
                    nouvelle_balle = gerer_collision_raquette(nouvelle_balle, raquette, position_impact)
                    break

            return nouvelle_balle, False

        return balle, False
    except Exception as e:
        logger.error(f"Erreur lors de la gestion de la balle: {e}", exc_info=True)
        return balle, False

def dessiner_table(ecran, regles):
    try:
        pygame.draw.rect(ecran, regles['VERT'],
            (regles['TABLE_X'], regles['TABLE_Y'],
             regles['LARGEUR_TABLE_PIXELS'], regles['HAUTEUR_TABLE']))
        
        lignes = [
            ((regles['TABLE_X'], regles['TABLE_Y']),
             (regles['TABLE_X'] + regles['LARGEUR_TABLE_PIXELS'], regles['TABLE_Y'])),
            ((regles['TABLE_X'], regles['TABLE_Y'] + regles['HAUTEUR_TABLE']),
             (regles['TABLE_X'] + regles['LARGEUR_TABLE_PIXELS'], 
              regles['TABLE_Y'] + regles['HAUTEUR_TABLE'])),
            ((regles['TABLE_X'], regles['TABLE_Y']),
             (regles['TABLE_X'], regles['TABLE_Y'] + regles['HAUTEUR_TABLE'])),
            ((regles['TABLE_X'] + regles['LARGEUR_TABLE_PIXELS'], regles['TABLE_Y']),
             (regles['TABLE_X'] + regles['LARGEUR_TABLE_PIXELS'], 
              regles['TABLE_Y'] + regles['HAUTEUR_TABLE']))
        ]
        
        for debut, fin in lignes:
            pygame.draw.line(ecran, regles['BLANC'], debut, fin, 2)
        
        centre_x = regles['TABLE_X'] + regles['LARGEUR_TABLE_PIXELS'] / 2
        pygame.draw.line(ecran, regles['BLANC'],
                        (centre_x, regles['TABLE_Y']),
                        (centre_x, regles['TABLE_Y'] + regles['HAUTEUR_TABLE']), 2)
    except Exception as e:
        logger.error(f"Erreur lors du dessin de la table: {e}", exc_info=True)

def dessiner_jeu(ecran, etat_jeu, ressources):
    try:
        ecran.fill(etat_jeu['regles']['NOIR'])
        if ressources['images'].get('arriere_plan'):
            ecran.blit(ressources['images']['arriere_plan'], (0, 0))
        
        dessiner_table(ecran, etat_jeu['regles'])
        
        dessiner_raquette(etat_jeu['raquette_rouge'], ecran)
        dessiner_raquette(etat_jeu['raquette_bleue'], ecran)
        dessiner_balle(etat_jeu['balle'], ecran)
        
        donnees_affichage = {
            'score_joueur1': etat_jeu['score']['score_joueur1'],
            'score_joueur2': etat_jeu['score']['score_joueur2'],
            'jeux_joueur1': etat_jeu['gestionnaire_match']['jeux_joueur1'],
            'jeux_joueur2': etat_jeu['gestionnaire_match']['jeux_joueur2'],
            'serveur_actuel': etat_jeu['gestionnaire_service']['serveur_actuel'],
            'en_service': etat_jeu['balle']['au_service'],
            'message_statut': etat_jeu['gestionnaire_match']['etat'],
            'est_avantage': etat_jeu['score']['est_avantage']
        }
        
        dessiner_tableau_score(etat_jeu['tableau_score'], ecran, donnees_affichage)
    except Exception as e:
        logger.error(f"Erreur lors du dessin du jeu: {e}", exc_info=True)

def nettoyer_ressources(ressources):
    try:
        if ressources:
            for son in ressources.get('sons', {}).values():
                if son:
                    son.stop()
                    son = None
            ressources['sons'].clear()
            ressources['images'].clear()
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des ressources: {e}", exc_info=True)

def mettre_a_jour_jeu(etat_jeu, touches, temps_actuel):
    try:
        nouvel_etat = {**etat_jeu}
        
        raquette_rouge, raquette_bleue, espace_presse = gerer_entree(
            touches, 
            nouvel_etat['raquette_rouge'], 
            nouvel_etat['raquette_bleue'], 
            nouvel_etat['regles']
        )
        
        raquette_rouge = deplacer_raquette(raquette_rouge)
        raquette_bleue = deplacer_raquette(raquette_bleue)
        
        nouvel_etat['balle'], point_marque = gerer_balle(
            nouvel_etat['balle'],
            raquette_rouge,
            raquette_bleue,
            espace_presse,
            temps_actuel,
            nouvel_etat['gestionnaire_service']
        )
        
        if point_marque:
            point_joueur2 = nouvel_etat['balle']['x'] < 0
            if point_joueur2:
                nouvel_etat['score'] = incrementer_joueur2(nouvel_etat['score'])
            else:
                nouvel_etat['score'] = incrementer_joueur1(nouvel_etat['score'])
                
            if nouvel_etat['score']['gagnant_jeu']:
                nouvel_etat['gestionnaire_match'] = incrementer_jeux_joueur(
                    nouvel_etat['gestionnaire_match'],
                    nouvel_etat['score']['gagnant_jeu'],
                    (nouvel_etat['score']['score_joueur1'],
                     nouvel_etat['score']['score_joueur2'])
                )
                nouvel_etat['score'] = reinitialiser_score(nouvel_etat['score'])
                nouvel_etat['gestionnaire_service'] = creer_gestionnaire_service()
            else:
                nouvel_etat['gestionnaire_service'] = mettre_a_jour_compte_service(
                    nouvel_etat['gestionnaire_service'],
                    nouvel_etat['score']['score_joueur1'],
                    nouvel_etat['score']['score_joueur2']
                )
            
            nouvel_etat['balle'] = servir(
                nouvel_etat['balle'],
                nouvel_etat['gestionnaire_service']['serveur_actuel']
            )
            
            nouvel_etat['raquette_rouge'] = reinitialiser_position(raquette_rouge)
            nouvel_etat['raquette_bleue'] = reinitialiser_position(raquette_bleue)
        
        nouvel_etat.update({
            'raquette_rouge': raquette_rouge,
            'raquette_bleue': raquette_bleue,
        })
        
        return nouvel_etat
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du jeu: {e}", exc_info=True)
        return etat_jeu

def boucle_selection_difficulte(etat_global):
    try:
        selecteur = creer_selecteur_difficulte(
            etat_global['regles']['LARGEUR_FENETRE'],
            etat_global['regles']['HAUTEUR_FENETRE']
        )
        selection_difficulte = True
        
        while selection_difficulte and etat_global['en_cours']:
            for evenement in pygame.event.get():
                if evenement.type == pygame.QUIT:
                    etat_global['en_cours'] = False
                    return None
                elif evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_RETURN:
                    selection_difficulte = False
                else:
                    selecteur = gerer_evenement(selecteur, evenement)

            ecran = etat_global['ecran']
            ecran.fill(etat_global['regles']['NOIR'])
            if etat_global['ressources']['images'].get('arriere_plan'):
                ecran.blit(etat_global['ressources']['images']['arriere_plan'], (0, 0))
            
            dessiner_selecteur(selecteur, ecran)
            pygame.display.flip()
            etat_global['horloge'].tick(etat_global['regles']['IPS'])
        
        return selecteur['vitesse_balle'] if etat_global['en_cours'] else None
    except Exception as e:
        logger.error(f"Erreur dans la boucle de sélection de difficulté: {e}", exc_info=True)
        return None

def boucle_principale():
    try:
        etat_global = initialiser_jeu()
        if not etat_global:
            logger.error("Échec de l'initialisation du jeu")
            return
            
        vitesse_balle = boucle_selection_difficulte(etat_global)
        if not vitesse_balle:
            return
            
        etat_global['etat_jeu'] = initialiser_objets_jeu(
            vitesse_balle, 
            etat_global['ressources'],
            etat_global['regles']
        )
        
        while etat_global['en_cours']:
            temps_actuel = pygame.time.get_ticks()
            touches = pygame.key.get_pressed()
            
            try:
                for evenement in pygame.event.get():
                    if evenement.type == pygame.QUIT:
                        etat_global['en_cours'] = False
                    elif evenement.type == pygame.KEYDOWN:
                        if evenement.key == pygame.K_ESCAPE or evenement.key == pygame.K_q:
                            etat_global['en_cours'] = False
                        elif evenement.key == etat_global['regles']['CONTROLES']['REINITIALISER']:
                            if etat_global['etat_jeu']['score']['gagnant_jeu'] or \
                               etat_global['etat_jeu']['gestionnaire_match']['match_termine']:
                                if etat_global['etat_jeu']['gestionnaire_match']['match_termine']:
                                    etat_global['etat_jeu']['gestionnaire_match'] = reinitialiser_match(
                                        etat_global['etat_jeu']['gestionnaire_match'])
                                etat_global['etat_jeu'].update({
                                    'score': reinitialiser_score(etat_global['etat_jeu']['score']),
                                    'balle': reinitialiser_balle(etat_global['etat_jeu']['balle']),
                                    'gestionnaire_service': creer_gestionnaire_service(),
                                    'raquette_rouge': reinitialiser_position(etat_global['etat_jeu']['raquette_rouge']),
                                    'raquette_bleue': reinitialiser_position(etat_global['etat_jeu']['raquette_bleue'])
                                })

                if not etat_global['etat_jeu']['gestionnaire_match']['match_termine']:
                    etat_global['etat_jeu'] = mettre_a_jour_jeu(
                        etat_global['etat_jeu'],
                        touches,
                        temps_actuel
                    )

                dessiner_jeu(
                    etat_global['ecran'],
                    etat_global['etat_jeu'],
                    etat_global['ressources']
                )
                
                pygame.display.flip()
                etat_global['horloge'].tick(etat_global['regles']['IPS'])
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle de jeu: {e}", exc_info=True)
                
    except Exception as e:
        logger.error(f"Erreur fatale dans la boucle principale: {e}", exc_info=True)
    finally:
        nettoyer_ressources(etat_global.get('ressources'))
        pygame.quit()

def main():
    try:
        boucle_principale()
    except Exception as e:
        logger.error(f"Erreur fatale: {e}", exc_info=True)
    finally:
        sys.exit()

if __name__ == "__main__":
    main()