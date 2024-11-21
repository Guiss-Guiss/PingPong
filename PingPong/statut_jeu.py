from dataclasses import dataclass
from typing import Optional, Dict, Tuple
import pygame
from regles_tennis_table import ReglesJeu

@dataclass(frozen=True)
class EtatStatut:
    """État immuable du statut de jeu"""
    statut_jeu: str
    statut_match: str
    message_alerte: str
    minuteur_alerte: int
    en_pause: bool
    police_principale: pygame.font.Font
    police_alerte: pygame.font.Font

def creer_statut(regles: ReglesJeu) -> EtatStatut:
    """Crée un nouvel état de statut"""
    return EtatStatut(
        statut_jeu="Préparez-vous !",
        statut_match="",
        message_alerte="",
        minuteur_alerte=0,
        en_pause=False,
        police_principale=pygame.font.Font(None, regles.TAILLE_POLICE_STANDARD),
        police_alerte=pygame.font.Font(None, regles.TAILLE_POLICE_ALERTE)
    )

def mettre_a_jour_statut(statut: EtatStatut, etat_jeu: Dict) -> EtatStatut:
    """Retourne un nouveau statut basé sur l'état du jeu"""
    nouveau_statut_jeu = statut.statut_jeu
    
    if etat_jeu.get('service', False):
        nouveau_statut_jeu = f"Joueur {etat_jeu['serveur']} au service"
    elif etat_jeu.get('point_marque'):
        return creer_alerte(statut, f"Point pour le Joueur {etat_jeu['gagnant_point']} !")
    elif etat_jeu.get('jeu_termine'):
        nouveau_statut_jeu = f"Joueur {etat_jeu['gagnant']} gagne le jeu !"
    elif etat_jeu.get('let_service'):
        return creer_alerte(statut, "Let Service !")
        
    return EtatStatut(
        statut_jeu=nouveau_statut_jeu,
        statut_match=statut.statut_match,
        message_alerte=statut.message_alerte,
        minuteur_alerte=statut.minuteur_alerte,
        en_pause=statut.en_pause,
        police_principale=statut.police_principale,
        police_alerte=statut.police_alerte
    )

def mettre_a_jour_match(statut: EtatStatut, etat_match: Dict) -> EtatStatut:
    """Retourne un nouveau statut avec les informations du match mises à jour"""
    nouveau_statut_match = ""
    
    if etat_match.get('match_termine'):
        nouveau_statut_match = f"Joueur {etat_match['gagnant']} gagne le match !"
    else:
        jeux = etat_match.get('jeux', (0, 0))
        nouveau_statut_match = f"Jeux : {jeux[0]} - {jeux[1]}"
    
    return EtatStatut(
        statut_jeu=statut.statut_jeu,
        statut_match=nouveau_statut_match,
        message_alerte=statut.message_alerte,
        minuteur_alerte=statut.minuteur_alerte,
        en_pause=statut.en_pause,
        police_principale=statut.police_principale,
        police_alerte=statut.police_alerte
    )

def creer_alerte(statut: EtatStatut, message: str) -> EtatStatut:
    """Retourne un nouveau statut avec une alerte"""
    return EtatStatut(
        statut_jeu=statut.statut_jeu,
        statut_match=statut.statut_match,
        message_alerte=message,
        minuteur_alerte=pygame.time.get_ticks(),
        en_pause=statut.en_pause,
        police_principale=statut.police_principale,
        police_alerte=statut.police_alerte
    )

def dessiner_statut(ecran: pygame.Surface, statut: EtatStatut, regles: ReglesJeu) -> None:
    """Dessine tous les éléments de statut à l'écran"""
    # Dessiner le statut du jeu
    if statut.statut_jeu:
        texte = statut.police_principale.render(statut.statut_jeu, True, regles.COULEURS['BLANC'])
        rect_texte = texte.get_rect(center=(regles.LARGEUR_FENETRE // 2, 30))
        ecran.blit(texte, rect_texte)
    
    # Dessiner le statut du match
    if statut.statut_match:
        texte = statut.police_principale.render(statut.statut_match, True, regles.COULEURS['BLANC'])
        rect_texte = texte.get_rect(center=(regles.LARGEUR_FENETRE // 2, 60))
        ecran.blit(texte, rect_texte)
    
    # Dessiner le message d'alerte si actif
    temps_actuel = pygame.time.get_ticks()
    if (statut.message_alerte and 
        temps_actuel - statut.minuteur_alerte < regles.DUREE_ALERTE):
        texte = statut.police_alerte.render(statut.message_alerte, True, regles.COULEURS['JAUNE'])
        rect_texte = texte.get_rect(center=(regles.LARGEUR_FENETRE // 2, 100))
        ecran.blit(texte, rect_texte)

def dessiner_controles(ecran: pygame.Surface, statut: EtatStatut, regles: ReglesJeu) -> None:
    """Dessine les informations de contrôle du jeu"""
    controles = [
        "Contrôles :",
        f"Joueur 1 : {pygame.key.name(regles.CONTROLES['JOUEUR1']['HAUT'])}/"
        f"{pygame.key.name(regles.CONTROLES['JOUEUR1']['BAS'])} pour bouger",
        f"Joueur 2 : {pygame.key.name(regles.CONTROLES['JOUEUR2']['HAUT'])}/"
        f"{pygame.key.name(regles.CONTROLES['JOUEUR2']['BAS'])} pour bouger",
        f"Appuyez sur {pygame.key.name(regles.CONTROLES['SERVICE'])} pour servir",
        f"Appuyez sur {pygame.key.name(regles.CONTROLES['REINITIALISER'])} pour redémarrer"
    ]
    
    position_y = 150
    for ligne in controles:
        texte = statut.police_principale.render(ligne, True, regles.COULEURS['BLANC'])
        rect_texte = texte.get_rect(center=(regles.LARGEUR_FENETRE // 2, position_y))
        ecran.blit(texte, rect_texte)
        position_y += 30

def dessiner_menu_pause(ecran: pygame.Surface, statut: EtatStatut, regles: ReglesJeu) -> None:
    """Dessine le menu de pause"""
    # Créer l'overlay semi-transparent
    overlay = pygame.Surface((regles.LARGEUR_FENETRE, ecran.get_height()))
    overlay.fill(regles.COULEURS['NOIR'])
    overlay.set_alpha(128)
    ecran.blit(overlay, (0, 0))
    
    messages = [
        ("JEU EN PAUSE", statut.police_alerte, regles.COULEURS['JAUNE']),
        ("Appuyez sur P pour reprendre", statut.police_principale, regles.COULEURS['BLANC']),
        (f"Appuyez sur {pygame.key.name(regles.CONTROLES['REINITIALISER'])} pour redémarrer",
         statut.police_principale, regles.COULEURS['BLANC']),
        ("Appuyez sur ESC pour quitter", statut.police_principale, regles.COULEURS['BLANC'])
    ]
    
    position_y = ecran.get_height() // 3
    for message, police, couleur in messages:
        texte = police.render(message, True, couleur)
        rect_texte = texte.get_rect(center=(regles.LARGEUR_FENETRE // 2, position_y))
        ecran.blit(texte, rect_texte)
        position_y += 50

def basculer_pause(statut: EtatStatut) -> EtatStatut:
    """Retourne un nouveau statut avec l'état de pause inversé"""
    return EtatStatut(
        statut_jeu=statut.statut_jeu,
        statut_match=statut.statut_match,
        message_alerte=statut.message_alerte,
        minuteur_alerte=statut.minuteur_alerte,
        en_pause=not statut.en_pause,
        police_principale=statut.police_principale,
        police_alerte=statut.police_alerte
    )