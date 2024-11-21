from dataclasses import dataclass
from typing import Tuple, Dict, Optional
import random
import time
from regles_tennis_table import ReglesTennisTable

@dataclass(frozen=True)
class EtatService:
    """État immuable du service"""
    serveur_actuel: int
    compte_service: int
    services_par_tour: int
    est_egalite: bool
    let_service: bool
    etat: str
    service_depuis_gauche: bool

def creer_etat_service() -> EtatService:
    """Crée un nouvel état de service initial avec un serveur aléatoire"""
    regles = ReglesTennisTable()
    
    # Initialiser le générateur aléatoire avec l'heure actuelle
    random.seed(time.time())
    serveur_initial = random.choice([1, 2])
    
    return EtatService(
        serveur_actuel=serveur_initial,
        compte_service=0,
        services_par_tour=regles.SERVICES_PAR_TOUR,
        est_egalite=False,
        let_service=False,
        etat=regles.ETATS_JEU['PRET_A_SERVIR'],
        service_depuis_gauche=serveur_initial == 1
    )

def mettre_a_jour_compte_service(etat: EtatService, score1: int, score2: int) -> EtatService:
    """Retourne un nouvel état après la mise à jour du compte de services"""
    regles = ReglesTennisTable()
    
    # Vérifier la situation d'égalité
    nouvelle_egalite = est_situation_egalite(score1, score2)
    nouveaux_services_par_tour = 1 if nouvelle_egalite else regles.SERVICES_PAR_TOUR
    
    # Si on entre en égalité
    if nouvelle_egalite and not etat.est_egalite:
        nouveau_compte = 0
    else:
        nouveau_compte = etat.compte_service + 1
    
    # Déterminer si on doit changer de serveur
    if nouveau_compte >= etat.services_par_tour:
        return changer_serveur(EtatService(
            serveur_actuel=etat.serveur_actuel,
            compte_service=0,
            services_par_tour=nouveaux_services_par_tour,
            est_egalite=nouvelle_egalite,
            let_service=False,
            etat=regles.ETATS_JEU['PRET_A_SERVIR'],
            service_depuis_gauche=etat.service_depuis_gauche
        ))
    
    return EtatService(
        serveur_actuel=etat.serveur_actuel,
        compte_service=nouveau_compte,
        services_par_tour=nouveaux_services_par_tour,
        est_egalite=nouvelle_egalite,
        let_service=etat.let_service,
        etat=regles.ETATS_JEU['PRET_A_SERVIR'],
        service_depuis_gauche=etat.service_depuis_gauche
    )

def est_situation_egalite(score1: int, score2: int) -> bool:
    """Détermine si le jeu est en situation d'égalité"""
    return score1 >= 10 and score2 >= 10

def changer_serveur(etat: EtatService) -> EtatService:
    """Retourne un nouvel état avec le serveur changé"""
    nouveau_serveur = 3 - etat.serveur_actuel  # Alterne entre 1 et 2
    return EtatService(
        serveur_actuel=nouveau_serveur,
        compte_service=0,
        services_par_tour=etat.services_par_tour,
        est_egalite=etat.est_egalite,
        let_service=False,
        etat=etat.etat,
        service_depuis_gauche=nouveau_serveur == 1
    )

def commencer_service(etat: EtatService) -> EtatService:
    """Retourne un nouvel état indiquant le début du service"""
    regles = ReglesTennisTable()
    return EtatService(
        serveur_actuel=etat.serveur_actuel,
        compte_service=etat.compte_service,
        services_par_tour=etat.services_par_tour,
        est_egalite=etat.est_egalite,
        let_service=False,
        etat=regles.ETATS_JEU['SERVICE_COMMENCE'],
        service_depuis_gauche=etat.service_depuis_gauche
    )

def gerer_let_service(etat: EtatService) -> EtatService:
    """Retourne un nouvel état après un let service"""
    regles = ReglesTennisTable()
    return EtatService(
        serveur_actuel=etat.serveur_actuel,
        compte_service=etat.compte_service,
        services_par_tour=etat.services_par_tour,
        est_egalite=etat.est_egalite,
        let_service=True,
        etat=regles.ETATS_JEU['PRET_A_SERVIR'],
        service_depuis_gauche=etat.service_depuis_gauche
    )

def obtenir_position_service(etat: EtatService) -> float:
    """Retourne la position x initiale du service"""
    regles = ReglesTennisTable()
    if etat.service_depuis_gauche:
        return regles.TABLE_X + 30
    return regles.TABLE_X + regles.LARGEUR_TABLE_PIXELS - 30

def obtenir_info_service(etat: EtatService) -> Dict:
    """Retourne un dictionnaire contenant les informations sur le service"""
    return {
        'serveur_actuel': etat.serveur_actuel,
        'services_restants': etat.services_par_tour - etat.compte_service,
        'est_egalite': etat.est_egalite,
        'service_depuis_gauche': etat.service_depuis_gauche,
        'etat': etat.etat,
        'let_service': etat.let_service
    }

def est_pret_a_servir(etat: EtatService) -> bool:
    """Vérifie si le service peut être effectué"""
    regles = ReglesTennisTable()
    return etat.etat == regles.ETATS_JEU['PRET_A_SERVIR']

def est_en_service(etat: EtatService) -> bool:
    """Vérifie si le service est en cours"""
    regles = ReglesTennisTable()
    return etat.etat == regles.ETATS_JEU['SERVICE_COMMENCE']