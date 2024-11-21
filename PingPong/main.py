import pygame
import sys
import logging
from dataclasses import dataclass
from typing import Optional, Tuple, Dict
from pathlib import Path

# Imports des modules du jeu
from regles_tennis_table import ReglesTennisTable
from gestionnaire_ressources import (
    Ressources, creer_gestionnaire_ressources, 
    charger_toutes_ressources, GestionnaireRessourcesError
)
from balle import (
    Balle, creer_balle, deplacer_balle, servir, 
    gerer_collision_raquette, BalleError
)
from raquette import (
    Raquette, creer_raquette, deplacer_raquette,
    definir_velocite, verifier_collision_balle
)
from score import (
    EtatScore, creer_score_initial, incrementer_score,
    commencer_nouveau_jeu, ScoreError
)
from gestionnaire_match import (
    EtatMatch, creer_match, mettre_a_jour_match,
    GestionnaireMatchError
)
from gestionnaire_service import (
    EtatService, creer_etat_service, 
    mettre_a_jour_service, commencer_service,
    gerer_service
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tennis_table.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JeuError(Exception):
    """Classe de base pour les erreurs du jeu"""
    pass

class InitialisationJeuError(JeuError):
    """Erreur lors de l'initialisation du jeu"""
    pass

class MiseAJourJeuError(JeuError):
    """Erreur lors de la mise à jour du jeu"""
    pass

@dataclass(frozen=True)
class EtatJeu:
    """État global du jeu"""
    regles: ReglesTennisTable
    ressources: Ressources
    balle: Balle
    raquette_gauche: Raquette
    raquette_droite: Raquette
    score: EtatScore
    match: EtatMatch
    service: EtatService
    en_pause: bool

    def __post_init__(self):
        """Validation des données à la création"""
        if not isinstance(self.regles, ReglesTennisTable):
            raise InitialisationJeuError("Les règles doivent être une instance de ReglesTennisTable")
        if not isinstance(self.ressources, Ressources):
            raise InitialisationJeuError("Les ressources doivent être une instance de Ressources")
        if not isinstance(self.balle, Balle):
            raise InitialisationJeuError("La balle doit être une instance de Balle")
        if not isinstance(self.score, EtatScore):
            raise InitialisationJeuError("Le score doit être une instance de EtatScore")

def initialiser_jeu() -> Optional[EtatJeu]:
    """Initialise le jeu et charge les ressources"""
    try:
        logger.info("Initialisation du jeu...")
        
        # Initialiser Pygame
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Créer les règles
        regles = ReglesTennisTable()
        logger.debug("Règles créées")
        
        # Charger les ressources
        ressources = creer_gestionnaire_ressources()
        dimensions_fenetre = (regles.LARGEUR_FENETRE, regles.HAUTEUR_FENETRE)
        dimensions_raquette = (regles.LARGEUR_RAQUETTE, regles.HAUTEUR_RAQUETTE)
        ressources = charger_toutes_ressources(
            ressources,
            dimensions_fenetre,
            dimensions_raquette
        )
        
        if not ressources.ressources_chargees:
            raise InitialisationJeuError(
                f"Erreur chargement ressources : {ressources.message_erreur}"
            )
        
        logger.debug("Ressources chargées")
        
        return EtatJeu(
            regles=regles,
            ressources=ressources,
            balle=creer_balle(regles),
            raquette_gauche=creer_raquette(
                x=50, 
                y=regles.HAUTEUR_FENETRE // 2,
                vitesse=regles.VITESSE_RAQUETTE,
                image=ressources.images.raquette_rouge
            ),
            raquette_droite=creer_raquette(
                x=regles.LARGEUR_FENETRE - 50,
                y=regles.HAUTEUR_FENETRE // 2,
                vitesse=regles.VITESSE_RAQUETTE,
                image=ressources.images.raquette_bleue
            ),
            score=creer_score_initial(regles),
            match=creer_match(regles),
            service=creer_etat_service(),
            en_pause=False
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation : {str(e)}", exc_info=True)
        return None

def mettre_a_jour_jeu(etat: EtatJeu, touches: Dict[int, bool], delta_temps: float) -> EtatJeu:
    """Met à jour l'état du jeu pour une frame"""
    try:
        if etat.en_pause:
            return etat

        # Mettre à jour les raquettes
        nouvelle_raquette_gauche = mettre_a_jour_raquette(
            etat.raquette_gauche,
            touches,
            delta_temps,
            True
        )
        nouvelle_raquette_droite = mettre_a_jour_raquette(
            etat.raquette_droite,
            touches,
            delta_temps,
            False
        )

        # Mettre à jour la balle
        nouvelle_balle, point_marque = deplacer_balle(etat.balle, etat.regles)
        
        # Gérer les collisions avec les raquettes
        nouvelle_balle = gerer_collisions(
            nouvelle_balle,
            nouvelle_raquette_gauche,
            nouvelle_raquette_droite,
            etat.regles
        )
        
        if point_marque:
            # Déterminer le gagnant du point
            gagnant = 1 if nouvelle_balle.position[0] > etat.regles.LARGEUR_FENETRE else 2
            
            # Mettre à jour le score
            nouveau_score = incrementer_score(etat.score, gagnant, etat.regles)
            nouveau_service = mettre_a_jour_service(
                etat.service,
                nouveau_score.score_actuel,
                etat.regles
            )
            
            # Mettre à jour l'état du match
            nouveau_match = mettre_a_jour_match(
                etat.match,
                nouveau_score.jeux_gagnes,
                etat.regles
            )
        else:
            nouveau_score = etat.score
            nouveau_service = etat.service
            nouveau_match = etat.match

        return EtatJeu(
            regles=etat.regles,
            ressources=etat.ressources,
            balle=nouvelle_balle,
            raquette_gauche=nouvelle_raquette_gauche,
            raquette_droite=nouvelle_raquette_droite,
            score=nouveau_score,
            match=nouveau_match,
            service=nouveau_service,
            en_pause=etat.en_pause
        )
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du jeu : {str(e)}", exc_info=True)
        raise MiseAJourJeuError(f"Erreur de mise à jour : {str(e)}")

def mettre_a_jour_raquette(
    raquette: Raquette,
    touches: Dict[int, bool],
    delta_temps: float,
    est_gauche: bool
) -> Raquette:
    """Met à jour l'état d'une raquette"""
    try:
        # Définir les touches pour chaque raquette
        if est_gauche:
            haut = pygame.K_w
            bas = pygame.K_s
        else:
            haut = pygame.K_UP
            bas = pygame.K_DOWN

        # Calculer la vélocité
        dy = 0
        if touches[haut]:
            dy = -1
        if touches[bas]:
            dy = 1

        # Mettre à jour la raquette
        raquette = definir_velocite(raquette, 0, dy)
        return deplacer_raquette(raquette, delta_temps)
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la raquette : {str(e)}")
        raise

def gerer_collisions(
    balle: Balle,
    raquette_gauche: Raquette,
    raquette_droite: Raquette,
    regles: ReglesTennisTable
) -> Balle:
    """Gère les collisions de la balle avec les raquettes"""
    try:
        temps_actuel = pygame.time.get_ticks()
        
        # Vérifier collision avec raquette gauche
        raquette_gauche, (collision_gauche, position_impact) = verifier_collision_balle(
            raquette_gauche,
            balle,
            temps_actuel
        )
        
        # Vérifier collision avec raquette droite
        raquette_droite, (collision_droite, position_impact) = verifier_collision_balle(
            raquette_droite,
            balle,
            temps_actuel
        )
        
        # Gérer la collision si elle existe
        if collision_gauche and position_impact is not None:
            return gerer_collision_raquette(balle, raquette_gauche, position_impact, regles)
        elif collision_droite and position_impact is not None:
            return gerer_collision_raquette(balle, raquette_droite, position_impact, regles)
            
        return balle
    except Exception as e:
        logger.error(f"Erreur lors de la gestion des collisions : {str(e)}")
        raise

def gerer_evenement(etat: EtatJeu, evenement: pygame.event.Event) -> EtatJeu:
    """Gère un événement et retourne le nouvel état du jeu"""
    try:
        if evenement.type == pygame.KEYDOWN:
            return gerer_touche(etat, evenement.key)
        return etat
    except Exception as e:
        logger.error(f"Erreur lors de la gestion d'événement : {str(e)}")
        raise JeuError(f"Erreur d'événement : {str(e)}")

def gerer_touche(etat: EtatJeu, touche: int) -> EtatJeu:
    """Gère l'appui d'une touche et retourne le nouvel état"""
    try:
        # Touche Echap ou P pour mettre en pause
        if touche in (pygame.K_ESCAPE, pygame.K_p):
            return EtatJeu(
                regles=etat.regles,
                ressources=etat.ressources,
                balle=etat.balle,
                raquette_gauche=etat.raquette_gauche,
                raquette_droite=etat.raquette_droite,
                score=etat.score,
                match=etat.match,
                service=etat.service,
                en_pause=not etat.en_pause
            )
        
        # Touche R pour réinitialiser
        if (touche == etat.regles.CONTROLES['REINITIALISER'] and 
            (etat.score.gagnant_jeu or etat.match.match_termine)):
            return reinitialiser_jeu(etat)
        
        # Touche Espace pour servir
        if (touche == etat.regles.CONTROLES['SERVICE'] and 
            etat.balle.au_service):
            if etat.ressources.sons.service:
                etat.ressources.sons.service.play()
            return servir_balle(etat)
        
        return etat
    except Exception as e:
        logger.error(f"Erreur lors de la gestion de touche : {str(e)}")
        raise JeuError(f"Erreur de touche : {str(e)}")

def servir_balle(etat: EtatJeu) -> EtatJeu:
    """Effectue le service et retourne le nouvel état"""
    try:
        nouvelle_balle = servir(etat.balle, etat.regles, etat.service.serveur_actuel)
        nouveau_service = commencer_service(etat.service)
        
        return EtatJeu(
            regles=etat.regles,
            ressources=etat.ressources,
            balle=nouvelle_balle,
            raquette_gauche=etat.raquette_gauche,
            raquette_droite=etat.raquette_droite,
            score=etat.score,
            match=etat.match,
            service=nouveau_service,
            en_pause=etat.en_pause
        )
    except Exception as e:
        logger.error(f"Erreur lors du service : {str(e)}")
        raise JeuError(f"Erreur de service : {str(e)}")

def reinitialiser_jeu(etat: EtatJeu) -> EtatJeu:
    """Réinitialise l'état du jeu pour une nouvelle partie"""
    try:
        return EtatJeu(
            regles=etat.regles,
            ressources=etat.ressources,
            balle=creer_balle(etat.regles),
            raquette_gauche=creer_raquette(
                x=50,
                y=etat.regles.HAUTEUR_FENETRE // 2,
                vitesse=etat.regles.VITESSE_RAQUETTE,
                image=etat.ressources.images.raquette_rouge
            ),
            raquette_droite=creer_raquette(
                x=etat.regles.LARGEUR_FENETRE - 50,
                y=etat.regles.HAUTEUR_FENETRE // 2,
                vitesse=etat.regles.VITESSE_RAQUETTE,
                image=etat.ressources.images.raquette_bleue
            ),
            score=creer_score_initial(etat.regles),
            match=creer_match(etat.regles),
            service=creer_etat_service(),
            en_pause=False
        )
    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation : {str(e)}")
        raise JeuError(f"Erreur de réinitialisation : {str(e)}")
    
def boucle_principale() -> None:
    """Boucle principale du jeu"""
    try:
        logger.info("Démarrage de la boucle principale")
        etat = initialiser_jeu()
        if etat is None:
            raise InitialisationJeuError("Échec de l'initialisation du jeu")

        # Créer la fenêtre
        ecran = pygame.display.set_mode((
            etat.regles.LARGEUR_FENETRE,
            etat.regles.HAUTEUR_FENETRE
        ))
        pygame.display.set_caption(etat.regles.TITRE_FENETRE)
        horloge = pygame.time.Clock()

        while True:
            try:
                # Gestion des événements
                for evenement in pygame.event.get():
                    if evenement.type == pygame.QUIT:
                        logger.info("Fermeture demandée par l'utilisateur")
                        raise SystemExit
                    
                    etat = gerer_evenement(etat, evenement)

                # Mise à jour de l'état si le jeu n'est pas en pause
                if not etat.en_pause:
                    touches = pygame.key.get_pressed()
                    delta_temps = horloge.get_time() / 1000.0
                    etat = mettre_a_jour_jeu(etat, touches, delta_temps)

                # Rendu
                dessiner_jeu(ecran, etat)
                pygame.display.flip()
                horloge.tick(etat.regles.IPS)

            except MiseAJourJeuError as e:
                logger.error(f"Erreur de mise à jour : {e}", exc_info=True)
                # Continuer la boucle malgré l'erreur de mise à jour
                continue
            except Exception as e:
                logger.error(f"Erreur inattendue dans la boucle : {e}", exc_info=True)
                # Continuer la boucle malgré l'erreur
                continue

    except SystemExit:
        logger.info("Fermeture normale du jeu")
    except Exception as e:
        logger.critical(f"Erreur critique : {e}", exc_info=True)
    finally:
        try:
            # Nettoyage des ressources
            pygame.quit()
            logger.info("Nettoyage effectué avec succès")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage : {e}", exc_info=True)
        sys.exit()

def dessiner_jeu(ecran: pygame.Surface, etat: EtatJeu) -> None:
    """Dessine l'état actuel du jeu"""
    try:
        # Dessiner l'arrière-plan
        if etat.ressources.images.arriere_plan:
            ecran.blit(etat.ressources.images.arriere_plan, (0, 0))
        else:
            ecran.fill(etat.regles.COULEURS['NOIR'])

        # Dessiner la table
        dessiner_table(ecran, etat.regles)
        
        # Dessiner les raquettes
        dessiner_raquettes(ecran, etat)
        
        # Dessiner la balle
        dessiner_balle(ecran, etat.balle)
        
        # Dessiner l'interface
        dessiner_interface(ecran, etat)
        
        # Dessiner le menu pause si nécessaire
        if etat.en_pause:
            dessiner_menu_pause(ecran, etat)

    except Exception as e:
        logger.error(f"Erreur lors du rendu : {e}", exc_info=True)
        raise JeuError(f"Erreur de rendu : {e}")

def dessiner_table(ecran: pygame.Surface, regles: ReglesTennisTable) -> None:
    """Dessine la table de tennis de table"""
    try:
        dimensions = regles.obtenir_dimensions_table()
        
        # Rectangle principal
        pygame.draw.rect(
            ecran,
            regles.COULEURS['VERT'],
            (
                dimensions['x'],
                dimensions['y'],
                dimensions['largeur'],
                dimensions['hauteur']
            )
        )

        # Bordures
        lignes = [
            ((dimensions['x'], dimensions['y']),
             (dimensions['x'] + dimensions['largeur'], dimensions['y'])),
            ((dimensions['x'], dimensions['y'] + dimensions['hauteur']),
             (dimensions['x'] + dimensions['largeur'], 
              dimensions['y'] + dimensions['hauteur'])),
            ((dimensions['x'], dimensions['y']),
             (dimensions['x'], dimensions['y'] + dimensions['hauteur'])),
            ((dimensions['x'] + dimensions['largeur'], dimensions['y']),
             (dimensions['x'] + dimensions['largeur'], 
              dimensions['y'] + dimensions['hauteur']))
        ]
        
        for debut, fin in lignes:
            pygame.draw.line(ecran, regles.COULEURS['BLANC'], debut, fin, 2)

        # Filet
        centre_x = dimensions['x'] + dimensions['largeur'] / 2
        pygame.draw.line(
            ecran,
            regles.COULEURS['BLANC'],
            (centre_x, dimensions['y']),
            (centre_x, dimensions['y'] + dimensions['hauteur']),
            2
        )
    except Exception as e:
        logger.error(f"Erreur lors du dessin de la table : {e}", exc_info=True)
        raise JeuError(f"Erreur de dessin de la table : {e}")

def dessiner_raquettes(ecran: pygame.Surface, etat: EtatJeu) -> None:
    """Dessine les raquettes"""
    try:
        dessiner_raquette(ecran, etat.raquette_gauche)
        dessiner_raquette(ecran, etat.raquette_droite)
    except Exception as e:
        logger.error(f"Erreur lors du dessin des raquettes : {e}", exc_info=True)
        raise JeuError(f"Erreur de dessin des raquettes : {e}")

def dessiner_interface(ecran: pygame.Surface, etat: EtatJeu) -> None:
    """Dessine l'interface utilisateur"""
    try:
        police_score = pygame.font.Font(None, etat.regles.TAILLE_POLICE_PRINCIPALE)
        police_info = pygame.font.Font(None, etat.regles.TAILLE_POLICE_SECONDAIRE)

        # Score
        score_actuel, score_match = obtenir_affichage_score(etat.score)
        surface_score = police_score.render(
            score_actuel,
            True,
            etat.regles.COULEURS['BLANC']
        )
        rect_score = surface_score.get_rect(
            midtop=(etat.regles.LARGEUR_FENETRE // 2, 20)
        )
        ecran.blit(surface_score, rect_score)

        # Score des jeux
        surface_match = police_info.render(
            score_match,
            True,
            etat.regles.COULEURS['GRIS']
        )
        rect_match = surface_match.get_rect(
            midtop=(etat.regles.LARGEUR_FENETRE // 2, 70)
        )
        ecran.blit(surface_match, rect_match)

        # Information sur le service
        if etat.balle.au_service:
            texte_service = f"Joueur {etat.service.serveur_actuel} au service"
            if not etat.match.match_termine:
                texte_service += " (ESPACE pour servir)"
            surface_service = police_info.render(
                texte_service,
                True,
                etat.regles.COULEURS['JAUNE']
            )
            rect_service = surface_service.get_rect(
                midtop=(etat.regles.LARGEUR_FENETRE // 2, 120)
            )
            ecran.blit(surface_service, rect_service)

    except Exception as e:
        logger.error(f"Erreur lors du dessin de l'interface : {e}", exc_info=True)
        raise JeuError(f"Erreur de dessin de l'interface : {e}")

def dessiner_menu_pause(ecran: pygame.Surface, etat: EtatJeu) -> None:
    """Dessine le menu de pause"""
    try:
        # Overlay semi-transparent
        overlay = pygame.Surface((
            etat.regles.LARGEUR_FENETRE,
            etat.regles.HAUTEUR_FENETRE
        ))
        overlay.fill(etat.regles.COULEURS['NOIR'])
        overlay.set_alpha(128)
        ecran.blit(overlay, (0, 0))

        # Polices
        police_titre = pygame.font.Font(None, etat.regles.TAILLE_POLICE_PRINCIPALE)
        police_texte = pygame.font.Font(None, etat.regles.TAILLE_POLICE_SECONDAIRE)

        messages = [
            ("JEU EN PAUSE", police_titre, etat.regles.COULEURS['JAUNE']),
            ("Appuyez sur P pour reprendre", police_texte, etat.regles.COULEURS['BLANC']),
            ("Appuyez sur R pour redémarrer", police_texte, etat.regles.COULEURS['BLANC']),
            ("Appuyez sur ÉCHAP pour quitter", police_texte, etat.regles.COULEURS['BLANC'])
        ]

        for i, (message, police, couleur) in enumerate(messages):
            surface = police.render(message, True, couleur)
            rect = surface.get_rect(
                center=(
                    etat.regles.LARGEUR_FENETRE // 2,
                    etat.regles.HAUTEUR_FENETRE // 3 + i * 50
                )
            )
            ecran.blit(surface, rect)

    except Exception as e:
        logger.error(f"Erreur lors du dessin du menu pause : {e}", exc_info=True)
        raise JeuError(f"Erreur de dessin du menu pause : {e}")

if __name__ == "__main__":
    boucle_principale()