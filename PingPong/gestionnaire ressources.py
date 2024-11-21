from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import os
import pygame
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GestionnaireRessourcesError(Exception):
    """Classe de base pour les erreurs du gestionnaire de ressources"""
    pass

class ChargementSonError(GestionnaireRessourcesError):
    """Erreur lors du chargement des sons"""
    pass

class ChargementImageError(GestionnaireRessourcesError):
    """Erreur lors du chargement des images"""
    pass

class ValidationError(GestionnaireRessourcesError):
    """Erreur de validation des paramètres"""
    pass

# Types personnalisés
Couleur = Tuple[int, int, int]
Dimension = Tuple[int, int]

@dataclass(frozen=True)
class ConfigurationRessources:
    """Configuration pour toutes les ressources"""
    # Configuration des sons
    VOLUME_DEFAUT: float = 0.7
    FORMAT_SONS: str = 'mp3'
    DELAI_ENTRE_SONS: int = 100  # ms
    
    # Configuration des images
    FORMAT_ARRIERE_PLAN: str = 'jpg'
    FORMAT_RAQUETTES: str = 'png'
    ALPHA_RAQUETTES: bool = True
    CONVERSION_ALPHA: bool = True
    
    # Chemins par défaut
    DOSSIER_SONS: str = "sons"
    DOSSIER_IMAGES: str = "images"

    def __post_init__(self):
        """Validation de la configuration"""
        if not 0 <= self.VOLUME_DEFAUT <= 1:
            raise ValidationError("Le volume doit être entre 0 et 1")
        if self.DELAI_ENTRE_SONS < 0:
            raise ValidationError("Le délai entre les sons doit être positif")

@dataclass(frozen=True)
class Sons:
    """Structure immuable pour les sons"""
    coup_gauche: Optional[pygame.mixer.Sound]
    coup_droit: Optional[pygame.mixer.Sound]
    service: Optional[pygame.mixer.Sound]
    volume: float

    def __post_init__(self):
        """Validation des sons"""
        if not 0 <= self.volume <= 1:
            raise ValidationError("Le volume doit être entre 0 et 1")
        for son in [self.coup_gauche, self.coup_droit, self.service]:
            if son is not None and not isinstance(son, pygame.mixer.Sound):
                raise ValidationError("Son invalide")

@dataclass(frozen=True)
class Images:
    """Structure immuable pour les images"""
    arriere_plan: Optional[pygame.Surface]
    raquette_bleue: Optional[pygame.Surface]
    raquette_rouge: Optional[pygame.Surface]
    dimensions_originales: Dict[str, Dimension]

    def __post_init__(self):
        """Validation des images"""
        for image in [self.arriere_plan, self.raquette_bleue, self.raquette_rouge]:
            if image is not None and not isinstance(image, pygame.Surface):
                raise ValidationError("Image invalide")

@dataclass(frozen=True)
class Ressources:
    """Structure immuable regroupant toutes les ressources"""
    sons: Sons
    images: Images
    config: ConfigurationRessources
    ressources_chargees: bool
    son_active: bool
    message_erreur: Optional[str]

    def __post_init__(self):
        """Validation des ressources"""
        if not isinstance(self.config, ConfigurationRessources):
            raise ValidationError("Configuration invalide")
        if not isinstance(self.sons, Sons):
            raise ValidationError("Sons invalides")
        if not isinstance(self.images, Images):
            raise ValidationError("Images invalides")

def creer_gestionnaire_ressources(dossier_base: str = ".") -> Ressources:
    """Crée une nouvelle instance du gestionnaire de ressources"""
    try:
        config = ConfigurationRessources()
        return Ressources(
            sons=Sons(None, None, None, config.VOLUME_DEFAUT),
            images=Images(None, None, None, {}),
            config=config,
            ressources_chargees=False,
            son_active=True,
            message_erreur=None
        )
    except Exception as e:
        logger.error(f"Erreur lors de la création du gestionnaire : {e}")
        raise GestionnaireRessourcesError(f"Erreur d'initialisation : {e}")

def charger_son(chemin: Path) -> Optional[pygame.mixer.Sound]:
    """Charge un son avec gestion des erreurs"""
    try:
        if not chemin.exists():
            logger.warning(f"Fichier son non trouvé : {chemin}")
            return None
            
        son = pygame.mixer.Sound(str(chemin))
        logger.debug(f"Son chargé avec succès : {chemin}")
        return son
    except pygame.error as e:
        logger.error(f"Erreur Pygame lors du chargement du son {chemin}: {e}")
        raise ChargementSonError(f"Erreur de chargement du son : {e}")
    except Exception as e:
        logger.error(f"Erreur inattendue lors du chargement du son {chemin}: {e}")
        raise ChargementSonError(f"Erreur inattendue : {e}")

def charger_image(
    chemin: Path,
    conversion_alpha: bool = False,
    dimensions_cible: Optional[Dimension] = None
) -> Optional[pygame.Surface]:
    """Charge une image avec gestion des erreurs"""
    try:
        if not chemin.exists():
            logger.warning(f"Fichier image non trouvé : {chemin}")
            return None
            
        image = pygame.image.load(str(chemin))
        if conversion_alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
            
        if dimensions_cible:
            image = pygame.transform.scale(image, dimensions_cible)
            
        logger.debug(f"Image chargée avec succès : {chemin}")
        return image
    except pygame.error as e:
        logger.error(f"Erreur Pygame lors du chargement de l'image {chemin}: {e}")
        raise ChargementImageError(f"Erreur de chargement de l'image : {e}")
    except Exception as e:
        logger.error(f"Erreur inattendue lors du chargement de l'image {chemin}: {e}")
        raise ChargementImageError(f"Erreur inattendue : {e}")

def charger_toutes_ressources(
    ressources: Ressources,
    dimensions_fenetre: Dimension,
    dimensions_raquette: Dimension
) -> Ressources:
    """Charge toutes les ressources du jeu"""
    try:
        # Valider les dimensions
        if any(d <= 0 for d in dimensions_fenetre + dimensions_raquette):
            raise ValidationError("Les dimensions doivent être positives")

        # Charger les sons
        ressources = charger_sons(ressources, Path("assets"))
        if not ressources.ressources_chargees:
            return ressources

        # Charger les images
        ressources = charger_images(
            ressources,
            Path("assets"),
            dimensions_fenetre,
            dimensions_raquette
        )

        return ressources
    except Exception as e:
        logger.error(f"Erreur lors du chargement des ressources : {e}")
        return Ressources(
            sons=ressources.sons,
            images=ressources.images,
            config=ressources.config,
            ressources_chargees=False,
            son_active=False,
            message_erreur=str(e)
        )

def jouer_son(ressources: Ressources, type_son: str, force_volume: Optional[float] = None) -> None:
    """Joue un son spécifique si disponible et activé"""
    try:
        if not ressources.son_active:
            return

        if type_son not in ['coup_gauche', 'coup_droit', 'service']:
            raise ValidationError(f"Type de son invalide : {type_son}")

        son = getattr(ressources.sons, type_son, None)
        if son:
            volume = force_volume if force_volume is not None else ressources.sons.volume
            if not 0 <= volume <= 1:
                raise ValidationError("Volume invalide")
            son.set_volume(volume)
            son.play()
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du son : {e}")
        raise GestionnaireRessourcesError(f"Erreur de lecture du son : {e}")

def modifier_volume(ressources: Ressources, nouveau_volume: float) -> Ressources:
    """Retourne de nouvelles ressources avec le volume modifié"""
    try:
        if not 0 <= nouveau_volume <= 1:
            raise ValidationError("Le volume doit être entre 0 et 1")
        
        # Créer de nouveaux sons avec le nouveau volume
        nouveaux_sons = Sons(
            coup_gauche=ressources.sons.coup_gauche,
            coup_droit=ressources.sons.coup_droit,
            service=ressources.sons.service,
            volume=nouveau_volume
        )
        
        # Appliquer le nouveau volume aux sons existants
        for son in [nouveaux_sons.coup_gauche, nouveaux_sons.coup_droit, nouveaux_sons.service]:
            if son:
                son.set_volume(nouveau_volume)
        
        return Ressources(
            sons=nouveaux_sons,
            images=ressources.images,
            config=ressources.config,
            ressources_chargees=ressources.ressources_chargees,
            son_active=ressources.son_active,
            message_erreur=ressources.message_erreur
        )
    except Exception as e:
        logger.error(f"Erreur lors de la modification du volume : {e}")
        raise GestionnaireRessourcesError(f"Erreur de modification du volume : {e}")

def basculer_son(ressources: Ressources) -> Ressources:
    """Retourne de nouvelles ressources avec le son activé/désactivé"""
    try:
        return Ressources(
            sons=ressources.sons,
            images=ressources.images,
            config=ressources.config,
            ressources_chargees=ressources.ressources_chargees,
            son_active=not ressources.son_active,
            message_erreur=ressources.message_erreur
        )
    except Exception as e:
        logger.error(f"Erreur lors du basculement du son : {e}")
        raise GestionnaireRessourcesError(f"Erreur de basculement du son : {e}")

def nettoyer_ressources(ressources: Ressources) -> None:
    """Nettoie les ressources"""
    try:
        # Pygame gère automatiquement la libération des ressources
        logger.info("Nettoyage des ressources terminé")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des ressources : {e}")
        raise GestionnaireRessourcesError(f"Erreur de nettoyage : {e}")