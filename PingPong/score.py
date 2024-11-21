from dataclasses import dataclass
from typing import Tuple, Dict, Optional
import logging
from regles_tennis_table import ReglesTennisTable

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScoreError(Exception):
    """Classe de base pour les erreurs liées au score"""
    pass

class ValidationScoreError(ScoreError):
    """Erreur de validation du score"""
    pass

class TransitionScoreError(ScoreError):
    """Erreur de transition d'état du score"""
    pass

Score = Tuple[int, int]

@dataclass(frozen=True)
class EtatScore:
    """État immuable du score"""
    score_actuel: Score
    jeux_gagnes: Score
    est_avantage: bool
    gagnant_jeu: Optional[int]
    gagnant_match: Optional[int]
    etat: str

    def __post_init__(self):
        """Validation des données à la création"""
        if not isinstance(self.score_actuel, tuple) or len(self.score_actuel) != 2:
            raise ValidationScoreError("Le score actuel doit être un tuple de 2 entiers")
        if not all(isinstance(s, int) and s >= 0 for s in self.score_actuel):
            raise ValidationScoreError("Les scores doivent être des entiers positifs")
            
        if not isinstance(self.jeux_gagnes, tuple) or len(self.jeux_gagnes) != 2:
            raise ValidationScoreError("Les jeux gagnés doivent être un tuple de 2 entiers")
        if not all(isinstance(j, int) and j >= 0 for j in self.jeux_gagnes):
            raise ValidationScoreError("Les jeux doivent être des entiers positifs")
            
        if self.gagnant_jeu is not None and self.gagnant_jeu not in (1, 2):
            raise ValidationScoreError("Le gagnant du jeu doit être 1 ou 2")
        if self.gagnant_match is not None and self.gagnant_match not in (1, 2):
            raise ValidationScoreError("Le gagnant du match doit être 1 ou 2")

def valider_score(score: Score, regles: ReglesTennisTable) -> None:
    """Valide un score selon les règles du jeu"""
    try:
        if not isinstance(score, tuple) or len(score) != 2:
            raise ValidationScoreError("Format de score invalide")
        if not all(isinstance(s, int) and s >= 0 for s in score):
            raise ValidationScoreError("Les scores doivent être des entiers positifs")
            
        # Vérifier les limites de score
        max_score = max(score)
        if max_score > regles.POINTS_POUR_GAGNER * 2:  # Limite arbitraire mais raisonnable
            raise ValidationScoreError(f"Score trop élevé : {max_score}")
            
        # Vérifier la différence en cas de fin de jeu
        if max_score >= regles.POINTS_POUR_GAGNER:
            difference = abs(score[0] - score[1])
            if difference > regles.POINTS_POUR_GAGNER:
                raise ValidationScoreError(f"Différence de score invalide : {difference}")
    except Exception as e:
        logger.error(f"Erreur de validation du score : {e}")
        raise

def creer_score_initial(regles: ReglesTennisTable) -> EtatScore:
    """Crée un nouvel état de score initial"""
    try:
        return EtatScore(
            score_actuel=(0, 0),
            jeux_gagnes=(0, 0),
            est_avantage=False,
            gagnant_jeu=None,
            gagnant_match=None,
            etat=regles.ETATS_JEU['PRET_A_SERVIR']
        )
    except Exception as e:
        logger.error(f"Erreur lors de la création du score initial : {e}")
        raise ScoreError(f"Erreur d'initialisation : {e}")

def incrementer_score(etat: EtatScore, joueur: int, regles: ReglesTennisTable) -> EtatScore:
    """Retourne un nouvel état avec le score incrémenté pour le joueur spécifié"""
    try:
        if not isinstance(joueur, int) or joueur not in (1, 2):
            raise ValidationScoreError("Joueur invalide")
        
        # Calculer le nouveau score
        nouveau_score = list(etat.score_actuel)
        nouveau_score[joueur - 1] += 1
        nouveau_score = tuple(nouveau_score)
        
        # Valider le nouveau score
        valider_score(nouveau_score, regles)
        
        # Vérifier l'avantage
        nouvel_avantage = verifier_avantage(nouveau_score, regles)
        
        # Vérifier le gagnant
        nouveau_gagnant = verifier_gagnant(nouveau_score, regles)
        
        # Calculer les nouveaux jeux gagnés si nécessaire
        nouveaux_jeux_gagnes = list(etat.jeux_gagnes)
        if nouveau_gagnant:
            nouveaux_jeux_gagnes[nouveau_gagnant - 1] += 1
        nouveaux_jeux_gagnes = tuple(nouveaux_jeux_gagnes)
        
        # Vérifier le gagnant du match
        nouveau_gagnant_match = verifier_gagnant_match(nouveaux_jeux_gagnes, regles)
        
        # Déterminer le nouvel état
        nouvel_etat = (
            regles.ETATS_JEU['MATCH_TERMINE'] if nouveau_gagnant_match else
            regles.ETATS_JEU['JEU_TERMINE'] if nouveau_gagnant else
            regles.ETATS_JEU['ECHANGE']
        )
        
        return EtatScore(
            score_actuel=nouveau_score,
            jeux_gagnes=nouveaux_jeux_gagnes,
            est_avantage=nouvel_avantage,
            gagnant_jeu=nouveau_gagnant,
            gagnant_match=nouveau_gagnant_match,
            etat=nouvel_etat
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'incrémentation du score : {e}")
        raise ScoreError(f"Erreur d'incrémentation : {e}")

def verifier_avantage(score: Score, regles: ReglesTennisTable) -> bool:
    """Vérifie si le score est en situation d'avantage"""
    try:
        valider_score(score, regles)
        return score[0] >= regles.POINTS_POUR_GAGNER - 1 and \
               score[1] >= regles.POINTS_POUR_GAGNER - 1 and \
               abs(score[0] - score[1]) <= 1
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'avantage : {e}")
        raise

def verifier_gagnant(score: Score, regles: ReglesTennisTable) -> Optional[int]:
    """Vérifie s'il y a un gagnant pour le jeu actuel"""
    try:
        valider_score(score, regles)
        
        if max(score) >= regles.POINTS_POUR_GAGNER:
            difference = abs(score[0] - score[1])
            if difference >= regles.DIFFERENCE_POINTS_MIN:
                return 1 if score[0] > score[1] else 2
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du gagnant : {e}")
        raise

def verifier_gagnant_match(jeux: Score, regles: ReglesTennisTable) -> Optional[int]:
    """Vérifie s'il y a un gagnant pour le match"""
    try:
        if jeux[0] >= regles.JEUX_POUR_GAGNER_MATCH:
            return 1
        elif jeux[1] >= regles.JEUX_POUR_GAGNER_MATCH:
            return 2
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du gagnant du match : {e}")
        raise

def obtenir_etat_jeu(etat: EtatScore) -> Dict:
    """Retourne un dictionnaire contenant l'état actuel du jeu"""
    try:
        return {
            'score': etat.score_actuel,
            'jeux': etat.jeux_gagnes,
            'est_avantage': etat.est_avantage,
            'gagnant_jeu': etat.gagnant_jeu,
            'gagnant_match': etat.gagnant_match,
            'etat': etat.etat
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'état : {e}")
        raise ScoreError(f"Erreur de récupération d'état : {e}")

def obtenir_affichage_score(etat: EtatScore) -> Tuple[str, str]:
    """Retourne les chaînes formatées du score pour l'affichage"""
    try:
        score_jeu = f"{etat.score_actuel[0]}-{etat.score_actuel[1]}"
        if etat.est_avantage:
            score_jeu += " AVANTAGE"
        
        score_match = f"Jeux: {etat.jeux_gagnes[0]}-{etat.jeux_gagnes[1]}"
        
        return score_jeu, score_match
    except Exception as e:
        logger.error(f"Erreur lors du formatage du score : {e}")
        raise ScoreError(f"Erreur de formatage : {e}")

def commencer_nouveau_jeu(etat: EtatScore, regles: ReglesTennisTable) -> EtatScore:
    """Retourne un nouvel état pour un nouveau jeu dans le match"""
    try:
        return EtatScore(
            score_actuel=(0, 0),
            jeux_gagnes=etat.jeux_gagnes,
            est_avantage=False,
            gagnant_jeu=None,
            gagnant_match=etat.gagnant_match,
            etat=regles.ETATS_JEU['PRET_A_SERVIR']
        )
    except Exception as e:
        logger.error(f"Erreur lors du démarrage d'un nouveau jeu : {e}")
        raise ScoreError(f"Erreur de nouveau jeu : {e}")

def reinitialiser_score(regles: ReglesTennisTable) -> EtatScore:
    """Retourne un nouvel état complètement réinitialisé"""
    try:
        return creer_score_initial(regles)
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation du score : {e}")
        raise ScoreError(f"Erreur de réinitialisation : {e}")