import pygame
import logging
from regles_tennis_table import creer_regles, est_avantage, est_gagnant_jeu, est_gagnant_match

logger = logging.getLogger('tennis_table')

def creer_gestionnaire_match():
    logger.debug("Création d'un nouveau gestionnaire de match")
    regles = creer_regles()
    gestionnaire = {
        'regles': regles,
        'score_jeu_actuel1': 0,
        'score_jeu_actuel2': 0,
        'jeux_joueur1': 0,
        'jeux_joueur2': 0,
        'match_termine': False,
        'gagnant_match': None,
        'etat': regles['ETATS_JEU']['PRET_A_SERVIR'],
        'historique_jeux': [],
        'jeu_actuel': 1
    }
    logger.debug(f"Gestionnaire créé: {gestionnaire}")
    return gestionnaire

def commencer_nouveau_jeu(gestionnaire):
    logger.debug("Démarrage d'un nouveau jeu")
    regles = gestionnaire['regles']
    nouveau_jeu = {
        'score_joueur1': 0,
        'score_joueur2': 0,
        'jeux_joueur1': 0,
        'jeux_joueur2': 0,
        'etat': regles['ETATS_JEU']['PRET_A_SERVIR']
    }
    logger.debug(f"Nouveau jeu créé: {nouveau_jeu}")
    return nouveau_jeu

def mettre_a_jour_score(gestionnaire, score1, score2):
    logger.debug(f"Mise à jour du score: {score1}-{score2}")
    ancien_etat = gestionnaire['etat']
    nouveau_gestionnaire = {
        **gestionnaire,
        'score_jeu_actuel1': score1,
        'score_jeu_actuel2': score2,
        'dernier_changement': pygame.time.get_ticks()
    }
    
    if est_gagnant_jeu(nouveau_gestionnaire['regles'], score1, score2):
        logger.debug("Jeu terminé détecté")
        nouveau_gestionnaire['etat'] = nouveau_gestionnaire['regles']['ETATS_JEU']['JEU_TERMINE']
        nouveau_gestionnaire['delai_prochain_jeu'] = pygame.time.get_ticks() + 2000
    elif est_avantage(nouveau_gestionnaire['regles'], score1, score2):
        logger.debug("Avantage détecté")
        nouveau_gestionnaire['etat'] = nouveau_gestionnaire['regles']['ETATS_JEU']['AVANTAGE']
    
    if ancien_etat != nouveau_gestionnaire['etat']:
        logger.debug(f"Changement d'état: {ancien_etat} -> {nouveau_gestionnaire['etat']}")
        nouveau_gestionnaire['changement_etat'] = True
    
    return nouveau_gestionnaire

def incrementer_jeux_joueur(gestionnaire, joueur, score_final):
    logger.debug(f"Incrémentation des jeux pour joueur {joueur}, score final: {score_final}")
    nouveau_gestionnaire = {
        **gestionnaire,
        'historique_jeux': [*gestionnaire['historique_jeux'], score_final],
        'etat': gestionnaire['regles']['ETATS_JEU']['JEU_TERMINE']
    }
    
    if joueur == 1:
        nouveau_gestionnaire['jeux_joueur1'] = gestionnaire['jeux_joueur1'] + 1
        logger.debug(f"Jeux joueur 1: {nouveau_gestionnaire['jeux_joueur1']}")
    else:
        nouveau_gestionnaire['jeux_joueur2'] = gestionnaire['jeux_joueur2'] + 1
        logger.debug(f"Jeux joueur 2: {nouveau_gestionnaire['jeux_joueur2']}")
            
    gagnant_match = est_gagnant_match(
        nouveau_gestionnaire['regles'],
        nouveau_gestionnaire['jeux_joueur1'], 
        nouveau_gestionnaire['jeux_joueur2'])
        
    if gagnant_match:
        logger.debug(f"Match terminé, gagnant: Joueur {gagnant_match}")
        nouveau_gestionnaire['match_termine'] = True
        nouveau_gestionnaire['gagnant_match'] = gagnant_match
        nouveau_gestionnaire['etat'] = nouveau_gestionnaire['regles']['ETATS_JEU']['MATCH_TERMINE']
    else:
        logger.debug("Passage au jeu suivant")
        nouveau_gestionnaire['jeu_actuel'] = gestionnaire['jeu_actuel'] + 1
        nouveau_gestionnaire['etat'] = nouveau_gestionnaire['regles']['ETATS_JEU']['PRET_A_SERVIR']
    
    return nouveau_gestionnaire

def verifier_progression_jeu(gestionnaire):
    logger.debug("Vérification de la progression du jeu")
    gagnant = est_gagnant_jeu(
        gestionnaire['regles'],
        gestionnaire['score_jeu_actuel1'], 
        gestionnaire['score_jeu_actuel2'])
    logger.debug(f"Gagnant trouvé: {gagnant}")
    return gagnant

def obtenir_statistiques_match(gestionnaire):
    logger.debug("Récupération des statistiques du match")
    try:
        total_points_j1 = sum(jeu[0] for jeu in gestionnaire['historique_jeux'])
        total_points_j2 = sum(jeu[1] for jeu in gestionnaire['historique_jeux'])
        
        stats = {
            'jeux_joues': len(gestionnaire['historique_jeux']),
            'jeux_joueur1': gestionnaire['jeux_joueur1'],
            'jeux_joueur2': gestionnaire['jeux_joueur2'],
            'points_totaux_joueur1': total_points_j1,
            'points_totaux_joueur2': total_points_j2,
            'historique_jeux': gestionnaire['historique_jeux'],
            'match_termine': gestionnaire['match_termine'],
            'gagnant_match': gestionnaire['gagnant_match'],
            'jeu_actuel': gestionnaire['jeu_actuel'],
            'total_jeux_possibles': gestionnaire['regles']['TOTAL_JEUX_POSSIBLES'],
            'etat': gestionnaire['etat']
        }
        logger.debug(f"Statistiques calculées: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Erreur lors du calcul des statistiques: {e}")
        return None

def reinitialiser(gestionnaire):
    logger.debug("Réinitialisation du gestionnaire de match")
    return creer_gestionnaire_match()