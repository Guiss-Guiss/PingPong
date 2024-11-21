from dataclasses import dataclass
from typing import Tuple, Dict, Optional
import pygame
from regles_tennis_table import ReglesJeu

@dataclass(frozen=True)
class PolicesTableau:
    """Polices utilisées pour l'affichage du tableau"""
    principale: pygame.font.Font
    secondaire: pygame.font.Font

@dataclass(frozen=True)
class ElementsScore:
    """Éléments du score à afficher"""
    score_principal: str
    score_jeux: str
    info_service: Optional[str]
    message_statut: Optional[str]
    message_gagnant: Optional[str]
    message_redemarrage: Optional[str]

@dataclass(frozen=True)
class PositionsAffichage:
    """Positions d'affichage des différents éléments"""
    y_score_principal: int = 30
    y_score_jeux: int = 60
    y_service: int = 90
    y_statut: int = 120
    y_gagnant: int = 200
    y_redemarrage: int = 250

@dataclass(frozen=True)
class TableauScore:
    """État immuable du tableau de score"""
    polices: PolicesTableau
    elements: ElementsScore
    positions: PositionsAffichage
    largeur_ecran: int

def creer_tableau_score(regles: ReglesJeu, largeur_ecran: int) -> TableauScore:
    """Crée un nouveau tableau de score"""
    polices = PolicesTableau(
        principale=pygame.font.Font(None, regles.TAILLE_POLICE_PRINCIPALE),
        secondaire=pygame.font.Font(None, regles.TAILLE_POLICE_SECONDAIRE)
    )
    
    elements = ElementsScore(
        score_principal="0 - 0",
        score_jeux="Jeux : 0 - 0",
        info_service=None,
        message_statut=None,
        message_gagnant=None,
        message_redemarrage=None
    )
    
    return TableauScore(
        polices=polices,
        elements=elements,
        positions=PositionsAffichage(),
        largeur_ecran=largeur_ecran
    )

def mettre_a_jour_tableau(tableau: TableauScore, donnees_jeu: Dict) -> TableauScore:
    """Met à jour le tableau avec les nouvelles données de jeu"""
    # Score principal
    score_principal = f"{donnees_jeu['score_joueur1']} - {donnees_jeu['score_joueur2']}"
    
    # Score des jeux
    score_jeux = f"Jeux : {donnees_jeu['jeux_joueur1']} - {donnees_jeu['jeux_joueur2']}"
    
    # Information sur le service
    info_service = None
    if donnees_jeu.get('serveur_actuel'):
        info_service = f"Joueur {donnees_jeu['serveur_actuel']} au service"
        if donnees_jeu.get('en_service'):
            info_service += " (ESPACE pour servir)"
    
    # Messages de statut
    message_statut = donnees_jeu.get('message_statut')
    message_gagnant = None
    message_redemarrage = None
    
    if donnees_jeu.get('match_termine'):
        message_gagnant = f"Le Joueur {donnees_jeu.get('gagnant')} gagne le match !"
        message_redemarrage = "Appuyez sur R pour recommencer"
    
    nouveaux_elements = ElementsScore(
        score_principal=score_principal,
        score_jeux=score_jeux,
        info_service=info_service,
        message_statut=message_statut,
        message_gagnant=message_gagnant,
        message_redemarrage=message_redemarrage
    )
    
    return TableauScore(
        polices=tableau.polices,
        elements=nouveaux_elements,
        positions=tableau.positions,
        largeur_ecran=tableau.largeur_ecran
    )

def dessiner_element(
    ecran: pygame.Surface,
    texte: str,
    police: pygame.font.Font,
    couleur: Tuple[int, int, int],
    position_y: int,
    largeur_ecran: int
) -> None:
    """Dessine un élément de texte centré à une position Y donnée"""
    surface_texte = police.render(texte, True, couleur)
    rect_texte = surface_texte.get_rect(center=(largeur_ecran // 2, position_y))
    ecran.blit(surface_texte, rect_texte)

def dessiner_tableau(ecran: pygame.Surface, tableau: TableauScore, regles: ReglesJeu) -> None:
    """Dessine le tableau de score complet"""
    # Score principal
    dessiner_element(
        ecran,
        tableau.elements.score_principal,
        tableau.polices.principale,
        regles.COULEURS['BLANC'],
        tableau.positions.y_score_principal,
        tableau.largeur_ecran
    )
    
    # Score des jeux
    dessiner_element(
        ecran,
        tableau.elements.score_jeux,
        tableau.polices.secondaire,
        regles.COULEURS['GRIS'],
        tableau.positions.y_score_jeux,
        tableau.largeur_ecran
    )
    
    # Information sur le service
    if tableau.elements.info_service:
        dessiner_element(
            ecran,
            tableau.elements.info_service,
            tableau.polices.secondaire,
            regles.COULEURS['JAUNE'],
            tableau.positions.y_service,
            tableau.largeur_ecran
        )
    
    # Message de statut
    if tableau.elements.message_statut:
        dessiner_element(
            ecran,
            tableau.elements.message_statut,
            tableau.polices.secondaire,
            regles.COULEURS['BLANC'],
            tableau.positions.y_statut,
            tableau.largeur_ecran
        )
    
    # Message de fin de match
    if tableau.elements.message_gagnant:
        dessiner_element(
            ecran,
            tableau.elements.message_gagnant,
            tableau.polices.principale,
            regles.COULEURS['JAUNE'],
            tableau.positions.y_gagnant,
            tableau.largeur_ecran
        )
        
        if tableau.elements.message_redemarrage:
            dessiner_element(
                ecran,
                tableau.elements.message_redemarrage,
                tableau.polices.secondaire,
                regles.COULEURS['BLANC'],
                tableau.positions.y_redemarrage,
                tableau.largeur_ecran
            )

def dessiner_fin_jeu(ecran: pygame.Surface, tableau: TableauScore,
                    gagnant: int, match_termine: bool = False) -> None:
    """Dessine le message de fin de jeu ou de match"""
    message = (f"Le joueur {gagnant} gagne le match !" if match_termine 
              else f"Le joueur {gagnant} gagne le jeu !")
    
    # Message principal
    dessiner_element(
        ecran,
        message,
        tableau.polices.principale,
        (255, 255, 0),  # Jaune
        tableau.largeur_ecran // 4,
        tableau.largeur_ecran
    )
    
    # Message pour redémarrer
    dessiner_element(
        ecran,
        "Appuyez sur R pour redémarrer",
        tableau.polices.secondaire,
        (255, 255, 255),  # Blanc
        tableau.largeur_ecran // 4 + 40,
        tableau.largeur_ecran
    )