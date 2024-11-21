from dataclasses import dataclass
from typing import Tuple, Optional
import pygame
import logging
from regles_tennis_table import ReglesJeu

# Configuration du logging
logger = logging.getLogger(__name__)

class SelecteurDifficulteError(Exception):
    """Classe de base pour les erreurs du sélecteur de difficulté"""
    pass

class ValidationSelecteurError(SelecteurDifficulteError):
    """Erreur de validation des paramètres du sélecteur"""
    pass

class PositionError(SelecteurDifficulteError):
    """Erreur liée aux positions du sélecteur"""
    pass

@dataclass(frozen=True)
class EtatSelecteur:
    """État immuable du sélecteur de difficulté"""
    position_curseur: Tuple[float, float]  # x, y du curseur
    position_poignee: float  # x de la poignée
    difficulte: int
    poignee_en_deplacement: bool
    dimensions_curseur: Tuple[int, int]  # largeur, hauteur
    dimensions_ecran: Tuple[int, int]

    def __post_init__(self):
        """Validation des données à la création"""
        if not isinstance(self.position_curseur, tuple) or len(self.position_curseur) != 2:
            raise ValidationSelecteurError("Position du curseur invalide")
        if not all(isinstance(p, (int, float)) for p in self.position_curseur):
            raise ValidationSelecteurError("Les coordonnées doivent être numériques")
            
        if not isinstance(self.position_poignee, (int, float)):
            raise ValidationSelecteurError("Position de la poignée invalide")
            
        if not isinstance(self.difficulte, int):
            raise ValidationSelecteurError("La difficulté doit être un entier")
            
        if not isinstance(self.dimensions_curseur, tuple) or len(self.dimensions_curseur) != 2:
            raise ValidationSelecteurError("Dimensions du curseur invalides")
        if not all(isinstance(d, int) and d > 0 for d in self.dimensions_curseur):
            raise ValidationSelecteurError("Les dimensions doivent être des entiers positifs")
            
        if not isinstance(self.dimensions_ecran, tuple) or len(self.dimensions_ecran) != 2:
            raise ValidationSelecteurError("Dimensions de l'écran invalides")
        if not all(isinstance(d, int) and d > 0 for d in self.dimensions_ecran):
            raise ValidationSelecteurError("Les dimensions doivent être des entiers positifs")

def valider_position_dans_ecran(position: Tuple[float, float], dimensions_ecran: Tuple[int, int]) -> None:
    """Valide qu'une position est dans les limites de l'écran"""
    try:
        if not (0 <= position[0] <= dimensions_ecran[0] and 
                0 <= position[1] <= dimensions_ecran[1]):
            raise PositionError("Position hors limites de l'écran")
    except Exception as e:
        logger.error(f"Erreur de validation de position : {e}")
        raise

def creer_selecteur(regles: ReglesJeu, dimensions_ecran: Tuple[int, int]) -> EtatSelecteur:
    """Crée un nouveau sélecteur de difficulté"""
    try:
        if not isinstance(regles, ReglesJeu):
            raise ValidationSelecteurError("Les règles doivent être une instance de ReglesJeu")
        if not isinstance(dimensions_ecran, tuple) or len(dimensions_ecran) != 2:
            raise ValidationSelecteurError("Dimensions de l'écran invalides")
            
        largeur_curseur = regles.LARGEUR_CURSEUR_DIFFICULTE
        hauteur_curseur = regles.HAUTEUR_CURSEUR_DIFFICULTE
        
        # Calculer la position centrale du curseur
        curseur_x = (dimensions_ecran[0] - largeur_curseur) // 2
        curseur_y = dimensions_ecran[1] // 2
        
        # Valider la position
        valider_position_dans_ecran((curseur_x, curseur_y), dimensions_ecran)
        
        etat = EtatSelecteur(
            position_curseur=(curseur_x, curseur_y),
            position_poignee=curseur_x,  # Commence au niveau minimum
            difficulte=regles.DIFFICULTE_MIN,
            poignee_en_deplacement=False,
            dimensions_curseur=(largeur_curseur, hauteur_curseur),
            dimensions_ecran=dimensions_ecran
        )
        
        logger.debug(f"Sélecteur créé avec difficulté initiale {etat.difficulte}")
        return etat
        
    except Exception as e:
        logger.error(f"Erreur lors de la création du sélecteur : {e}")
        raise SelecteurDifficulteError(f"Erreur de création : {e}")

def obtenir_couleur_niveau(regles: ReglesJeu, niveau: int) -> Tuple[int, int, int]:
    """Retourne la couleur correspondant au niveau de difficulté"""
    try:
        if niveau < regles.DIFFICULTE_MIN or niveau > regles.DIFFICULTE_MAX:
            raise ValidationSelecteurError(
                f"Niveau {niveau} hors limites [{regles.DIFFICULTE_MIN}, {regles.DIFFICULTE_MAX}]"
            )
            
        if niveau <= 3:
            return regles.CONFIG_DIFFICULTE['COULEURS_NIVEAU'][0]  # Bleu - Débutant
        elif niveau <= 6:
            return regles.CONFIG_DIFFICULTE['COULEURS_NIVEAU'][1]  # Vert - Intermédiaire
        elif niveau <= 9:
            return regles.CONFIG_DIFFICULTE['COULEURS_NIVEAU'][2]  # Orange - Expert
        return regles.CONFIG_DIFFICULTE['COULEURS_NIVEAU'][3]      # Rouge - Maître
    except Exception as e:
        logger.error(f"Erreur lors de l'obtention de la couleur : {e}")
        raise SelecteurDifficulteError(f"Erreur de couleur : {e}")

def calculer_difficulte(etat: EtatSelecteur, regles: ReglesJeu) -> int:
    """Calcule le niveau de difficulté basé sur la position de la poignée"""
    try:
        if not isinstance(etat, EtatSelecteur):
            raise ValidationSelecteurError("État invalide")
            
        progression = ((etat.position_poignee - etat.position_curseur[0]) / 
                      etat.dimensions_curseur[0])
        
        if not 0 <= progression <= 1:
            raise ValidationSelecteurError("Progression hors limites")
            
        niveau = round(
            regles.DIFFICULTE_MIN + 
            (regles.DIFFICULTE_MAX - regles.DIFFICULTE_MIN) * progression
        )
        
        # Valider le niveau calculé
        if niveau < regles.DIFFICULTE_MIN or niveau > regles.DIFFICULTE_MAX:
            raise ValidationSelecteurError(f"Niveau calculé invalide : {niveau}")
            
        return niveau
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la difficulté : {e}")
        raise SelecteurDifficulteError(f"Erreur de calcul : {e}")

def gerer_evenement(
    etat: EtatSelecteur,
    evenement: pygame.event.Event,
    regles: ReglesJeu
) -> EtatSelecteur:
    """Gère les événements du sélecteur de difficulté"""
    try:
        if evenement.type == pygame.MOUSEBUTTONDOWN:
            return gerer_clic_souris(etat, evenement.pos, regles)
        elif evenement.type == pygame.MOUSEBUTTONUP:
            return arreter_deplacement(etat)
        elif evenement.type == pygame.MOUSEMOTION and etat.poignee_en_deplacement:
            return deplacer_poignee(etat, evenement.pos[0], regles)
        return etat
    except Exception as e:
        logger.error(f"Erreur lors de la gestion d'événement : {e}")
        raise SelecteurDifficulteError(f"Erreur d'événement : {e}")

def gerer_clic_souris(
    etat: EtatSelecteur,
    position: Tuple[int, int],
    regles: ReglesJeu
) -> EtatSelecteur:
    """Gère le clic de souris sur le sélecteur"""
    try:
        x, y = position
        distance = ((x - etat.position_poignee) ** 2 + 
                   (y - (etat.position_curseur[1] + etat.dimensions_curseur[1] // 2)) ** 2) ** 0.5
        
        if distance < regles.RAYON_POIGNEE_DIFFICULTE:
            return EtatSelecteur(
                position_curseur=etat.position_curseur,
                position_poignee=etat.position_poignee,
                difficulte=etat.difficulte,
                poignee_en_deplacement=True,
                dimensions_curseur=etat.dimensions_curseur,
                dimensions_ecran=etat.dimensions_ecran
            )
        return etat
    except Exception as e:
        logger.error(f"Erreur lors de la gestion du clic : {e}")
        raise SelecteurDifficulteError(f"Erreur de clic : {e}")

def arreter_deplacement(etat: EtatSelecteur) -> EtatSelecteur:
    """Arrête le déplacement de la poignée"""
    try:
        return EtatSelecteur(
            position_curseur=etat.position_curseur,
            position_poignee=etat.position_poignee,
            difficulte=etat.difficulte,
            poignee_en_deplacement=False,
            dimensions_curseur=etat.dimensions_curseur,
            dimensions_ecran=etat.dimensions_ecran
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt du déplacement : {e}")
        raise SelecteurDifficulteError(f"Erreur d'arrêt : {e}")

def deplacer_poignee(
    etat: EtatSelecteur,
    nouvelle_position_x: int,
    regles: ReglesJeu
) -> EtatSelecteur:
    """Déplace la poignée à une nouvelle position"""
    try:
        # Limiter la position dans les bornes du curseur
        position_x = max(
            etat.position_curseur[0],
            min(nouvelle_position_x, 
                etat.position_curseur[0] + etat.dimensions_curseur[0])
        )
        
        # Créer un état temporaire pour calculer la nouvelle difficulté
        etat_temp = EtatSelecteur(
            position_curseur=etat.position_curseur,
            position_poignee=position_x,
            difficulte=etat.difficulte,
            poignee_en_deplacement=etat.poignee_en_deplacement,
            dimensions_curseur=etat.dimensions_curseur,
            dimensions_ecran=etat.dimensions_ecran
        )
        
        nouvelle_difficulte = calculer_difficulte(etat_temp, regles)
        
        return EtatSelecteur(
            position_curseur=etat.position_curseur,
            position_poignee=position_x,
            difficulte=nouvelle_difficulte,
            poignee_en_deplacement=etat.poignee_en_deplacement,
            dimensions_curseur=etat.dimensions_curseur,
            dimensions_ecran=etat.dimensions_ecran
        )
    except Exception as e:
        logger.error(f"Erreur lors du déplacement de la poignée : {e}")
        raise SelecteurDifficulteError(f"Erreur de déplacement : {e}")

def dessiner_selecteur(
    ecran: pygame.Surface,
    etat: EtatSelecteur,
    regles: ReglesJeu
) -> None:
    """Dessine le sélecteur de difficulté"""
    try:
        # Dessiner le titre
        police = pygame.font.Font(None, regles.TAILLE_POLICE_PRINCIPALE)
        titre = police.render(
            "Sélectionnez le Niveau de Difficulté",
            True,
            regles.COULEURS['BLANC']
        )
        rect_titre = titre.get_rect(
            center=(etat.dimensions_ecran[0] // 2, etat.position_curseur[1] - 60)
        )
        ecran.blit(titre, rect_titre)

        # Dessiner l'arrière-plan du curseur
        pygame.draw.rect(
            ecran,
            regles.CONFIG_DIFFICULTE['CURSEUR_ARRIERE_PLAN'],
            (
                etat.position_curseur[0],
                etat.position_curseur[1],
                etat.dimensions_curseur[0],
                etat.dimensions_curseur[1]
            )
        )

        # Dessiner la portion remplie du curseur
        largeur_remplie = etat.position_poignee - etat.position_curseur[0]
        pygame.draw.rect(
            ecran,
            obtenir_couleur_niveau(regles, etat.difficulte),
            (
                etat.position_curseur[0],
                etat.position_curseur[1],
                largeur_remplie,
                etat.dimensions_curseur[1]
            )
        )

        # Dessiner les marqueurs de difficulté
        petite_police = pygame.font.Font(None, regles.TAILLE_POLICE_SECONDAIRE)
        for i in range(10):
            x = etat.position_curseur[0] + (i * etat.dimensions_curseur[0] // 9)
            # Marque
            pygame.draw.line(
                ecran,
                regles.COULEURS['BLANC'],
                (x, etat.position_curseur[1] - 5),
                (x, etat.position_curseur[1] + etat.dimensions_curseur[1] + 5),
                2
            )
            # Numéro
            num = petite_police.render(str(i + 1), True, regles.COULEURS['BLANC'])
            rect_num = num.get_rect(center=(x, etat.position_curseur[1] + 20))
            ecran.blit(num, rect_num)

        # Dessiner la poignée
        pygame.draw.circle(
            ecran,
            regles.COULEURS['BLANC'],
            (
                int(etat.position_poignee),
                int(etat.position_curseur[1] + etat.dimensions_curseur[1] // 2)
            ),
            regles.RAYON_POIGNEE_DIFFICULTE
        )

# Dessiner le texte de difficulté actuelle (suite)
        texte_difficulte = (
            f"{regles.obtenir_nom_niveau(etat.difficulte)} "
            f"(Niveau {etat.difficulte})"
        )
        surface_diff = police.render(
            texte_difficulte,
            True,
            obtenir_couleur_niveau(regles, etat.difficulte)
        )
        rect_diff = surface_diff.get_rect(
            center=(etat.dimensions_ecran[0] // 2, etat.position_curseur[1] + 60)
        )
        ecran.blit(surface_diff, rect_diff)

        # Dessiner l'instruction
        instruction = petite_police.render(
            "Appuyez sur ENTRÉE pour commencer la partie",
            True,
            regles.COULEURS['BLANC']
        )
        rect_instruction = instruction.get_rect(
            center=(etat.dimensions_ecran[0] // 2, etat.position_curseur[1] + 120)
        )
        ecran.blit(instruction, rect_instruction)

    except pygame.error as e:
        logger.error(f"Erreur Pygame lors du dessin : {e}")
        raise SelecteurDifficulteError(f"Erreur de rendu Pygame : {e}")
    except Exception as e:
        logger.error(f"Erreur lors du dessin du sélecteur : {e}")
        raise SelecteurDifficulteError(f"Erreur de dessin : {e}")

def valider_limites_curseur(etat: EtatSelecteur) -> None:
    """Valide que le curseur est dans les limites valides"""
    try:
        # Vérifier que la position du curseur est dans l'écran
        if not (0 <= etat.position_curseur[0] <= etat.dimensions_ecran[0] - etat.dimensions_curseur[0] and
                0 <= etat.position_curseur[1] <= etat.dimensions_ecran[1]):
            raise PositionError("Position du curseur hors limites")

        # Vérifier que la poignée est dans les limites du curseur
        if not (etat.position_curseur[0] <= etat.position_poignee <= 
                etat.position_curseur[0] + etat.dimensions_curseur[0]):
            raise PositionError("Position de la poignée hors limites")
            
    except Exception as e:
        logger.error(f"Erreur lors de la validation des limites : {e}")
        raise SelecteurDifficulteError(f"Erreur de validation des limites : {e}")

def obtenir_progression(etat: EtatSelecteur) -> float:
    """Retourne la progression actuelle du curseur (0.0 à 1.0)"""
    try:
        progression = ((etat.position_poignee - etat.position_curseur[0]) / 
                      etat.dimensions_curseur[0])
        
        if not 0 <= progression <= 1:
            raise ValidationSelecteurError("Progression hors limites")
            
        return progression
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la progression : {e}")
        raise SelecteurDifficulteError(f"Erreur de calcul de progression : {e}")

def definir_difficulte(etat: EtatSelecteur, niveau: int, regles: ReglesJeu) -> EtatSelecteur:
    """Crée un nouvel état avec le niveau de difficulté spécifié"""
    try:
        if niveau < regles.DIFFICULTE_MIN or niveau > regles.DIFFICULTE_MAX:
            raise ValidationSelecteurError(
                f"Niveau {niveau} hors limites [{regles.DIFFICULTE_MIN}, {regles.DIFFICULTE_MAX}]"
            )

        # Calculer la nouvelle position de la poignée
        progression = (niveau - regles.DIFFICULTE_MIN) / (regles.DIFFICULTE_MAX - regles.DIFFICULTE_MIN)
        nouvelle_position = (etat.position_curseur[0] + 
                           progression * etat.dimensions_curseur[0])

        return EtatSelecteur(
            position_curseur=etat.position_curseur,
            position_poignee=nouvelle_position,
            difficulte=niveau,
            poignee_en_deplacement=False,
            dimensions_curseur=etat.dimensions_curseur,
            dimensions_ecran=etat.dimensions_ecran
        )
    except Exception as e:
        logger.error(f"Erreur lors de la définition de la difficulté : {e}")
        raise SelecteurDifficulteError(f"Erreur de définition de difficulté : {e}")

def reinitialiser_selecteur(etat: EtatSelecteur, regles: ReglesJeu) -> EtatSelecteur:
    """Réinitialise le sélecteur à son état initial"""
    try:
        return definir_difficulte(etat, regles.DIFFICULTE_MIN, regles)
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation : {e}")
        raise SelecteurDifficulteError(f"Erreur de réinitialisation : {e}")

def est_pret(etat: EtatSelecteur) -> bool:
    """Vérifie si le sélecteur est prêt (poignée non en déplacement)"""
    try:
        return not etat.poignee_en_deplacement
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de l'état : {e}")
        raise SelecteurDifficulteError(f"Erreur de vérification : {e}")