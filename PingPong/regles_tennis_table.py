from dataclasses import dataclass
from typing import Dict, Tuple, TypedDict
import pygame
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

class ReglesError(Exception):
    """Classe de base pour les erreurs de règles"""
    pass

class ConfigurationError(ReglesError):
    """Erreur de configuration des règles"""
    pass

class ValidationReglesError(ReglesError):
    """Erreur de validation des règles"""
    pass

class ConfigCouleurs(TypedDict):
    """Configuration des couleurs du jeu"""
    BLANC: Tuple[int, int, int]
    NOIR: Tuple[int, int, int]
    GRIS: Tuple[int, int, int]
    VERT: Tuple[int, int, int]
    JAUNE: Tuple[int, int, int]
    ROUGE: Tuple[int, int, int]

class ConfigDifficulte(TypedDict):
    """Configuration de la difficulté"""
    CURSEUR_ARRIERE_PLAN: Tuple[int, int, int]
    CURSEUR_REMPLISSAGE: Tuple[int, int, int]
    COULEURS_NIVEAU: list[Tuple[int, int, int]]

@dataclass(frozen=True)
class ReglesJeu:
    """Configuration immuable des règles du jeu"""
    # Configuration fenêtre
    LARGEUR_FENETRE: int = 800
    HAUTEUR_FENETRE: int = 600
    TITRE_FENETRE: str = "Tennis de Table"
    IPS: int = 60

    # Règles du score
    POINTS_POUR_GAGNER: int = 11
    DIFFERENCE_POINTS_MIN: int = 2
    JEUX_POUR_GAGNER_MATCH: int = 3
    TOTAL_JEUX_POSSIBLES: int = 5

    # Règles du service
    SERVICES_PAR_TOUR: int = 2
    DELAI_ENTRE_IMPACTS: int = 100  # ms

    # Dimensions table
    LARGEUR_TABLE_POURCENT: int = 60
    POSITION_FILET_POURCENT: int = 50

    def __post_init__(self):
        """Validation des règles à la création"""
        try:
            self._valider_dimensions_fenetre()
            self._valider_regles_score()
            self._valider_regles_service()
            self._valider_dimensions_table()
            self._valider_dimensions_raquette()
            self._valider_configuration_balle()
            self._valider_configuration_interface()
            self._valider_configuration_difficulte()
        except Exception as e:
            raise ConfigurationError(f"Configuration invalide : {str(e)}")

    def _valider_dimensions_fenetre(self) -> None:
        """Valide les dimensions de la fenêtre"""
        if self.LARGEUR_FENETRE <= 0 or self.HAUTEUR_FENETRE <= 0:
            raise ValidationReglesError("Les dimensions de la fenêtre doivent être positives")
        if self.IPS <= 0:
            raise ValidationReglesError("Le nombre d'images par seconde doit être positif")

    def _valider_regles_score(self) -> None:
        """Valide les règles du score"""
        if self.POINTS_POUR_GAGNER <= 0:
            raise ValidationReglesError("Le nombre de points pour gagner doit être positif")
        if self.DIFFERENCE_POINTS_MIN <= 0:
            raise ValidationReglesError("La différence minimale de points doit être positive")
        if self.JEUX_POUR_GAGNER_MATCH <= 0:
            raise ValidationReglesError("Le nombre de jeux pour gagner doit être positif")
        if self.TOTAL_JEUX_POSSIBLES <= 0:
            raise ValidationReglesError("Le nombre total de jeux possibles doit être positif")
        if self.TOTAL_JEUX_POSSIBLES <= self.JEUX_POUR_GAGNER_MATCH:
            raise ValidationReglesError("Le total des jeux doit être supérieur aux jeux nécessaires")

    def _valider_regles_service(self) -> None:
        """Valide les règles du service"""
        if self.SERVICES_PAR_TOUR <= 0:
            raise ValidationReglesError("Le nombre de services par tour doit être positif")
        if self.DELAI_ENTRE_IMPACTS < 0:
            raise ValidationReglesError("Le délai entre impacts doit être positif ou nul")

    def _valider_dimensions_table(self) -> None:
        """Valide les dimensions de la table"""
        if not 0 <= self.LARGEUR_TABLE_POURCENT <= 100:
            raise ValidationReglesError("La largeur de la table doit être entre 0 et 100%")
        if not 0 <= self.POSITION_FILET_POURCENT <= 100:
            raise ValidationReglesError("La position du filet doit être entre 0 et 100%")

    @property
    def TABLE_X(self) -> int:
        """Calcule la position X de la table"""
        return (self.LARGEUR_FENETRE - (self.LARGEUR_FENETRE * self.LARGEUR_TABLE_POURCENT // 100)) // 2

    @property
    def TABLE_Y(self) -> int:
        """Calcule la position Y de la table"""
        return self.HAUTEUR_FENETRE * 25 // 100

    @property
    def HAUTEUR_TABLE(self) -> int:
        """Calcule la hauteur de la table"""
        return self.HAUTEUR_FENETRE * 50 // 100

    @property
    def LARGEUR_TABLE_PIXELS(self) -> int:
        """Calcule la largeur de la table en pixels"""
        return self.LARGEUR_FENETRE * self.LARGEUR_TABLE_POURCENT // 100

    # Configuration raquettes
    LARGEUR_RAQUETTE: int = 60
    HAUTEUR_RAQUETTE: int = 100
    VITESSE_RAQUETTE: int = 12

    def _valider_dimensions_raquette(self) -> None:
        """Valide les dimensions de la raquette"""
        if self.LARGEUR_RAQUETTE <= 0 or self.HAUTEUR_RAQUETTE <= 0:
            raise ValidationReglesError("Les dimensions de la raquette doivent être positives")
        if self.VITESSE_RAQUETTE <= 0:
            raise ValidationReglesError("La vitesse de la raquette doit être positive")

    # Configuration balle
    RAYON_BALLE: int = 7
    VITESSE_BALLE_MIN: float = 7.0
    VITESSE_BALLE_MAX: float = 18.0

    def _valider_configuration_balle(self) -> None:
        """Valide la configuration de la balle"""
        if self.RAYON_BALLE <= 0:
            raise ValidationReglesError("Le rayon de la balle doit être positif")
        if self.VITESSE_BALLE_MIN <= 0:
            raise ValidationReglesError("La vitesse minimale de la balle doit être positive")
        if self.VITESSE_BALLE_MAX <= self.VITESSE_BALLE_MIN:
            raise ValidationReglesError("La vitesse max doit être supérieure à la vitesse min")

    # Configuration interface
    TAILLE_POLICE_PRINCIPALE: int = 48
    TAILLE_POLICE_SECONDAIRE: int = 32
    TAILLE_POLICE_STANDARD: int = 36
    TAILLE_POLICE_ALERTE: int = 48
    DUREE_ALERTE: int = 2000  # ms

    def _valider_configuration_interface(self) -> None:
        """Valide la configuration de l'interface"""
        if any(taille <= 0 for taille in [
            self.TAILLE_POLICE_PRINCIPALE,
            self.TAILLE_POLICE_SECONDAIRE,
            self.TAILLE_POLICE_STANDARD,
            self.TAILLE_POLICE_ALERTE
        ]):
            raise ValidationReglesError("Les tailles de police doivent être positives")
        if self.DUREE_ALERTE <= 0:
            raise ValidationReglesError("La durée d'alerte doit être positive")

    # Configuration difficulté
    DIFFICULTE_MIN: int = 1
    DIFFICULTE_MAX: int = 10
    LARGEUR_CURSEUR_DIFFICULTE: int = 400
    HAUTEUR_CURSEUR_DIFFICULTE: int = 8
    RAYON_POIGNEE_DIFFICULTE: int = 12

    def _valider_configuration_difficulte(self) -> None:
        """Valide la configuration de la difficulté"""
        if self.DIFFICULTE_MIN <= 0:
            raise ValidationReglesError("La difficulté minimale doit être positive")
        if self.DIFFICULTE_MAX <= self.DIFFICULTE_MIN:
            raise ValidationReglesError("La difficulté max doit être supérieure à la min")
        if any(dim <= 0 for dim in [
            self.LARGEUR_CURSEUR_DIFFICULTE,
            self.HAUTEUR_CURSEUR_DIFFICULTE,
            self.RAYON_POIGNEE_DIFFICULTE
        ]):
            raise ValidationReglesError("Les dimensions du curseur doivent être positives")

    # Couleurs de base
    COULEURS: ConfigCouleurs = ConfigCouleurs(
        BLANC=(255, 255, 255),
        NOIR=(0, 0, 0),
        GRIS=(64, 64, 66),
        VERT=(0, 164, 0),
        JAUNE=(255, 255, 0),
        ROUGE=(255, 0, 0)
    )

    # Configuration du sélecteur de difficulté
    CONFIG_DIFFICULTE: ConfigDifficulte = ConfigDifficulte(
        CURSEUR_ARRIERE_PLAN=(100, 100, 100),
        CURSEUR_REMPLISSAGE=(150, 150, 150),
        COULEURS_NIVEAU=[
            (0, 0, 255),      # Débutant
            (0, 255, 0),      # Intermédiaire
            (255, 165, 0),    # Expert
            (255, 0, 0)       # Maître
        ]
    )

    # États du jeu
    ETATS_JEU: Dict[str, str] = {
        'PRET_A_SERVIR': 'pret_a_servir',
        'SERVICE_COMMENCE': 'service_commence',
        'ECHANGE': 'echange',
        'POINT_TERMINE': 'point_termine',
        'JEU_TERMINE': 'jeu_termine',
        'MATCH_TERMINE': 'match_termine'
    }

    # Contrôles
    CONTROLES: Dict[str, Dict[str, int]] = {
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

    def obtenir_dimensions_table(self) -> Dict[str, int]:
        """Retourne les dimensions calculées de la table"""
        return {
            'x': self.TABLE_X,
            'y': self.TABLE_Y,
            'largeur': self.LARGEUR_TABLE_PIXELS,
            'hauteur': self.HAUTEUR_TABLE
        }

def creer_regles() -> ReglesJeu:
    """Crée une instance des règles du jeu"""
    try:
        logger.info("Création des règles du jeu")
        regles = ReglesJeu()
        logger.debug("Règles créées avec succès")
        return regles
    except Exception as e:
        logger.error(f"Erreur lors de la création des règles : {e}")
        raise ReglesError(f"Impossible de créer les règles : {e}")

# Fonctions pures pour les règles du jeu
def est_avantage(regles: ReglesJeu, score1: int, score2: int) -> bool:
    """Vérifie si le jeu est en situation d'avantage"""
    try:
        if not all(isinstance(s, int) and s >= 0 for s in (score1, score2)):
            raise ValidationReglesError("Les scores doivent être des entiers positifs")
        return (score1 >= regles.POINTS_POUR_GAGNER - 1 and 
                score2 >= regles.POINTS_POUR_GAGNER - 1)
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'avantage : {e}")
        raise

def est_gagnant_jeu(regles: ReglesJeu, score1: int, score2: int) -> int | None:
    """Détermine s'il y a un gagnant du jeu"""
    try:
        if not all(isinstance(s, int) and s >= 0 for s in (score1, score2)):
            raise ValidationReglesError("Les scores doivent être des entiers positifs")
            
        if max(score1, score2) >= regles.POINTS_POUR_GAGNER:
            if abs(score1 - score2) >= regles.DIFFERENCE_POINTS_MIN:
                return 1 if score1 > score2 else 2
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du gagnant du jeu : {e}")
        raise

def est_gagnant_match(regles: ReglesJeu, jeux1: int, jeux2: int) -> int | None:
    """Détermine s'il y a un gagnant du match"""
    try:
        if not all(isinstance(j, int) and j >= 0 for j in (jeux1, jeux2)):
            raise ValidationReglesError("Les jeux doivent être des entiers positifs")
            
        if jeux1 >= regles.JEUX_POUR_GAGNER_MATCH:
            return 1
        elif jeux2 >= regles.JEUX_POUR_GAGNER_MATCH:
            return 2
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du gagnant du match : {e}")
        raise

def calculer_vitesse_balle(regles: ReglesJeu, niveau: int) -> float:
    """Calcule la vitesse de la balle en fonction du niveau de difficulté"""
    try:
        if not isinstance(niveau, int):
            raise ValidationReglesError("Le niveau doit être un entier")
        if niveau < regles.DIFFICULTE_MIN or niveau > regles.DIFFICULTE_MAX:
            raise ValidationReglesError(
                f"Le niveau doit être entre {regles.DIFFICULTE_MIN} "
                f"et {regles.DIFFICULTE_MAX}"
            )
        
        ratio = (niveau - regles.DIFFICULTE_MIN) / (regles.DIFFICULTE_MAX - regles.DIFFICULTE_MIN)
        vitesse = (regles.VITESSE_BALLE_MIN + 
                  (regles.VITESSE_BALLE_MAX - regles.VITESSE_BALLE_MIN) * ratio)
        
        # Valider la vitesse calculée
        if not regles.VITESSE_BALLE_MIN <= vitesse <= regles.VITESSE_BALLE_MAX:
            raise ValidationReglesError(f"Vitesse calculée invalide : {vitesse}")
            
        return vitesse
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la vitesse : {e}")
        raise ReglesError(f"Erreur de calcul de vitesse : {e}")

def obtenir_nom_niveau(regles: ReglesJeu, niveau: int) -> str:
    """Retourne le nom du niveau de difficulté"""
    try:
        if not isinstance(niveau, int):
            raise ValidationReglesError("Le niveau doit être un entier")
        if niveau < regles.DIFFICULTE_MIN or niveau > regles.DIFFICULTE_MAX:
            raise ValidationReglesError(
                f"Le niveau doit être entre {regles.DIFFICULTE_MIN} "
                f"et {regles.DIFFICULTE_MAX}"
            )
            
        if niveau <= 3:
            return "Débutant"
        elif niveau <= 6:
            return "Intermédiaire"
        elif niveau <= 9:
            return "Expert"
        else:
            return "Maître"
    except Exception as e:
        logger.error(f"Erreur lors de l'obtention du nom du niveau : {e}")
        raise ReglesError(f"Erreur d'obtention du nom de niveau : {e}")

def valider_etat_jeu(etat: str, regles: ReglesJeu) -> bool:
    """Valide si l'état du jeu est valide"""
    try:
        return etat in regles.ETATS_JEU.values()
    except Exception as e:
        logger.error(f"Erreur lors de la validation de l'état : {e}")
        raise ReglesError(f"Erreur de validation d'état : {e}")

def verifier_transition_etat_valide(etat_actuel: str, nouvel_etat: str, regles: ReglesJeu) -> bool:
    """Vérifie si la transition d'état est valide"""
    try:
        if not valider_etat_jeu(etat_actuel, regles) or not valider_etat_jeu(nouvel_etat, regles):
            return False
            
        transitions_valides = {
            regles.ETATS_JEU['PRET_A_SERVIR']: [
                regles.ETATS_JEU['SERVICE_COMMENCE']
            ],
            regles.ETATS_JEU['SERVICE_COMMENCE']: [
                regles.ETATS_JEU['ECHANGE'],
                regles.ETATS_JEU['POINT_TERMINE']
            ],
            regles.ETATS_JEU['ECHANGE']: [
                regles.ETATS_JEU['POINT_TERMINE']
            ],
            regles.ETATS_JEU['POINT_TERMINE']: [
                regles.ETATS_JEU['PRET_A_SERVIR'],
                regles.ETATS_JEU['JEU_TERMINE']
            ],
            regles.ETATS_JEU['JEU_TERMINE']: [
                regles.ETATS_JEU['PRET_A_SERVIR'],
                regles.ETATS_JEU['MATCH_TERMINE']
            ]
        }
        
        return nouvel_etat in transitions_valides.get(etat_actuel, [])
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de transition : {e}")
        raise ReglesError(f"Erreur de vérification de transition : {e}")

def verifier_controle_valide(touche: int, regles: ReglesJeu) -> bool:
    """Vérifie si une touche de contrôle est valide"""
    try:
        controles_valides = set()
        # Ajouter tous les contrôles des joueurs
        for controles_joueur in regles.CONTROLES['JOUEUR1'].values():
            controles_valides.add(controles_joueur)
        for controles_joueur in regles.CONTROLES['JOUEUR2'].values():
            controles_valides.add(controles_joueur)
        # Ajouter les contrôles spéciaux
        controles_valides.add(regles.CONTROLES['SERVICE'])
        controles_valides.add(regles.CONTROLES['REINITIALISER'])
        
        return touche in controles_valides
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du contrôle : {e}")
        raise ReglesError(f"Erreur de vérification de contrôle : {e}")

def valider_configuration_couleurs(couleurs: ConfigCouleurs) -> None:
    """Valide la configuration des couleurs"""
    try:
        for nom, couleur in couleurs.items():
            if not isinstance(couleur, tuple) or len(couleur) != 3:
                raise ValidationReglesError(f"Format de couleur invalide pour {nom}")
            if not all(isinstance(c, int) and 0 <= c <= 255 for c in couleur):
                raise ValidationReglesError(
                    f"Valeurs de couleur invalides pour {nom}"
                )
    except Exception as e:
        logger.error(f"Erreur lors de la validation des couleurs : {e}")
        raise ReglesError(f"Erreur de validation des couleurs : {e}")

def valider_configuration_difficulte(config: ConfigDifficulte) -> None:
    """Valide la configuration de la difficulté"""
    try:
        # Valider les couleurs du curseur
        for couleur in [config['CURSEUR_ARRIERE_PLAN'], config['CURSEUR_REMPLISSAGE']]:
            if not isinstance(couleur, tuple) or len(couleur) != 3:
                raise ValidationReglesError("Format de couleur de curseur invalide")
            if not all(isinstance(c, int) and 0 <= c <= 255 for c in couleur):
                raise ValidationReglesError("Valeurs de couleur de curseur invalides")
                
        # Valider les couleurs des niveaux
        if len(config['COULEURS_NIVEAU']) != 4:
            raise ValidationReglesError("Nombre incorrect de couleurs de niveau")
        for couleur in config['COULEURS_NIVEAU']:
            if not isinstance(couleur, tuple) or len(couleur) != 3:
                raise ValidationReglesError("Format de couleur de niveau invalide")
            if not all(isinstance(c, int) and 0 <= c <= 255 for c in couleur):
                raise ValidationReglesError("Valeurs de couleur de niveau invalides")
    except Exception as e:
        logger.error(f"Erreur lors de la validation de la config difficulté : {e}")
        raise ReglesError(f"Erreur de validation de la config difficulté : {e}")