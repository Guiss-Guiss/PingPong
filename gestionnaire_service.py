import random
import time
import logging
from regles_tennis_table import creer_regles, est_avantage

logger = logging.getLogger('tennis_table')

def creer_gestionnaire_service():
    logger.debug("Création d'un nouveau gestionnaire de service")
    regles = creer_regles()
    
    heure_actuelle = time.time()
    random.seed(heure_actuelle)
    serveur_initial = random.choice([1, 2])
    
    gestionnaire = {
        'regles': regles,
        'serveur_actuel': serveur_initial,
        'compte_service': 0,
        'services_par_tour': regles['SERVICES_PAR_TOUR'],
        'est_egalite': False,
        'let_service': False,
        'etat': regles['ETATS_JEU']['PRET_A_SERVIR'],
        'service_depuis_gauche': serveur_initial == 1
    }
    logger.debug(f"Gestionnaire service créé: {gestionnaire}")
    return gestionnaire

def mettre_a_jour_compte_service(gestionnaire, score1, score2):
    logger.debug(f"Mise à jour du compte service pour score {score1}-{score2}")
    nouveau_gestionnaire = {**gestionnaire}
    
    try:
        if est_avantage(gestionnaire['regles'], score1, score2):
            logger.debug("Situation d'avantage détectée")
            if not gestionnaire['est_egalite']:
                nouveau_gestionnaire.update({
                    'est_egalite': True,
                    'services_par_tour': 1,
                    'compte_service': 0
                })
        
        nouveau_gestionnaire['compte_service'] = gestionnaire['compte_service'] + 1
        logger.debug(f"Nouveau compte service: {nouveau_gestionnaire['compte_service']}")
        
        if nouveau_gestionnaire['compte_service'] >= gestionnaire['services_par_tour']:
            logger.debug("Changement de serveur nécessaire")
            nouveau_gestionnaire = changer_serveur(nouveau_gestionnaire)
            nouveau_gestionnaire['compte_service'] = 0
                
        nouveau_gestionnaire['etat'] = gestionnaire['regles']['ETATS_JEU']['PRET_A_SERVIR']
        
        return nouveau_gestionnaire
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du compte service: {e}")
        raise

def changer_serveur(gestionnaire):
    logger.debug("Changement de serveur")
    try:
        nouveau_serveur = 3 - gestionnaire['serveur_actuel']
        nouveau_gestionnaire = {
            **gestionnaire,
            'serveur_actuel': nouveau_serveur,
            'service_depuis_gauche': nouveau_serveur == 1,
            'let_service': False,
            'etat': gestionnaire['regles']['ETATS_JEU']['PRET_A_SERVIR']
        }
        logger.debug(f"Nouveau serveur: {nouveau_serveur}")
        return nouveau_gestionnaire
    except Exception as e:
        logger.error(f"Erreur lors du changement de serveur: {e}")
        raise

def commencer_service(gestionnaire):
    logger.debug("Début du service")
    return {
        **gestionnaire,
        'etat': gestionnaire['regles']['ETATS_JEU']['SERVICE_COMMENCE']
    }

def gerer_le_service(gestionnaire):
    logger.debug("Gestion du let service")
    return {
        **gestionnaire,
        'let_service': True,
        'etat': gestionnaire['regles']['ETATS_JEU']['PRET_A_SERVIR']
    }

def obtenir_position_service(gestionnaire):
    logger.debug("Calcul de la position de service")
    try:
        if gestionnaire['service_depuis_gauche']:
            position = gestionnaire['regles']['TABLE_X'] + 30
        else:
            position = gestionnaire['regles']['TABLE_X'] + gestionnaire['regles']['LARGEUR_TABLE_PIXELS'] - 30
        logger.debug(f"Position de service calculée: {position}")
        return position
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la position de service: {e}")
        raise

def reinitialiser(gestionnaire):
    logger.debug("Réinitialisation du gestionnaire de service")
    return creer_gestionnaire_service()

def obtenir_info_service(gestionnaire):
    logger.debug("Récupération des informations de service")
    return {
        'serveur_actuel': gestionnaire['serveur_actuel'],
        'services_restants': gestionnaire['services_par_tour'] - gestionnaire['compte_service'],
        'est_egalite': gestionnaire['est_egalite'],
        'service_depuis_gauche': gestionnaire['service_depuis_gauche'],
        'etat': gestionnaire['etat'],
        'let_service': gestionnaire['let_service']
    }

def est_pret_a_servir(gestionnaire):
    try:
        resultat = gestionnaire['etat'] == gestionnaire['regles']['ETATS_JEU']['PRET_A_SERVIR']
        logger.debug(f"Vérification prêt à servir: {resultat}")
        return resultat
    except Exception as e:
        logger.error(f"Erreur lors de la vérification prêt à servir: {e}")
        raise

def est_en_service(gestionnaire):
    try:
        resultat = gestionnaire['etat'] == gestionnaire['regles']['ETATS_JEU']['SERVICE_COMMENCE']
        logger.debug(f"Vérification en service: {resultat}")
        return resultat
    except Exception as e:
        logger.error(f"Erreur lors de la vérification en service: {e}")
        raise

def servir(gestionnaire):
    logger.debug("Début d'un nouveau service")
    return commencer_service(gestionnaire)