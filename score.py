import logging
from regles_tennis_table import creer_regles, est_avantage, est_gagnant_jeu, est_gagnant_match

logger = logging.getLogger('tennis_table')

def creer_score():
    try:
        logger.debug("Création d'un nouveau score")
        score = {
            'regles': creer_regles(),
            'score_joueur1': 0,
            'score_joueur2': 0,
            'jeux_joueur1': 0,
            'jeux_joueur2': 0,
            'est_avantage': False,
            'gagnant_jeu': None,
            'gagnant_match': None
        }
        logger.debug(f"Score créé: {score}")
        return score
    except Exception as e:
        logger.error(f"Erreur lors de la création du score: {e}", exc_info=True)
        raise

def incrementer_joueur1(score):
    try:
        logger.debug(f"Incrémentation score joueur 1: {score['score_joueur1']} -> {score['score_joueur1'] + 1}")
        nouveau_score = {
            **score,
            'score_joueur1': score['score_joueur1'] + 1
        }
        return verifier_progression(nouveau_score)
    except Exception as e:
        logger.error(f"Erreur lors de l'incrémentation du score joueur 1: {e}", exc_info=True)
        return score

def incrementer_joueur2(score):
    try:
        logger.debug(f"Incrémentation score joueur 2: {score['score_joueur2']} -> {score['score_joueur2'] + 1}")
        nouveau_score = {
            **score,
            'score_joueur2': score['score_joueur2'] + 1
        }
        return verifier_progression(nouveau_score)
    except Exception as e:
        logger.error(f"Erreur lors de l'incrémentation du score joueur 2: {e}", exc_info=True)
        return score

def verifier_progression(score):
    try:
        nouveau_score = verifier_avantage(score)
        return verifier_gagnant(nouveau_score)
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la progression: {e}", exc_info=True)
        return score

def verifier_avantage(score):
    try:
        avantage = est_avantage(score['regles'], score['score_joueur1'], score['score_joueur2'])
        difference = abs(score['score_joueur1'] - score['score_joueur2'])
        
        nouveau_score = {
            **score,
            'est_avantage': avantage,
            'avantage_joueur': (1 if score['score_joueur1'] > score['score_joueur2']
                               else 2 if score['score_joueur2'] > score['score_joueur1']
                               else None) if avantage and difference == 1 else None
        }
        
        if nouveau_score['est_avantage']:
            logger.debug(f"Avantage détecté pour joueur {nouveau_score['avantage_joueur']}")
            
        return nouveau_score
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'avantage: {e}", exc_info=True)
        return score

def verifier_gagnant(score):
    try:
        if score['gagnant_jeu'] is None:
            gagnant = est_gagnant_jeu(
                score['regles'],
                score['score_joueur1'],
                score['score_joueur2']
            )
            if gagnant:
                logger.debug(f"Gagnant détecté: Joueur {gagnant}")
                return gerer_victoire_jeu(score, gagnant)
        return score
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du gagnant: {e}", exc_info=True)
        return score

def gerer_victoire_jeu(score, gagnant):
    try:
        logger.debug(f"Gestion de la victoire du jeu pour le joueur {gagnant}")
        nouveau_score = {
            **score,
            'gagnant_jeu': gagnant,
            'jeux_joueur1': score['jeux_joueur1'] + (1 if gagnant == 1 else 0),
            'jeux_joueur2': score['jeux_joueur2'] + (1 if gagnant == 2 else 0)
        }

        nouveau_score['gagnant_match'] = est_gagnant_match(
            score['regles'],
            nouveau_score['jeux_joueur1'],
            nouveau_score['jeux_joueur2']
        )
        
        if nouveau_score['gagnant_match']:
            logger.debug(f"Match gagné par le joueur {nouveau_score['gagnant_match']}")

        return nouveau_score
    except Exception as e:
        logger.error(f"Erreur lors de la gestion de la victoire: {e}", exc_info=True)
        return score

def obtenir_etat_jeu(score):
    try:
        logger.debug("Récupération de l'état du jeu")
        return {
            'score': (score['score_joueur1'], score['score_joueur2']),
            'jeux': (score['jeux_joueur1'], score['jeux_joueur2']),
            'est_avantage': score['est_avantage'],
            'gagnant_jeu': score['gagnant_jeu'],
            'gagnant_match': score['gagnant_match'],
            'etat': (score['regles']['ETATS_JEU']['JEU_TERMINE'] if score['gagnant_jeu'] 
                    else score['regles']['ETATS_JEU']['MATCH_TERMINE'] if score['gagnant_match'] 
                    else score['regles']['ETATS_JEU']['ECHANGE'])
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'obtention de l'état du jeu: {e}", exc_info=True)
        return None

def obtenir_affichage_score(score):
    try:
        score_jeu = f"{score['score_joueur1']}-{score['score_joueur2']}"
        score_match = f"Jeux: {score['jeux_joueur1']}-{score['jeux_joueur2']}"
        
        if score['est_avantage']:
            score_jeu += " AVANTAGE"
        
        logger.debug(f"Affichage du score: {score_jeu}, {score_match}")
        return score_jeu, score_match
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'affichage du score: {e}", exc_info=True)
        return "0-0", "Jeux: 0-0"

def commencer_nouveau_jeu(score):
    try:
        logger.debug("Démarrage d'un nouveau jeu")
        return {
            **score,
            'score_joueur1': 0,
            'score_joueur2': 0,
            'est_avantage': False,
            'gagnant_jeu': None,
            'dernier_point': None,
            'service_change': True
        }
    except Exception as e:
        logger.error(f"Erreur lors du démarrage d'un nouveau jeu: {e}", exc_info=True)
        return score

def reinitialiser(score):
    try:
        logger.debug("Réinitialisation complète du score")
        return {
            **score,
            'score_joueur1': 0,
            'score_joueur2': 0,
            'jeux_joueur1': 0,
            'jeux_joueur2': 0,
            'est_avantage': False,
            'gagnant_jeu': None,
            'gagnant_match': None
        }
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation du score: {e}", exc_info=True)
        return score