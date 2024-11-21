from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from enum import Enum
from regles_tennis_table import ReglesTennisTable
from balle import Balle, creer_balle, definir_sons

class GestionnaireMatchError(Exception):
    """Classe de base pour les exceptions du gestionnaire de match"""
    pass

class ScoreInvalideError(GestionnaireMatchError):
    """Exception levée quand un score est invalide"""
    pass

class EtatMatchInvalideError(GestionnaireMatchError):
    """Exception levée quand une transition d'état est invalide"""
    pass

class TransitionError(GestionnaireMatchError):
    """Exception levée quand une transition d'état est impossible"""
    pass

class PhaseMatch(Enum):
    """Phases possibles d'un match"""
    INITIALISATION = "initialisation"
    DEBUT_JEU = "debut_jeu"
    EN_COURS = "en_cours"
    POINT_MARQUE = "point_marque"
    FIN_JEU = "fin_jeu"
    FIN_MATCH = "fin_match"
    PAUSE = "pause"

@dataclass(frozen=True)
class Score:
    """Représentation immuable du score"""
    points: Tuple[int, int]
    jeux: Tuple[int, int]
    avantage: Optional[int] = None  # 1 pour joueur 1, 2 pour joueur 2, None si pas d'avantage

@dataclass(frozen=True)
class EtatMatch:
    """État immuable du match"""
    score: Score
    phase: PhaseMatch
    serveur_actuel: int
    nombre_services: int
    match_termine: bool
    gagnant_match: Optional[int]
    dernier_point_gagne_par: Optional[int]

    def __post_init__(self):
        """Validation des données à la création de l'instance"""
        if not isinstance(self.score, Score):
            raise ScoreInvalideError("Le score doit être une instance de Score")
        
        if not isinstance(self.phase, PhaseMatch):
            raise EtatMatchInvalideError(f"Phase de match invalide : {self.phase}")
        
        if self.serveur_actuel not in (1, 2):
            raise ValueError("Le serveur doit être 1 ou 2")
        
        if not isinstance(self.nombre_services, int) or self.nombre_services < 0:
            raise ValueError("Le nombre de services doit être un entier positif")
        
        if self.gagnant_match is not None and self.gagnant_match not in (1, 2):
            raise ScoreInvalideError("Le gagnant du match doit être 1 ou 2")

def valider_score(score: Score, regles: ReglesTennisTable) -> None:
    """Valide un score selon les règles du jeu"""
    if not all(isinstance(p, int) and p >= 0 for p in score.points):
        raise ScoreInvalideError("Les points doivent être des entiers positifs")
    
    if not all(isinstance(j, int) and j >= 0 for j in score.jeux):
        raise ScoreInvalideError("Les jeux doivent être des entiers positifs")
    
    if score.avantage is not None and score.avantage not in (1, 2):
        raise ScoreInvalideError("L'avantage doit être 1, 2 ou None")
    
    if max(score.jeux) > regles.TOTAL_JEUX_POSSIBLES:
        raise ScoreInvalideError(f"Score impossible : maximum {regles.TOTAL_JEUX_POSSIBLES} jeux")

def creer_match(regles: ReglesTennisTable) -> EtatMatch:
    """Crée un nouvel état de match initial"""
    try:
        score_initial = Score(points=(0, 0), jeux=(0, 0))
        return EtatMatch(
            score=score_initial,
            phase=PhaseMatch.INITIALISATION,
            serveur_actuel=1,  # Le joueur 1 commence à servir
            nombre_services=0,
            match_termine=False,
            gagnant_match=None,
            dernier_point_gagne_par=None
        )
    except Exception as e:
        raise GestionnaireMatchError(f"Erreur lors de la création du match : {str(e)}")

def calculer_prochain_serveur(match: EtatMatch, regles: ReglesTennisTable) -> int:
    """Détermine qui doit servir au prochain point"""
    if match.score.points[0] >= 10 and match.score.points[1] >= 10:
        # En cas d'égalité à 10+, on alterne à chaque point
        return 3 - match.serveur_actuel
    
    if match.nombre_services >= regles.SERVICES_PAR_TOUR:
        return 3 - match.serveur_actuel
    
    return match.serveur_actuel

def marquer_point(match: EtatMatch, joueur: int, regles: ReglesTennisTable) -> EtatMatch:
    """Gère le marquage d'un point"""
    try:
        if not isinstance(joueur, int) or joueur not in (1, 2):
            raise ValueError("Le joueur doit être 1 ou 2")
        
        if match.match_termine:
            raise EtatMatchInvalideError("Le match est déjà terminé")

        points_actuels = list(match.score.points)
        points_actuels[joueur-1] += 1
        
        # Gérer l'avantage et la victoire du jeu
        nouvel_avantage = None
        nouveau_jeux = list(match.score.jeux)
        nouvelle_phase = PhaseMatch.EN_COURS
        
        if max(points_actuels) >= 11:
            difference = abs(points_actuels[0] - points_actuels[1])
            if difference >= 2:
                # Fin du jeu
                nouveau_jeux[joueur-1] += 1
                points_actuels = [0, 0]  # Réinitialiser les points
                nouvelle_phase = PhaseMatch.FIN_JEU
        
        # Vérifier si le match est terminé
        match_termine = False
        gagnant_match = None
        if max(nouveau_jeux) >= regles.JEUX_POUR_GAGNER_MATCH:
            match_termine = True
            gagnant_match = 1 if nouveau_jeux[0] > nouveau_jeux[1] else 2
            nouvelle_phase = PhaseMatch.FIN_MATCH

        # Calculer le prochain serveur
        nouveau_nombre_services = match.nombre_services + 1
        prochain_serveur = calculer_prochain_serveur(match, regles)
        if prochain_serveur != match.serveur_actuel:
            nouveau_nombre_services = 0

        nouveau_score = Score(
            points=tuple(points_actuels),
            jeux=tuple(nouveau_jeux),
            avantage=nouvel_avantage
        )

        return EtatMatch(
            score=nouveau_score,
            phase=nouvelle_phase,
            serveur_actuel=prochain_serveur,
            nombre_services=nouveau_nombre_services,
            match_termine=match_termine,
            gagnant_match=gagnant_match,
            dernier_point_gagne_par=joueur
        )

    except Exception as e:
        raise GestionnaireMatchError(f"Erreur lors du marquage du point : {str(e)}")

def obtenir_info_match(match: EtatMatch) -> Dict:
    """Retourne un dictionnaire contenant les informations sur le match"""
    try:
        return {
            'score': {
                'points': match.score.points,
                'jeux': match.score.jeux,
                'avantage': match.score.avantage
            },
            'phase': match.phase.value,
            'serveur_actuel': match.serveur_actuel,
            'nombre_services': match.nombre_services,
            'match_termine': match.match_termine,
            'gagnant_match': match.gagnant_match,
            'dernier_point_gagne_par': match.dernier_point_gagne_par
        }
    except Exception as e:
        raise GestionnaireMatchError(f"Erreur lors de la récupération des informations : {str(e)}")

def peut_servir(match: EtatMatch) -> bool:
    """Vérifie si le service peut être effectué"""
    return match.phase in (PhaseMatch.DEBUT_JEU, PhaseMatch.INITIALISATION)

def mettre_en_pause(match: EtatMatch) -> EtatMatch:
    """Met le match en pause"""
    if match.phase == PhaseMatch.PAUSE:
        raise EtatMatchInvalideError("Le match est déjà en pause")
    
    return EtatMatch(
        score=match.score,
        phase=PhaseMatch.PAUSE,
        serveur_actuel=match.serveur_actuel,
        nombre_services=match.nombre_services,
        match_termine=match.match_termine,
        gagnant_match=match.gagnant_match,
        dernier_point_gagne_par=match.dernier_point_gagne_par
    )

def reprendre_match(match: EtatMatch) -> EtatMatch:
    """Reprend le match après une pause"""
    if match.phase != PhaseMatch.PAUSE:
        raise EtatMatchInvalideError("Le match n'est pas en pause")
    
    return EtatMatch(
        score=match.score,
        phase=PhaseMatch.EN_COURS,
        serveur_actuel=match.serveur_actuel,
        nombre_services=match.nombre_services,
        match_termine=match.match_termine,
        gagnant_match=match.gagnant_match,
        dernier_point_gagne_par=match.dernier_point_gagne_par
    )